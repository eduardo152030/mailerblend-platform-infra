#!/usr/bin/env python3
"""Prepare a private candidate from a real baseline. Never deploys, reloads or sends alerts."""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('inventory_generator',ROOT/'scripts/gen-prom-targets.py')
generator=importlib.util.module_from_spec(spec);spec.loader.exec_module(generator)


def checksum(body):return hashlib.sha256(body.encode()).hexdigest()


def eligible(state,root=ROOT):
    return generator.validated_cpu_cts(state,root)


def build(baseline,state,services,root=ROOT):
    ids=eligible(state,root)
    inventory={int(s['vmid']):s for s in services}
    assert ids<=inventory.keys() and len(inventory)==17
    remaining=state['remaining_order']
    assert len(remaining)==len(set(remaining)) and not ids.intersection(remaining) and ids|set(remaining)==inventory.keys(), 'Migration registry must cover all 17 exactly'
    files=copy.deepcopy(baseline['files'])
    for path in files:assert not Path(path).is_absolute() and '..' not in Path(path).parts
    config=yaml.safe_load(files['prometheus.yml'])
    node=next(x for x in config['scrape_configs'] if x['job_name']=='node')
    cad=next(x for x in config['scrape_configs'] if x['job_name']=='cadvisor')
    for job,filename in [(node,'node-exporter.json'),(cad,'cadvisor.json')]:
        assert job['file_sd_configs']==[{'files':['/etc/prometheus/targets/'+filename]}], 'Review nonstandard discovery before merging'
        key='targets/'+filename;rows=json.loads(files[key]);seen=set()
        for row in rows:
            assert len(row['targets'])==1
            addr=row['targets'][0];assert addr not in seen,'Duplicate target'
            seen.add(addr)
        port=9100 if filename.startswith('node') else 8085
        for ct in sorted(ids):
            s=inventory[ct];addr=s['ip']+':'+str(port)
            found=[r for r in rows if r['targets']==[addr]]
            if found:r=found[0];assert r['labels']['service']==s['name']
            else:
                r={'targets':[addr],'labels':{'job':'node_exporter' if port==9100 else 'cadvisor','source':'inventory','service':s['name']}};rows.append(r)
            if port==9100:r['labels'].update(cpu_contract='lxc_cgroup_v1',vmid=str(ct))
        # No pending target, label or endpoint is removed or changed.
        for old in json.loads(files[key]):
            ct=next((i for i,s in inventory.items() if old['targets']==[s['ip']+':'+str(port)]),None)
            if ct not in ids:assert old in rows
        assert len(rows)==17 and len({r['labels']['service'] for r in rows})==17,'Inventory/discovery mismatch'
        files[key]=json.dumps(rows,indent=2)+'\n'
    old_rules=yaml.safe_load(baseline['files']['rules/infra-hosts.yml'])
    new_rules=yaml.safe_load((root/'services/infra-prom/config/rules/infra-hosts.yml').read_text())
    def noncpu(doc):
        d=copy.deepcopy(doc)
        for group in d['groups']:
            group['rules']=[r for r in group['rules'] if r.get('alert')!='HostHighCpuUsage']
            for rule in group['rules']:
                if rule.get('alert')=='HostMemoryFillingFast':
                    original='predict_linear(node_memory_MemAvailable_bytes{job="node_exporter"}[1h], 4 * 3600) < 0'
                    qualified='('+original+') and on (job, instance, service, cpu_contract, vmid) (changes(node_memory_MemTotal_bytes{job="node_exporter"}[1h]) == 0) and on (job, instance, service, cpu_contract, vmid) (up{job="node_exporter"} == 1)'
                    assert rule['expr'] in [original,qualified], 'Unreviewed memory prediction change'
                    rule['expr']=original
        return d
    assert noncpu(old_rules)==noncpu(new_rules), 'Unrelated host rule change refused'
    inventory_rules=[]
    for ct in sorted(ids):
        svc=inventory[ct]
        inventory_rules.append({'record':'lxc:cpu_inventory:expected','expr':'vector(1)',
          'labels':{'job':'node_exporter','instance':svc['ip']+':9100','service':svc['name'],'ct_id':str(ct)}})
    files['rules/lxc-cpu-inventory.yml']=yaml.safe_dump({'groups':[{'name':'lxc_cpu_inventory','rules':inventory_rules}]},sort_keys=False,allow_unicode=True)
    # Copy only CPU compatibility rules, never the prepared global config/targets.
    for name in ['infra-hosts.yml','lxc-cpu.yml','lxc-cpu-targets.yml']:
        files['rules/'+name]=(root/'services/infra-prom/config/rules'/name).read_text()
    assert files['prometheus.yml']==baseline['files']['prometheus.yml']
    for path,old in baseline['files'].items():
        if path not in ['targets/node-exporter.json','targets/cadvisor.json','rules/infra-hosts.yml','rules/lxc-cpu.yml','rules/lxc-cpu-inventory.yml','rules/lxc-cpu-targets.yml']:assert files[path]==old
    return files,{'mode':'PREPARED_NOT_DEPLOYED','reliable_exporters_cts':sorted(ids),'prometheus_chain_verified_cts':state['telegram_chain_verified'],
                  'pending_unverified_cts':sorted(set(inventory)-ids),'node_targets':17,'cadvisor_targets':17,
                  'grafana_or_blackbox_changes':False,'baseline_sha256':{k:checksum(v) for k,v in baseline['files'].items()},
                  'candidate_sha256':{k:checksum(v) for k,v in files.items()}}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--state',type=Path,default=ROOT/'services/common/exporter-migration.yml');p.add_argument('--output',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    files,report=build(json.loads(a.baseline.read_text()),yaml.safe_load(a.state.read_text()),generator.load_services())
    os.umask(0o077);a.output.mkdir(parents=True,exist_ok=True,mode=0o700);a.output.chmod(0o700)
    for name,body in files.items():
        f=a.output/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(body);f.chmod(0o600)
    # Validation copy only; the deployment candidate retains the real paths unchanged.
    (a.output/'check-prometheus.yml').write_text(files['prometheus.yml'].replace('/etc/prometheus/',str(a.output.resolve())+'/'))
    a.report.write_text(json.dumps(report,indent=2)+'\n');print('Prepared: 17 mixed-state targets, only validated exporters promoted; no deployment')

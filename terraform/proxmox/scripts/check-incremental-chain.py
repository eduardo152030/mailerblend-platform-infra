#!/usr/bin/env python3
"""Read-only Prometheus chain check or local generation of an exporter-backed test rule."""
import argparse
import json
import math
from pathlib import Path
import re
import urllib.parse
import urllib.request
import yaml


def verification_rule(ct,run_id,enabled=True):
    assert ct>0 and re.fullmatch(r'[A-Za-z0-9_-]{1,60}',run_id)
    return {'groups':[{'name':'incremental_delivery_verification','rules':[{
      'alert':'LxcCpuIntegrationVerification','expr':'lxc:cpu_usage:percent{ct_id="'+str(ct)+'"} '+('>= 0' if enabled else '< 0'),
      'for':'30s','labels':{'severity':'info','integration_test_run':run_id},
      'annotations':{'summary':'Verificación de integración CPU LXC {{ $labels.ct_id }}','description':'Prueba controlada desde métricas reales; no se ha incrementado la carga del LXC.'}}]}]}


def assess(data):
    issues=[]
    for job in ['node_exporter','cadvisor']:
        rows=[t for t in data['targets'] if t['labels'].get('job')==job]
        if len(rows)!=1 or rows[0]['health']!='up':issues.append('Expected exactly one healthy '+job)
    nodes=[t for t in data['targets'] if t['labels'].get('job')=='node_exporter']
    if nodes and (nodes[0]['labels'].get('cpu_contract')!='lxc_cgroup_v1' or nodes[0]['labels'].get('vmid')!=str(data['ct'])):issues.append('Wrong Node contract/identity')
    values=data['cpu_percent']
    if len(values)!=1 or not math.isfinite(float(values[0]['value'][1])) or float(values[0]['value'][1])<0:issues.append('CPU percent missing/invalid; never substitute zero')
    if data['native_cpu']:issues.append('Shared CPU series still present')
    if len(data['cpu_valid'])!=1:issues.append('CPU contract is not valid')
    required={'HostHighCpuUsage','LxcCpuCollectorInvalid','LxcCpuTargetMissing'}
    for name in required:
        rules=[r for r in data['rules'] if r.get('name')==name]
        if len(rules)!=1 or rules[0].get('health')!='ok':issues.append('Missing/duplicate/unhealthy rule '+name)
    return issues


def fetch(base,path):
    with urllib.request.urlopen(base.rstrip('/')+path,timeout=15) as response:return json.load(response)


def collect(base,ct,service):
    assert re.fullmatch(r'[a-zA-Z0-9_-]+',service)
    def query(expr):return fetch(base,'/api/v1/query?'+urllib.parse.urlencode({'query':expr}))['data']['result']
    targets=fetch(base,'/api/v1/targets')['data']['activeTargets']
    return {'ct':ct,'targets':[t for t in targets if t['labels'].get('service')==service],
      'cpu_percent':query('lxc:cpu_usage:percent{ct_id="'+str(ct)+'",service="'+service+'"}'),
      'cpu_valid':query('lxc:cpu_contract:valid{ct_id="'+str(ct)+'",service="'+service+'"}'),
      'native_cpu':query('node_cpu_seconds_total{job="node_exporter",service="'+service+'"}'),
      'rules':[r for g in fetch(base,'/api/v1/rules')['data']['groups'] for r in g['rules']]}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ct',type=int,required=True);p.add_argument('--service');p.add_argument('--prometheus-url',default='http://192.168.1.110:9090');p.add_argument('--output',type=Path,required=True);p.add_argument('--prepare-test-run');p.add_argument('--resolved-rule',action='store_true');a=p.parse_args()
    if a.prepare_test_run:
        a.output.write_text(yaml.safe_dump(verification_rule(a.ct,a.prepare_test_run,not a.resolved_rule),sort_keys=False,allow_unicode=True));print('Local test rule prepared; not installed, no notifications sent')
    else:
        if not a.service:p.error('--service required for read-only check')
        data=collect(a.prometheus_url,a.ct,a.service);issues=assess(data)
        report={'ct':a.ct,'prometheus_rules_checks_passed':not issues,'issues':issues,'full_chain_verified':False,'telegram_delivery_requires_real_FIRING_and_RESOLVED_evidence_and_recipient_confirmation':True}
        a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));raise SystemExit(1 if issues else 0)

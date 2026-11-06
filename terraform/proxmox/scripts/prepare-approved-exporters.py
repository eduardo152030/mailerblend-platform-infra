#!/usr/bin/env python3
"""D025 local bundle builder. R2 reuses the tested bundle unchanged; other targets gated."""
import hashlib,importlib.util,json,tempfile,re,sys,inspect
import yaml
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def render(ct,out,audit):
 assert ct in [618,622,621,620,619,623,617,615,614,61211,611,616,610], 'Outside D025 scope'
 if ct not in [621,620]:return render_other(ct,out,audit)
 spec=importlib.util.spec_from_file_location('r2',ROOT/'scripts/prepare-r2-exporters.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 manifest=m.render(ct,out)
 assert audit['hostname']==m.TARGETS[ct]['host']
 assert audit['allocation']['cores']=='2' and audit['allocation']['memory']=='2048'
 manifest.update(cores=2,memory_mib=2048,ip=m.TARGETS[ct]['ip'],socket_and_namespace_approval='APPROVED_D025_SAME_REVIEWED_MODEL')
 for name in manifest['file_sha256']:
  path=out/name
  if path.suffix=='.py':compile(path.read_text(),str(path),'exec')
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest


def render_other(ct,out,audit):
 contracts=yaml.safe_load((ROOT/'services/common/approved-rollout.yml').read_text());contract=contracts['contracts'][ct]
 inventory=[yaml.safe_load(p.read_text())['service'] for p in (ROOT/'inventory/services').glob('*.yml')];svc=next(s for s in inventory if int(s['vmid'])==ct)
 assert audit.get('hostname')==svc['name'],'Fresh matching audit required';cores=int(audit['allocation']['cores']);memory=int(audit['allocation']['memory']);ip=svc['ip'].split('/')[0]
 spec=importlib.util.spec_from_file_location('r2',ROOT/'scripts/prepare-r2-exporters.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 with tempfile.TemporaryDirectory() as d:
  base=Path(d);m.render(621,base);files={p.name:p.read_text() for p in base.iterdir() if p.name!='manifest.json'}
 for n,body in files.items():
  body=body.replace('192.168.1.121',ip).replace('infra-project-gestion',svc['name']);body=re.sub(r'(?<![0-9a-f])621(?![0-9a-f])',str(ct),body);files[n]=body
 # D031: new R4/R5 candidates must not repeat the known dynamic+jitter freshness defect.
 # CT623 has a separate revision builder because an earlier candidate must be preserved.
 if ct in [617,615,614,61211]:
  config=yaml.safe_load(files['cadvisor.yml'])
  config['services']['cadvisor']['command']+=['--allow_dynamic_housekeeping=false','--max_housekeeping_interval=30s','--jitter_factor=0','--initial_splay_factor=0']
  files['cadvisor.yml']=yaml.safe_dump(config,sort_keys=False)
 lock=json.loads((ROOT/'services/common/phase4-images.json').read_text());node=lock['node'][svc['name']]['image'];old=lock['node']['infra-project-gestion']['image']
 helper=files['pilot.py'].replace(old,node).replace("mem['MemTotal'] == 2048 * 1024 and cpus == 2",f"mem['MemTotal'] == {memory} * 1024 and cpus == {cores}").replace("mem['MemAvailable'] >= 512 * 1024",f"mem['MemAvailable'] >= {min(512,max(128,memory//4))} * 1024").replace('== 2048 * 1024 * 1024',f'== {memory} * 1024 * 1024').replace("value('lxc_cpu_capacity_cores')==2",f"value('lxc_cpu_capacity_cores')=={cores}").replace('<=max(1,2*(age+1))',f'<=max(1,{cores}*(age+1))')
 apps={c['name']:c['compose_service'] for c in audit['containers'] if not c['name'].startswith(('node_exporter','cadvisor'))}
 assert all(c['running'] for c in audit['containers']), 'Review stopped application before rollout'
 assert ct!=610 or set(apps)=={'prometheus','alertmanager','eloquent_ganguly'}, 'Review Prometheus application inventory'
 body="def application_probe():\n    results=[]\n"
 for url in contract['urls']:body+=f"    with urllib.request.urlopen({url!r},timeout=8) as response:assert response.status==200\n    results.append({{'endpoint':{url!r},'status':200}})\n"
 for check in contract.get('http_status',[]):
  body+="    try:\n        with urllib.request.urlopen("+repr(check['url'])+",timeout=8) as response:status=response.status\n    except urllib.error.HTTPError as exc:status=exc.code\n    assert status=="+str(check['expected'])+"\n    results.append({'endpoint':"+repr(check['url'])+",'status':status})\n"
 for check in contract.get('backend_http',[]):
  body+="    container=json.loads(subprocess.check_output(['docker','inspect',"+repr(check['container'])+"]))[0]\n    addresses=[n['IPAddress'] for n in container['NetworkSettings']['Networks'].values() if n.get('IPAddress')]\n    assert len(addresses)==1\n    with urllib.request.urlopen('http://'+addresses[0]+':"+str(check['port'])+check['path']+"',timeout=8) as response:assert response.status=="+str(check['expected'])+"\n    results.append({'container':"+repr(check['container'])+",'status':"+str(check['expected'])+"})\n"
 for cmd in contract['exec']:body+=f"    assert subprocess.run({cmd!r},capture_output=True,timeout=10).returncode==0,'Database readiness failed'\n"
 body+="    return {'status':200,'application_health':"+repr(contract.get("application_baseline","endpoints_available"))+",'read_only_application_checks':results}\n"
 def literal(names):return 'set('+repr(tuple(sorted(names)))+')'
 active=literal(set(apps)|{'node_exporter','cadvisor'})
 app_identity_names=audit.get('all_application_names',list(apps))
 a=helper.index('def application_probe():');b=helper.index('def scope_guard',a)
 web="\ndef web():\n    assert {x['name'] for x in identities()}=="+literal(app_identity_names)+"\n    assert set(run(['docker','ps','--format','{{.Names}}']).decode().split())=="+active+"\n    return application_probe()\n\n"
 files['pilot.py']=helper[:a]+body+web+helper[b:]
 sampler=files['sample.py'];a=sampler.index('def application_probe():');b=sampler.index("if __name__=='__main__':",a);sampler=sampler[:a]+body+'\n'+sampler[b:]
 sampler=sampler.replace("set(('cadvisor', 'focalboard', 'node_exporter'))",active);files['sample.py']=sampler
 observer=files['observe.py'];a=observer.index('    assert set(active)==');b=observer.index('class WindowTracker:',a)
 extra='    assert set(active)=='+active+"\n    assert sample['integration']['node_and_cadvisor_up'] and sample['integration']['rules_healthy'] and sample['integration']['alertmanager_ready']\n"
 for name,service in apps.items():
  if service:extra+="    row=next(r for r in sample['cadvisor']['container_memory_usage_bytes'] if r['labels'].get('name','').lstrip('/')=="+repr(name)+")\n    assert row['labels'].get('container_label_com_docker_compose_service')=="+repr(service)+"\n"
 observer=observer[:a]+extra+'\n'+observer[b:]
 observer=observer.replace('2048*1024*1024',f'{memory}*1024*1024').replace("['cpu_count']==2",f"['cpu_count']=={cores}").replace("node_value('lxc_cpu_capacity_cores')==2",f"node_value('lxc_cpu_capacity_cores')=={cores}").replace('max(1,2*(age+2))',f'max(1,{cores}*(age+2))').replace('256*1024*1024',f'{min(256,max(64,memory//8))}*1024*1024')
 ps=importlib.util.spec_from_file_location('window_policy',ROOT/'scripts/rollout-observation-policy.py');pm=importlib.util.module_from_spec(ps);sys.modules[ps.name]=pm;ps.loader.exec_module(pm);window=pm.policy(contract['batch'])
 if contract['batch']=='R7':observer=observer.replace('WindowTracker(180,7,','WindowTracker(600,21,')
 if ct in [618,622]:observer=observer.replace("if not c['name'].startswith(('node_exporter','cadvisor'))}","if c['running'] and not c['name'].startswith(('node_exporter','cadvisor'))}")
 files['observe.py']=observer
 files['node-cgroup.sh']=files['node-cgroup.sh'].replace(' = 2 ]',f' = {cores} ]').replace('cores%s 2\\n',f'cores%s {cores}\\n')
 # D029: compare CPU at its actual sample timestamp; preserve every other gate.
 spec_contract=importlib.util.spec_from_file_location('metric_contract',ROOT/'scripts/exporter_metric_contract.py');metric_contract_module=importlib.util.module_from_spec(spec_contract);spec_contract.loader.exec_module(metric_contract_module)
 files['cpu-alignment.py']=metric_contract_module.render_alignment_source('cpu')
 old="'value':value})"
 assert files['sample.py'].count(old)==1
 files['sample.py']=files['sample.py'].replace(old,"'value':value,'timestamp':float(tail.split()[1])/1000 if len(tail.split())>1 else None})")
 tree_sampler=__import__('ast').parse(files['sample.py']);fn_rows=next(n for n in tree_sampler.body if isinstance(n,__import__('ast').FunctionDef) and n.name=='rows');old_rows=__import__('ast').get_source_segment(files['sample.py'],fn_rows)
 files['sample.py']=files['sample.py'].replace(old_rows,"def rows(text,metric):\n    ns={'__name__':'metric_parser'}\n    exec(Path(CPU_HISTORY_PATH).with_name('cpu-alignment.py').read_text(),ns)\n    return ns['mc'].prom_rows(text,metric)")
 marker="    print(json.dumps(out,sort_keys=True))"
 assert files['sample.py'].count(marker)==1
 files['sample.py']=files['sample.py'].replace(marker,"    cpu_ns={'__name__':'cpu_alignment'}\n    exec(Path(CPU_HISTORY_PATH).with_name('cpu-alignment.py').read_text(),cpu_ns)\n    out['measurement_contract_schema']=cpu_ns['mc'].SCHEMA\n    out['measurement_scope']=cpu_ns['mc'].scope()\n    try:\n        cpu_ns['require_collector'](CPU_HISTORY_PATH)\n        history=cpu_ns['history_for_sample'](out,CPU_HISTORY_PATH)\n        out['cpu_alignment']=cpu_ns['aligned_evidence'](out,history)\n    except Exception as exc:\n        cpu_ns['record_probe_failure'](out,CPU_HISTORY_PATH,exc)\n        raise\n"+marker)
 old="                assert abs(row['value']-api['cpu_total_ns']/1e9)<=max(1.0,api['cpu_total_ns']/1e9*.03),'cAdvisor/Docker CPU mismatch: '+name"
 assert files['observe.py'].count(old)==1
 files['observe.py']=files['observe.py'].replace(old,"                assert api['cpu_total_ns']>=0,'Invalid Docker CPU counter'")
 marker="    # Direct cgroup/API consistency; cadvisor is cached at a 30s housekeeping interval."
 assert files['observe.py'].count(marker)==1
 library=files['cpu-alignment.py'].split("\nif __name__=='__main__':")[0]
 files['observe.py']=library+'\n'+files['observe.py'].replace(marker,"    validate_alignment(sample,previous)\n"+marker)
 out=Path(out);out.mkdir(parents=True,exist_ok=True);assert not (out/'baseline.json').exists()
 for name,body in files.items():
  if name.endswith('.py'):compile(body,name,'exec')
  (out/name).write_text(body)
 manifest={'ct':ct,'service':svc['name'],'ip':ip,'cores':cores,'memory_mib':memory,'node_image':node,'cadvisor_image':lock['cadvisor_candidate']['image'],'initial_seconds':window['seconds'],'initial_minimum_samples':window['minimum_samples'],'apps':apps,'application_urls':contract['urls'],'file_sha256':{n:hashlib.sha256(s.encode()).hexdigest() for n,s in files.items()},'measurement_contract_schema':metric_contract_module.SCHEMA,'measurement_contract_sha256':hashlib.sha256((ROOT/'scripts/exporter_metric_contract.py').read_bytes()).hexdigest(),'socket_and_namespace_approval':'D025_REVIEWED_MODEL_ONLY'}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest

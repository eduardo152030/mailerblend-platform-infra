#!/usr/bin/env python3
"""Prepare only R2 CT621/620, including 180s initial gate and continued integrated watch."""
import argparse,hashlib,importlib.util,json,tempfile,inspect,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('journal',ROOT/'scripts/prepare-journal-exporters.py');journal=importlib.util.module_from_spec(spec);spec.loader.exec_module(journal)
TARGETS={621:{'host':'infra-project-gestion','ip':'192.168.1.121','apps':{'focalboard':'focalboard'},'urls':['http://192.168.1.121:8081/']},620:{'host':'infra-excraper','ip':'192.168.1.120','apps':{'infra-excraper-linkedin-worker-1':'linkedin-worker','infra-excraper-signals-worker-1':'signals-worker','infra-excraper-redis-1':'redis'},'urls':['http://192.168.1.120:3000/health','http://192.168.1.120:3001/health']}}

def render(ct,output):
    assert ct in TARGETS;target=TARGETS[ct]
    with tempfile.TemporaryDirectory() as tmp:
        journal.render(626,Path(tmp));files={p.name:p.read_text() for p in sorted(Path(tmp).iterdir()) if p.name!='manifest.json'}
    def adapt(s):return s.replace('626',str(ct)).replace('infra-journal-api',target['host']).replace('192.168.1.126',target['ip'])
    files={n:adapt(s) for n,s in files.items()}
    lock=json.loads((ROOT/'services/common/phase4-images.json').read_text());node_image=lock['node'][target['host']]['image']
    old='prom/node-exporter@sha256:3ac34ce007accad95afed72149e0d2b927b7e42fd1c866149b945b84737c62c3'
    files['pilot.py']=files['pilot.py'].replace(old,node_image)
    body="""def application_probe():
    results=[]
    for url in URLS:
        with urllib.request.urlopen(url,timeout=8) as response:
            assert response.status==200
            if '/health' in url:assert json.loads(response.read()).get('status')=='healthy'
        results.append({'endpoint':url,'status':200})
    REDIS
    return {'status':200,'read_only_application_checks':results}
""".replace('URLS',repr(target['urls'])).replace('REDIS',"assert subprocess.check_output(['docker','exec','infra-excraper-redis-1','redis-cli','ping'],timeout=8).strip()==b'PONG'" if ct==620 else 'pass')
    def set_literal(names):return 'set('+repr(tuple(sorted(names)))+')'
    helper=files['pilot.py'];a=helper.index('def web():');b=helper.index('\n\ndef scope_guard',a)
    web="\ndef web():\n    assert {x['name'] for x in identities()}=="+set_literal(target['apps'])+", 'Application inventory drift'\n    assert set(run(['docker','ps','--format','{{.Names}}']).decode().split())=="+set_literal(set(target['apps'])|{'node_exporter','cadvisor'})+", 'Unexpected application or stopped service'\n    return application_probe()\n"
    files['pilot.py']=helper[:a]+body+web+helper[b:]
    files['pilot.py']=files['pilot.py'].replace("assert containerd_socket_ready(), 'Missing containerd socket'","assert containerd_socket_ready(), 'Missing containerd socket'\n    assert all(Path(p).is_dir() for p in ['/var/lib/docker','/var/lib/containerd','/sys']), 'Required bind directory absent'")
    sampler=files['sample.py'];a=sampler.index('    web=fetch(');b=sampler.index("    mem=Path('/proc/meminfo')",a)
    sampler=sampler[:a]+"    assert {c['name'] for c in out['containers'] if c['running']}=="+set_literal(set(target['apps'])|{'node_exporter','cadvisor'})+"\n    out['web']=application_probe()\n"+sampler[b:]
    sampler=sampler.replace("if __name__=='__main__':",body+"\nif __name__=='__main__':")
    sampler += ''
    # Append integrated checks before JSON output; no credentials, jobs, writes or messages.
    integrated='''    import urllib.parse,math
    base='http://192.168.1.110:9090'
    def pq(expr):return json.loads(fetch(base+'/api/v1/query?'+urllib.parse.urlencode({'query':expr})))['data']['result']
    targets=json.loads(fetch(base+'/api/v1/targets'))['data']['activeTargets']
    subset=[t for t in targets if t['labels'].get('service')==SERVICE]
    for job in ['node_exporter','cadvisor']:
        found=[t for t in subset if t['labels'].get('job')==job];assert len(found)==1 and found[0]['health']=='up'
    percent=pq('lxc:cpu_usage:percent{ct_id="CT",service="SERVICE_NAME"}')
    assert len(percent)==1 and math.isfinite(float(percent[0]['value'][1])) and float(percent[0]['value'][1])>=0
    rules=json.loads(fetch(base+'/api/v1/rules'))['data']['groups']
    assert all(r['health']=='ok' for g in rules for r in g['rules'])
    fetch('http://192.168.1.110:9093/-/ready')
    out['integration']={'node_and_cadvisor_up':True,'cpu_percent':float(percent[0]['value'][1]),'rules_healthy':True,'alertmanager_ready':True}
'''.replace('SERVICE_NAME',target['host']).replace('SERVICE',repr(target['host'])).replace('CT',str(ct))
    sampler=sampler.replace('    print(json.dumps(out,sort_keys=True))',integrated+'    print(json.dumps(out,sort_keys=True))');files['sample.py']=sampler
    observer=files['observe.py'];a=observer.index("    web=next(r for r in sample['cadvisor']['container_memory_usage_bytes']");b=observer.index('\n\ndef main',a)
    extra="    assert set(active)=="+set_literal(set(target['apps'])|{'node_exporter','cadvisor'})+"\n    assert sample['integration']['node_and_cadvisor_up'] and sample['integration']['rules_healthy'] and sample['integration']['alertmanager_ready']\n"
    for name,service in target['apps'].items():extra+="    row=next(r for r in sample['cadvisor']['container_memory_usage_bytes'] if r['labels'].get('name','').lstrip('/')=="+repr(name)+")\n    assert row['labels'].get('container_label_com_docker_compose_service')=="+repr(service)+"\n"
    observer=observer[:a]+extra+observer[b:]
    # Reuse validated metric gates; replace only scheduler/window lifecycle.
    a=observer.index('def main():')
    main=(ROOT/'services/common/r2-watch-main.py.txt').read_text().replace('CT_NUMBER',str(ct))
    ps=importlib.util.spec_from_file_location('observation_policy',ROOT/'scripts/rollout-observation-policy.py');pm=importlib.util.module_from_spec(ps);sys.modules[ps.name]=pm;ps.loader.exec_module(pm);window=pm.policy('R2')
    for key,value in {'INITIAL_SECONDS':window['seconds'],'MIN_INITIAL_SAMPLES':window['minimum_samples'],'WATCH_SECONDS':window['watch_seconds'],'SAMPLE_INTERVAL':window['interval'],'ANOMALY_SECONDS':window['extended_seconds']}.items():main=main.replace(key,str(value))
    observer=observer[:a]+inspect.getsource(pm.WindowTracker)+'\n'+main;files['observe.py']=observer
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    assert not any((output/n).exists() for n in ['baseline.json','applied.json'])
    for name,content in files.items():(output/name).write_text(content)
    manifest={'ct':ct,'service':target['host'],'status':'PREPARED_NOT_DEPLOYED','node_image':node_image,'cadvisor_image':lock['cadvisor_candidate']['image'],'initial_seconds':window['seconds'],'initial_minimum_samples':window['minimum_samples'],'interval_seconds':window['interval'],'continued_external_watch_seconds':window['watch_seconds'],'continuous_prometheus_alertmanager_required':True,'alert_for_runtime_firing_validated':False,'anomaly_extended_seconds':600,'socket_and_namespace_approval':'PENDING_FOR_R2','apps':target['apps'],'application_urls':target['urls'],'file_sha256':{n:hashlib.sha256(s.encode()).hexdigest() for n,s in files.items()}}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ct',type=int,choices=TARGETS,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(render(a.ct,a.output),indent=2))

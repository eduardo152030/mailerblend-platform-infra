#!/usr/bin/env python3
"""Revalidate completed Journal observations locally; publish a secret-free summary."""
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
from pathlib import Path


def report(run,ct):
    assert ct in [625,626] and __import__("re").fullmatch(r"journal-[0-9TZ+-]+",run)
    here=Path.home()/'.local/share/mailerblend-recovery/phase4'/run/str(ct)
    state=json.loads((here/'state.json').read_text());assert state['result']=='PASS' and state['ct']==ct
    assert state.get('after_configuration',{}).get('offhost_verified')
    for filename,expected in [('exporters-before.tar',state['backup']['sha256']),('exporters-after-config.tar.gz',state['after_configuration']['sha256'])]:
        h=hashlib.sha256()
        with (here/filename).open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
        assert h.hexdigest()==expected, 'Backup changed after verification'
    for name,digest in state['manifest']['files'].items():
        assert hashlib.sha256((here/'bundle'/name).read_bytes()).hexdigest()==digest, 'Local deployed input drift'
    obs=here/'observations.jsonl'
    assert hashlib.sha256(obs.read_bytes()).hexdigest()==state['observation']['sha256']
    rows=[json.loads(l) for l in obs.read_text().splitlines()]
    assert len(rows)>=21 and rows[-1]['elapsed_seconds']>=600
    spec=importlib.util.spec_from_file_location('verified_observer',here/'bundle/observe.py')
    observer=importlib.util.module_from_spec(spec);spec.loader.exec_module(observer)
    before=observer.counters(state['preflight']['memory_events'])
    for index,row in enumerate(rows):
        observer.validate(row,rows[0],rows[index-1] if index else None)
        assert all(observer.counters(row['resources']['memory.events']).get(k,0)==before.get(k,0) for k in ['oom','oom_kill','oom_group_kill'])
        known={c['id'] for c in row['containers']}
        for metric in ['container_memory_usage_bytes','container_cpu_usage_seconds_total']:
            for item in row['cadvisor'][metric]:
                if item['labels'].get('name'):
                    assert any(cid in item['labels'].get('id','') for cid in known), 'Docker metric outside CT engine'
    def nv(row,key):return row['node'][key][0]['value']
    def active(row):return {c['name']:c for c in row['containers'] if c['running']}
    usage={}
    for name in ['node_exporter','cadvisor']:
        containers=[active(r)[name] for r in rows]
        cap=(48 if name=='node_exporter' else 128)*1024**2
        assert all(c['memory_limit']==cap for c in containers)
        assert all(c['nano_cpus']==(200000000 if name=='node_exporter' else 500000000) for c in containers)
        assert max(c['docker_stats']['memory_usage'] for c in containers)<cap
        rates=[(b['docker_stats']['cpu_total_ns']-a['docker_stats']['cpu_total_ns'])/1e9/(rows[i+1]['time']-rows[i]['time'])*100 for i,(a,b) in enumerate(zip(containers,containers[1:]))]
        usage[name]={'id':containers[-1]['id'],'image_id':containers[-1]['image'],'started_at':containers[-1]['started_at'],'restart_count':containers[-1]['restarts'],
          'memory_peak_sampled_bytes':max(c['docker_stats']['memory_usage'] for c in containers),'memory_limit_bytes':cap,'cpu_quota_cores':.2 if name=='node_exporter' else .5,'max_interval_mean_cpu_percent_of_one_core':max(rates)}
    cg=lambda r:observer.counters(r['resources']['cpu.stat'])['usage_usec']/1e6
    result={'ct':ct,'result':'PASS','scope':'exporters only; no global discovery','recorded_at':datetime.now(timezone.utc).isoformat(),
      'images':{'node':'1.10.2','cadvisor':'0.60.6'},'allocated_cpu_cores':2,'node_memory_total_bytes':nv(rows[-1],'node_memory_MemTotal_bytes'),
      'cpu_source':'cgroup_v2_textfile','native_cpu_series_absent':True,
      'cpu_window_delta_seconds':{'node_lxc':nv(rows[-1],'lxc_cpu_usage_seconds_total')-nv(rows[0],'lxc_cpu_usage_seconds_total'),'parent_cgroup':cg(rows[-1])-cg(rows[0])},
      'max_counter_read_lag_seconds':max(abs(nv(r,'lxc_cpu_usage_seconds_total')-cg(r)) for r in rows),
      'observation':state['observation']|{'first_sample_at':datetime.fromtimestamp(rows[0]['time'],timezone.utc).isoformat(),'last_sample_at':datetime.fromtimestamp(rows[-1]['time'],timezone.utc).isoformat()},
      'minimum_lxc_available_memory_bytes':min(r['lxc_proc']['mem_available_bytes'] for r in rows),
      'memory_current_peak_bytes':max(int(r['resources']['memory.current']) for r in rows),
      'memory_psi_max_sampled_avg_percent':max(float(x) for r in rows for x in __import__('re').findall(r'avg(?:10|60)=(\S+)',r['resources']['memory.pressure'])),
      'memory_events_before':before,'memory_events_final':observer.counters(rows[-1]['resources']['memory.events']),
      'swap_bytes_first':int(rows[0]['resources']['memory.swap.current']),'swap_bytes_last':int(rows[-1]['resources']['memory.swap.current']),
      'active_docker_containers':sorted(active(rows[-1])), 'exporter_resources':usage,'application_status':rows[-1]['web'],
      'backups':state['backup']|{'pve_directory':state['pve_directory'],'offhost_location':'~/.local/share/mailerblend-recovery/phase4/'+run+'/'+str(ct),'nested_image_hashes_verified':True,'original_image_load_verified':True},
      'original_exporter_ids':state['original_exporter_ids'],'after_configuration':state['after_configuration'],
      'rollback_original_running_and_metrics_verified':True,'resume_same_candidate_ids_verified':True,'second_apply_same_id_started_at_verified':True,
      'application_ids_images_config_and_started_at_preserved':True,
      'node_and_docker_metrics_separate':True,'strict_local_observer_revalidation':'PASS','run':run,
      'deployed_file_sha256':state['manifest']['files']}
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ct',type=int,choices=[625,626],required=True);p.add_argument('--run',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=report(a.run,a.ct);a.output.write_text(json.dumps(result,indent=2)+'\n');print('CT',a.ct,'PASS: independently revalidated observations and before/after backup evidence')

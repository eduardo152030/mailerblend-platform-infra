#!/usr/bin/env python3
"""Run on PVE: sample only CT 624, with explicit quality/stability gates and no rollout."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import time


def cg(path):
    result={}
    for name in ['memory.current','memory.max','memory.swap.current','memory.events','memory.pressure','cpu.stat','cpu.max','cpuset.cpus.effective']:
        p=path/name
        if p.exists():result[name]=p.read_text().strip()
    return result


def counters(text):
    return {k:int(v) for k,v in (x.split() for x in text.splitlines())}


def validate(sample, initial, previous=None):
    assert sample['web']['status']==200
    assert sample['web']==initial['web'],'Journal Web body/status changed'
    r=sample['resources']
    assert int(r['memory.max'])==512*1024*1024
    for key in ['oom','oom_kill','oom_group_kill']:
        assert counters(r['memory.events']).get(key,0)==counters(initial['resources']['memory.events']).get(key,0),'New OOM event'
    assert all(float(n)<=5 for n in re.findall(r'avg(?:10|60)=(\S+)',r['memory.pressure'])),'Significant memory PSI'
    assert sample['lxc_proc']['mem_available_bytes']>=64*1024*1024,'Insufficient available memory'
    assert sample['lxc_proc']['cpu_count']==1
    assert sample['node']['node_memory_MemTotal_bytes'][0]['value']==512*1024*1024
    assert not sample['node']['node_cpu_seconds_total'], 'Wrong physical CPU collector still enabled'
    def node_value(key):
        rows=sample['node'][key];assert len(rows)==1
        return rows[0]['value']
    assert node_value('lxc_cpu_capacity_cores')==1 and node_value('lxc_cpu_collector_success')==1
    assert node_value('node_textfile_scrape_error')==0
    age=sample['time']-node_value('lxc_cpu_collector_timestamp_seconds')
    assert -2<=age<=15, 'CPU collector stale'
    total=node_value('lxc_cpu_usage_seconds_total')
    direct=counters(r['cpu.stat'])['usage_usec']/1e6
    assert abs(total-direct)<=max(1,age+2), 'LXC CPU counter does not match Proxmox cgroup'
    for metric,field in [('lxc_cpu_user_seconds_total','user_usec'),('lxc_cpu_system_seconds_total','system_usec')]:
        assert abs(node_value(metric)-counters(r['cpu.stat'])[field]/1e6)<=max(1,age+2)
    assert sample['node']['lxc_cpu_usage_seconds_total'][0]['labels'].get('ct_id')=='624'
    assert sample['node']['lxc_cpu_usage_seconds_total'][0]['labels'].get('cpu_source')=='cgroup_v2'
    active={c['name']:c for c in sample['containers'] if c['running']}
    initial_apps={c['name']:c for c in initial['containers'] if not c['name'].startswith(('node_exporter','cadvisor'))}
    for name,c in initial_apps.items():
        now=active[name]
        assert all(now[k]==c[k] for k in ['id','image','started_at','restarts']),'Application changed'
    for name in ['node_exporter','cadvisor']:
        assert active[name]['restarts']==0 and not active[name]['oom_killed'],'Exporter unstable'
        if previous:
            prev=next(c for c in previous['containers'] if c['name']==name)
            assert (active[name]['id'],active[name]['started_at'])==(prev['id'],prev['started_at'])
    known={c['id'] for c in sample['containers']}
    for key in ['container_memory_usage_bytes','container_cpu_usage_seconds_total']:
        rows=sample['cadvisor'][key]
        for name in active:
            matching=[row for row in rows if row['labels'].get('name','').lstrip('/')==name and active[name]['id'] in row['labels'].get('id','')]
            assert len(matching)==1,'Missing/duplicate current Docker identity: '+name
            row=matching[0]
            assert any(cid in row['labels'].get('id','') for cid in known),'Metric outside target Docker engine'
            assert row['value']>=0
            api=active[name]['docker_stats']
            if key=='container_memory_usage_bytes':
                allowance=max(4*1024*1024,api['memory_usage']*.30) if name in ['node_exporter','cadvisor'] else max(512*1024,api['memory_usage']*.20)
                assert abs(row['value']-api['memory_usage'])<=allowance,'cAdvisor/Docker RAM mismatch: '+name
            else:
                assert abs(row['value']-api['cpu_total_ns']/1e9)<=max(1.0,api['cpu_total_ns']/1e9*.03),'cAdvisor/Docker CPU mismatch: '+name
    # Direct cgroup/API consistency; cadvisor is cached at a 30s housekeeping interval.
    for name,c in active.items():
        assert c.get('cgroup'), 'Missing direct cgroup evidence: '+name
        assert 'memory.current' in c['cgroup'] and 'cpu.stat' in c['cgroup']
        api=c['docker_stats']
        assert api['memory_usage'] is not None and api['cpu_total_ns'] is not None
        direct=int(c['cgroup']['memory.current'])
        assert abs(api['memory_usage']-direct)<=max(8*1024*1024,direct*.25),'Docker API/cgroup RAM mismatch'
    # Useful Compose labels must identify the Journal application independently of exporters.
    for name,c in active.items():
        seen=[row for row in sample['cadvisor']['container_last_seen'] if c['id'] in row['labels'].get('id','')]
        assert len(seen)==1, 'Missing freshness evidence: '+name
        assert -5<=sample['time']-seen[0]['value']<=90, 'Stale cAdvisor collection'
    web=next(r for r in sample['cadvisor']['container_memory_usage_bytes'] if r['labels'].get('name','').lstrip('/')=='infra-journal-web-web-1')
    assert web['labels'].get('container_label_com_docker_compose_service')=='web'
    assert web['labels'].get('container_label_com_docker_compose_project')=='infra-journal-web'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--probe',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--seconds',type=int,default=600)
    p.add_argument('--interval',type=int,default=30)
    args=p.parse_args()
    assert args.seconds>=600 and 1<=args.interval<=30
    assert Path('/etc/pve/lxc/624.conf').is_file(),'Run only on existing PVE node'
    root=Path('/sys/fs/cgroup/lxc/624')
    assert root.is_dir()
    initial=None;previous=None;start=time.monotonic();n=0
    fd=os.open(args.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as out:
        while True:
            r=subprocess.run(['pct','exec','624','--','python3','-'],input=args.probe.read_text(),capture_output=True,text=True,timeout=30)
            assert r.returncode==0,'Read-only probe failed'
            sample=json.loads(r.stdout);sample['resources']=cg(root)
            for c in sample['containers']:
                if not c['running']:continue
                paths=list(root.rglob('docker-'+c['id']+'.scope'))
                if not paths:paths=list(root.rglob(c['id']))
                if len(paths)==1:c['cgroup']=cg(paths[0])
            if initial is None:initial=sample
            validate(sample,initial,previous)
            sample['elapsed_seconds']=round(time.monotonic()-start,3)
            out.write(json.dumps(sample)+'\n');out.flush()
            n+=1;previous=sample
            print('validated sample',n,'elapsed',sample['elapsed_seconds'],'seconds',flush=True)
            if time.monotonic()-start>=args.seconds:break
            time.sleep(min(args.interval,max(.1,args.seconds-(time.monotonic()-start))))
    print('Pilot observation passed: >=600 seconds with application, identity, resource and OOM gates.',flush=True)


if __name__=='__main__':main()

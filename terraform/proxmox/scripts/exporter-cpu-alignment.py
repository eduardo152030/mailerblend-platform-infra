"""Contadores CPU con identidad, timestamp y ventana comunes; solo lectura Docker/cgroup."""
import bisect
from datetime import datetime
import http.client
import json
import math
from pathlib import Path
import re
import socket
import time

# BEGIN METRIC CONTRACT LOADER
import importlib.util as _contract_import
_contract_spec=_contract_import.spec_from_file_location('exporter_metric_contract',Path(__file__).with_name('exporter_metric_contract.py'))
mc=_contract_import.module_from_spec(_contract_spec)
_contract_spec.loader.exec_module(mc)
# END METRIC CONTRACT LOADER

timestamp=mc.timestamp

def tolerance(seconds):
    mc.finite(seconds,'CPU tolerance reference',nonnegative=False)
    return max(mc.LIMITS['cpu_floor_seconds'],abs(seconds)*mc.LIMITS['cpu_fraction'])

def _pair(history,when,field):
    for p in history:mc.finite(p.get(field),field)
    pair=mc.bracket(history,when)
    assert pair[1][field]>=pair[0][field],'CPU counter reset inside alignment interval'
    return pair

def interpolate(history,when,field):
    a,b=_pair(history,when,field)
    return a[field]+(b[field]-a[field])*(when-a['time'])/(b['time']-a['time'])

def bounds(history,when,field):
    return [p[field] for p in _pair(history,when,field)]


def aligned_evidence(sample, history):
    result={}
    for cid,c in mc.active(sample).items():
        row=mc.metric(sample,'container_cpu_usage_seconds_total',c);when=row['timestamp']
        age=time.time()-when
        assert -5<=age<=90,('CPU metric data stale: '+c['name']+' id='+cid+' metric_time='+str(when)+' observed_time='+str(when+age)+' age_seconds='+str(age)+' cpu_seconds='+str(row['value']))
        current=mc.points(history,c,['docker_seconds','cgroup_seconds'])
        for field in ['docker_seconds','cgroup_seconds']:
            assert all(b[field]>=a[field] for a,b in zip(current,current[1:])),'CPU counter reset inside history'
        docker=interpolate(current,when,'docker_seconds')
        cgroup=interpolate(current,when,'cgroup_seconds')
        intervals={f:bounds(current,when,f) for f in ['docker_seconds','cgroup_seconds']}
        assert math.isfinite(row['value']) and row['value']>=0,'Invalid CPU counter'
        for interval in intervals.values():
            for value in interval:assert abs(row['value']-value)<=tolerance(value),'Aligned cAdvisor CPU mismatch: '+c['name']
        assert abs(docker-cgroup)<=tolerance(cgroup),'Aligned Docker/cgroup CPU mismatch: '+c['name']
        result[cid]={'name':c['name'],'started_at':c['started_at'],'time':when,'cadvisor_seconds':row['value'],'docker_seconds':docker,'cgroup_seconds':cgroup,'bounds':intervals}
        if c.get('_scope'):result[cid]['measurement_scope']=c['_scope']
    return result

def require_collector(path):
    mc.require_collector(path,'cpu-alignment.py')


def history_for_sample(sample,path):
    deadline=time.monotonic()+2
    active=mc.active(sample)
    metrics=[mc.metric(sample,'container_cpu_usage_seconds_total',c) for c in active.values()]
    while True:
        # Keep bounded memory even when the source retains its complete incident history.
        earliest=min(r['timestamp'] for r in metrics)-2;latest=max(r['timestamp'] for r in metrics)+2
        history=mc.read_history(path,earliest,latest)
        complete=True
        for cid,c in active.items():
            when=mc.metric(sample,'container_cpu_usage_seconds_total',c)['timestamp']
            times=[r['time'] for r in history if r.get('id')==cid and r.get('started_at')==c['started_at']]
            if not times or not min(times)<when<max(times):complete=False
        if complete:return history
        assert time.monotonic()<deadline,'CPU timeline does not bracket metric timestamp'
        time.sleep(.1)


def record_probe_failure(sample,path,exc):
    import os,traceback
    destination=Path(path).with_name('cpu-probe-failures.jsonl')
    fd=os.open(destination,os.O_CREAT|os.O_WRONLY|os.O_APPEND,0o600)
    with os.fdopen(fd,'a') as out:out.write(json.dumps({'sample':sample,'failure_type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()})+'\n')

def validate_alignment(sample,previous=None):
    aligned=sample.get('cpu_alignment')
    active=mc.active(sample)
    assert aligned and set(aligned)==set(active),'Aligned CPU evidence required for every running container'
    for cid,point in aligned.items():
        assert point['started_at']==active[cid]['started_at'] and point['name']==active[cid]['name'],'Aligned CPU generation mismatch'
        if active[cid].get('_scope'):assert point.get('measurement_scope')==active[cid]['_scope'],'CPU measurement scope mismatch'
        row=mc.metric(sample,'container_cpu_usage_seconds_total',active[cid])
        assert row['timestamp']==point['time'] and row['value']==point['cadvisor_seconds'],'CPU raw metric/evidence mismatch'
        mc.fresh(point['time'],time.time())
        for field in ['cadvisor_seconds','docker_seconds','cgroup_seconds']:
            assert math.isfinite(point[field]) and point[field]>=0,'Invalid aligned CPU counter'
        for field in ['docker_seconds','cgroup_seconds']:
            for value in point['bounds'][field]:assert abs(point['cadvisor_seconds']-mc.finite(value,field))<=tolerance(value),'Aligned cumulative CPU mismatch'
        if previous:
            old=previous['cpu_alignment'][cid]
            assert old['started_at']==point['started_at'],'CPU generation changed'
            dt=point['time']-old['time'];assert dt>=0,'CPU timestamp moved backwards'
            if dt==0:
                for field in ['cadvisor_seconds','docker_seconds','cgroup_seconds','bounds']:assert point[field]==old[field],'Same timestamp changed CPU value'
                continue
            deltas={k:point[k]-old[k] for k in ['cadvisor_seconds','docker_seconds','cgroup_seconds']}
            assert all(v>=0 for v in deltas.values()),'CPU counter reset'
            for field in ['docker_seconds','cgroup_seconds']:
                low=point['bounds'][field][0]-old['bounds'][field][1]
                high=point['bounds'][field][1]-old['bounds'][field][0]
                for value in [low,high]:assert abs(deltas['cadvisor_seconds']-value)<=tolerance(value),'Aligned CPU window mismatch'

class DockerCPU(http.client.HTTPConnection):
    def connect(self):
        self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        self.sock.settimeout(5);self.sock.connect('/var/run/docker.sock')

def docker_get(path,allow_missing=False):
    conn=DockerCPU('localhost')
    try:
        conn.request('GET',path);r=conn.getresponse()
        if allow_missing and r.status==404:return None
        assert r.status==200
        return json.loads(r.read())
    finally:conn.close()

def container_cpu_path(container,cid):
    if not container or not container['State']['Running'] or container['State']['Pid']<=0:return None
    try:text=Path('/proc/'+str(container['State']['Pid'])+'/cgroup').read_text()
    except FileNotFoundError:return None  # Process exited between inspect and proc read.
    path=next(line.split('::',1)[1] for line in text.splitlines() if line.startswith('0::'))
    assert '..' not in Path(path).parts
    cg=Path('/sys/fs/cgroup')/path.lstrip('/')/'cpu.stat'
    assert mc.exact_id(str(cg.parent),cid),'Cgroup identity mismatch'
    return cg

def collect_cpu(directory,names,seconds=7200):
    directory=Path(directory)
    destination=directory/'cpu-history.jsonl'
    assert not destination.exists(),'Never replace a CPU history'
    start=time.monotonic();cache={};last_refresh=0
    with destination.open('x') as out:
        destination.chmod(0o600)
        while time.monotonic()-start<seconds:
            tick=time.monotonic()
            if tick-last_refresh>=.5:
                active=docker_get('/containers/json')
                cache={}
                for item in active:
                    if not any(n.lstrip('/') in names for n in item['Names']):continue
                    c=docker_get('/containers/'+item['Id']+'/json',allow_missing=True)
                    cg=container_cpu_path(c,item['Id'])
                    if cg is None:continue
                    cache[item['Id']]=(c['Name'].lstrip('/'),c['State']['StartedAt'],cg)
                last_refresh=tick
            for cid,(name,generation,cg) in cache.items():
                try:
                    point=mc.capture(cg.parent,lambda:docker_get('/containers/'+cid+'/stats?stream=false&one-shot=true'),cid,name,generation)['cpu']
                    out.write(json.dumps(point)+'\n')
                    out.flush()
                except (OSError,AssertionError) as exc:
                    # An identity transition is recorded; readers fail closed on history gaps.
                    with (directory/'cpu-history-errors.jsonl').open('a') as errors:errors.write(json.dumps({'time':time.time(),'id':cid,'type':type(exc).__name__,'message':str(exc)})+'\n')
            time.sleep(max(.01,.5-(time.monotonic()-tick)))

if __name__=='__main__':
    import argparse,os
    os.umask(0o077)
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',required=True);p.add_argument('--names',nargs='+',required=True);p.add_argument('--seconds',type=int,default=7200);a=p.parse_args()
    collect_cpu(a.directory,a.names,a.seconds)

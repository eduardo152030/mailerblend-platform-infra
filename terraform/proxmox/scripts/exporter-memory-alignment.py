"""RAM gauge validation at cAdvisor's timestamp. No interpolation or widened tolerances."""
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


def allowance(value, name):
    mc.finite(value,'RAM reference')
    return max(mc.LIMITS['ram_exporter_floor_bytes'],value*mc.LIMITS['ram_exporter_fraction']) if name in ('node_exporter','cadvisor') else max(mc.LIMITS['ram_app_floor_bytes'],value*mc.LIMITS['ram_app_fraction'])


def bracket(history, when, max_gap=2):
    assert max_gap==mc.LIMITS['history_gap_seconds'],'RAM gap policy cannot be widened'
    pair=mc.bracket(history,when)
    for p in pair:
        assert p['request_before']<=p['time']<=p['request_after'],'RAM Docker timestamp outside request'
        assert 0<=p['request_after']-p['request_before']<=.5,'RAM request too slow'
        for key in ['docker_bytes','cgroup_before','cgroup_after']:
            assert math.isfinite(p[key]) and p[key]>=0,'Invalid RAM gauge'
        for value in [p['cgroup_before'],p['cgroup_after']]:
            assert abs(p['docker_bytes']-value)<=max(8*1024**2,value*.25),'Docker/cgroup RAM mismatch'
    return pair


def aligned_evidence(sample,history):
    result={}
    for cid,c in mc.active(sample).items():
        name=c['name']
        row=mc.metric(sample,'container_memory_usage_bytes',c);when=row['timestamp']
        assert -5<=time.time()-when<=90,'RAM metric stale: '+name
        assert math.isfinite(row['value']) and row['value']>=0,'Invalid cAdvisor RAM gauge'
        current=mc.points(history,c,['docker_bytes','cgroup_before','cgroup_after'])
        assert all(p['name']==name for p in current),'RAM history name changed'
        pair=bracket(current,when)
        # RAM is non-monotonic: compare BOTH endpoints, never interpolate/choose a convenient one.
        for point in pair:
            for field in ['docker_bytes','cgroup_before','cgroup_after']:
                assert abs(row['value']-point[field])<=allowance(point[field],name),'Aligned cAdvisor RAM mismatch or volatile bracket: '+name
        result[cid]={'name':name,'started_at':c['started_at'],'time':when,'cadvisor_bytes':row['value'],'bracket':pair}
    return result


def require_collector(path):
    mc.require_collector(path,'memory-alignment.py')


def history_for_sample(sample,path):
    deadline=time.monotonic()+2
    while True:
        active=mc.active(sample);metrics=[mc.metric(sample,'container_memory_usage_bytes',c) for c in active.values()]
        metric_times=[r['timestamp'] for r in metrics]
        history=mc.read_history(path,min(metric_times)-2,max(metric_times)+2)
        ready=True
        for c in sample['containers']:
            if not c['running']:continue
            row=mc.metric(sample,'container_memory_usage_bytes',c)
            ts=[p['time'] for p in history if p['id']==c['id'] and p['started_at']==c['started_at']]
            if not ts or not min(ts)<row['timestamp']<max(ts):ready=False
        if ready:return history
        assert time.monotonic()<deadline,'RAM timeline does not bracket metric timestamp'
        time.sleep(.1)


def validate_alignment(sample,previous=None):
    active=mc.active(sample)
    evidence=sample.get('memory_alignment')
    assert evidence and set(evidence)==set(active),'Aligned RAM evidence required for every running container'
    history=[]
    for cid,p in evidence.items():
        assert p['name']==active[cid]['name'] and p['started_at']==active[cid]['started_at'],'RAM generation mismatch'
        history.extend(p['bracket'])
        if previous:
            old=previous['memory_alignment'][cid]
            assert old['started_at']==p['started_at'] and p['time']>=old['time'],'RAM generation/timestamp changed'
            if p['time']==old['time']:assert p==old,'Same timestamp changed RAM evidence'
    assert aligned_evidence(sample,history)==evidence,'RAM evidence not reproducible from raw bracket'


class IdentityTransition(RuntimeError):
    pass


class Docker(http.client.HTTPConnection):
    def connect(self):
        self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(5);self.sock.connect('/var/run/docker.sock')


def api(path):
    conn=Docker('localhost')
    try:
        conn.request('GET',path);r=conn.getresponse()
        if r.status==404:raise IdentityTransition('Container disappeared during RAM read')
        assert r.status==200
        return json.loads(r.read())
    finally:conn.close()


STAT_KEYS={'anon','file','shmem','inactive_file','active_file','kernel','slab_reclaimable','slab_unreclaimable'}

def read_stat(cg):
    return {k:int(v) for k,v in (l.split() for l in (cg/'memory.stat').read_text().splitlines()) if k in STAT_KEYS}


def collect_once(names, allow_transition=False):
    points=[]
    for item in api('/containers/json'):
        name=next((n.lstrip('/') for n in item['Names'] if n.lstrip('/') in names),None)
        if not name:continue
        c=api('/containers/'+item['Id']+'/json');cid=c['Id']
        if not c['State']['Running'] or c['State']['Pid']<=0:raise IdentityTransition('RAM identity transition')
        path=next(l.split('::',1)[1] for l in Path('/proc/'+str(c['State']['Pid'])+'/cgroup').read_text().splitlines() if l.startswith('0::'))
        assert '..' not in Path(path).parts and mc.exact_id(path,cid),'RAM cgroup identity mismatch'
        cg=Path('/sys/fs/cgroup')/path.lstrip('/')
        point=mc.capture(cg,lambda:api('/containers/'+cid+'/stats?stream=false&one-shot=true'),cid,name,c['State']['StartedAt'])['memory']
        assert point['request_before']<=point['time']<=point['request_after'],'RAM request timestamp invalid'
        points.append(point)
    if not allow_transition:assert {p['name'] for p in points}==set(names),'RAM active inventory drift'
    return points


def main():
    import argparse,os
    os.umask(0o077)
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,required=True);p.add_argument('--names',nargs='+',required=True);p.add_argument('--seconds',type=int,default=2700);p.add_argument('--interval',type=float,default=.5);a=p.parse_args()
    assert 1<=a.seconds<=2700 and .05<=a.interval<=.5
    with (a.directory/'memory-history.jsonl').open('x') as out:
        end=time.monotonic()+a.seconds
        while time.monotonic()<end:
            tick=time.monotonic()
            # Planned stop/start can remove a PID. Record gaps; readers still require exact generation.
            # All accounting/latency failures remain fatal; no fallback or fabricated values.
            try:
                for point in collect_once(a.names,allow_transition=True):out.write(json.dumps(point)+'\n')
            except (IdentityTransition,FileNotFoundError) as exc:
                with (a.directory/'memory-history-errors.jsonl').open('a') as errors:errors.write(json.dumps({'time':time.time(),'type':type(exc).__name__,'message':'Container/process transition; no RAM sample fabricated'})+'\n')
            out.flush();time.sleep(max(.01,a.interval-(time.monotonic()-tick)))

if __name__=='__main__':main()

"""Authoritative CPU/RAM measurement contract. Pure helpers; no production mutations."""
import bisect
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re

if not __debug__:raise RuntimeError('Validation cannot run with Python assertions disabled')

SCHEMA=1
LIMITS={'metric_age_seconds':90,'future_seconds':5,'history_gap_seconds':2,'request_seconds':.5,'cpu_floor_seconds':1.,'cpu_fraction':.03,'ram_app_floor_bytes':512*1024,'ram_app_fraction':.20,'ram_exporter_floor_bytes':4*1024**2,'ram_exporter_fraction':.30,'docker_cgroup_floor_bytes':8*1024**2,'docker_cgroup_fraction':.25}


def finite(value, label='measurement', nonnegative=True):
    assert isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value),label+' missing/non-numeric/non-finite'
    assert not nonnegative or value>=0,label+' negative'
    return value


def timestamp(text):
    if not isinstance(text,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?(?:Z|[+-]\d{2}:\d{2})',text):raise ValueError('Timestamp must be RFC3339 with timezone')
    normalized=re.sub(r'\.(\d+)',lambda m:'.'+m.group(1)[:6].ljust(6,'0'),text)
    return finite(datetime.fromisoformat(normalized.replace('Z','+00:00')).timestamp(),'timestamp')


def exact_id(path,cid):
    assert isinstance(cid,str) and re.fullmatch(r'[a-f0-9]{64}',cid),'Full Docker ID required'
    if not isinstance(path,str):return False
    parts=path.strip('/').split('/')
    return '..' not in parts and parts[-1] in [cid,'docker-'+cid+'.scope']


def scope():
    import socket
    return socket.gethostname()+'|'+str(Path('/proc/self/ns/cgroup').readlink())


def active(sample):
    result={}
    for c in sample['containers']:
        if not c['running']:continue
        cid=c['id'];assert exact_id(cid,cid)
        assert cid not in result and c['name'] not in {x['name'] for x in result.values()},'Duplicate active Docker identity/name'
        assert isinstance(c.get('started_at'),str) and c['started_at'] and isinstance(c.get('name'),str) and c['name'],'Container generation/name required'
        assert sample.get('measurement_scope'),'Measurement scope required; legacy replay must declare its source provenance'
        assert sample.get('measurement_contract_schema',SCHEMA)==SCHEMA,'Unknown measurement contract schema'
        result[cid]=dict(c,_scope=sample['measurement_scope'])
    assert result,'Active Docker inventory missing'
    return result


def metric(sample,key,c):
    rows=[r for r in sample['cadvisor'].get(key,[]) if r['labels'].get('name','').lstrip('/')==c['name'] and exact_id(r['labels'].get('id',''),c['id']) and (key!='container_cpu_usage_seconds_total' or r['labels'].get('cpu','total')=='total')]
    assert len(rows)==1,'Missing/duplicate metric identity: '+key+' '+c['name']
    row=rows[0];finite(row.get('value'),key);finite(row.get('timestamp'),key+' timestamp')
    return row


def fresh(when,observed):
    finite(when,'metric timestamp');finite(observed,'observed time')
    assert -LIMITS['future_seconds']<=observed-when<=LIMITS['metric_age_seconds'],'Metric timestamp stale/future: metric_time='+str(when)+' observed_time='+str(observed)+' age_seconds='+str(observed-when)


def points(history,c,fields):
    selected=[p for p in history if p.get('id')==c['id'] and p.get('started_at')==c['started_at']]
    if c.get('_scope'):
        assert selected and all(p.get('measurement_scope')==c['_scope'] for p in selected),'Cross-LXC/engine measurement scope mismatch'
    assert len(selected)>=2,'Measured history missing for current container generation'
    last=None
    for p in selected:
        finite(p.get('time'),'history time')
        assert last is None or p['time']>last,'Duplicate or backwards history timestamp'
        last=p['time']
        if 'name' in p:assert p['name']==c['name'],'History container name changed'
        for field in fields:finite(p.get(field),field)
    return selected


def bracket(points,when):
    finite(when,'metric timestamp');assert len(points)>=2,'Measured history missing'
    times=[finite(p.get('time'),'history time') for p in points]
    assert all(b>a for a,b in zip(times,times[1:])),'Duplicate or backwards history timestamp'
    i=bisect.bisect_left(times,when)
    assert 0<i<len(points),'Metric timestamp outside measured history'
    pair=points[i-1:i+1]
    assert 0<pair[1]['time']-pair[0]['time']<=LIMITS['history_gap_seconds'],'History gap >2s'
    return pair


def cpu_seconds(value,unit):
    finite(value,'CPU counter');assert unit in ['ns','us','seconds'],'Unknown CPU unit'
    return value/{'ns':1e9,'us':1e6,'seconds':1}[unit]


def memory_views(usage,stats):
    finite(usage,'memory usage');inactive=finite(stats.get('inactive_file'),'inactive_file');file=finite(stats.get('file'),'file');shmem=finite(stats.get('shmem'),'shmem')
    assert shmem<=file,'Shared memory is part of file, not an additional charge'
    # These views have different meanings. Only raw usage is compared across API/cgroup/cAdvisor usage.
    return {'usage_bytes':usage,'working_set_bytes':max(0,usage-inactive),'docker_cli_bytes':usage-inactive if inactive<usage else usage,'proxmox_net_bytes':usage-file,'file_bytes':file,'shmem_included_in_file_bytes':shmem}


def read_history(path,earliest,latest):
    finite(earliest,'history lower bound',False);finite(latest,'history upper bound');out=[]
    with Path(path).open() as stream:
        for line in stream:
            if not line.endswith('\n'):continue # Writer's final partial append only; never ignore malformed complete records.
            p=json.loads(line);finite(p.get('time'),'history time')
            if earliest<=p['time']<=latest:out.append(p)
    return out


PROM_LABELS={'name','id','image','cpu','mode','fstype','mountpoint','container_label_com_docker_compose_project','container_label_com_docker_compose_service','version','cadvisorVersion','dockerVersion','kernelVersion','osVersion','ct_id','resource_scope','cpu_source'}

def prom_rows(text,key):
    result=[]
    for line in text.splitlines():
        if not line.startswith(key+'{') and not line.startswith(key+' '):continue
        tail=line[line.rfind('}')+1:] if line.startswith(key+'{') else line[len(key):]
        fields=tail.split();assert 1<=len(fields)<=2,'Malformed metric sample: '+key
        value=finite(float(fields[0]),key)
        when=finite(float(fields[1]),key+' milliseconds')/1000 if len(fields)==2 else None
        labels={k:json.loads('"'+v+'"') for k,v in re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)="((?:\\.|[^"\\])*)"',line[:line.rfind('}')+1])}
        result.append({'labels':{k:v for k,v in labels.items() if k in PROM_LABELS},'value':value,'timestamp':when})
    return result

def require_collector(history_path,script):
    path=Path(history_path);marker=path.with_name(path.stem+'-process.json')
    pid=json.loads(marker.read_text()).get('pid')
    assert isinstance(pid,int) and not isinstance(pid,bool) and pid>0,'Invalid collector PID'
    try:args=(Path('/proc')/str(pid)/'cmdline').read_bytes().split(bytes([0]))
    except FileNotFoundError:raise AssertionError('Framework collector not running: '+script)
    assert str(path.with_name(script)).encode() in args,'Framework collector stopped or PID identity changed: '+script


STAT_KEYS={'anon','file','shmem','inactive_file','active_file','kernel','slab_reclaimable','slab_unreclaimable'}

def capture(cg,read_stats,cid,name,started_at):
    assert exact_id(str(cg),cid),'Cgroup identity mismatch'
    def cpu():return cpu_seconds(int(dict(l.split() for l in (cg/'cpu.stat').read_text().splitlines())['usage_usec']),'us')
    def mem():return finite(int((cg/'memory.current').read_text()),'cgroup RAM')
    def stat():
        values={k:int(v) for k,v in (l.split() for l in (cg/'memory.stat').read_text().splitlines()) if k in STAT_KEYS}
        for k,v in values.items():finite(v,'memory.stat '+k)
        assert {'anon','file','shmem','inactive_file'}<=set(values),'Missing memory.stat accounting fields'
        return values
    import time
    before=time.time();c0=cpu();m0=mem();s0=stat();data=read_stats();c1=cpu();m1=mem();s1=stat();after=time.time()
    assert data.get('id')==cid,'Docker response ID mismatch'
    assert data.get('name','').lstrip('/')==name,'Docker response name changed'
    when=timestamp(data['read']);docker_cpu=cpu_seconds(data['cpu_stats']['cpu_usage']['total_usage'],'ns');docker_mem=finite(data['memory_stats'].get('usage'),'Docker RAM')
    assert 0<=after-before<=LIMITS['request_seconds'],'Sampling request too slow'
    assert before-.01<=when<=after+.01,'Docker timestamp outside measured request'
    assert c0<=c1 and c0-max(1,c0*.03)<=docker_cpu<=c1+max(1,c1*.03),'Docker/cgroup CPU mismatch'
    common={'id':cid,'name':name,'started_at':started_at,'time':when,'request_before':before,'request_after':after,'measurement_scope':scope()}
    return {'cpu':dict(common,docker_seconds=docker_cpu,cgroup_seconds=(c0+c1)/2,cgroup_before=c0,cgroup_after=c1),
            'memory':dict(common,docker_bytes=docker_mem,cgroup_before=m0,cgroup_after=m1,stat_before=s0,stat_after=s1,docker_stat={k:v for k,v in data['memory_stats'].get('stats',{}).items() if k in STAT_KEYS})}


def render_alignment_source(kind):
    assert kind in ['cpu','memory']
    common=Path(__file__).read_text().split('\ndef render_alignment_source(')[0]
    body=Path(__file__).with_name('exporter-'+kind+'-alignment.py').read_text()
    start=body.index('# BEGIN METRIC CONTRACT LOADER');end=body.index('# END METRIC CONTRACT LOADER',start)+len('# END METRIC CONTRACT LOADER')
    inline="import types\n_contract_ns={'__name__':'metric_contract'}\nexec("+repr(common)+",_contract_ns)\nmc=types.SimpleNamespace(**_contract_ns)"
    return body[:start]+inline+body[end:]

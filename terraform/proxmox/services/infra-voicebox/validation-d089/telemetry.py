"""Durable numeric-only memory events; never serialize user inputs or tensor values."""
from pathlib import Path
import json,os,time,resource

def pairs(path):
    try:return {k:int(v) for k,v in (line.split() for line in Path(path).read_text().splitlines())}
    except (OSError,ValueError):return {}

def snapshot(cgroup=Path('/sys/fs/cgroup')):
    result={}
    for name in ['memory.current','memory.peak','memory.swap.current','memory.high','memory.max']:
        try:
            value=(cgroup/name).read_text().strip();result[name]=int(value) if value!='max' else 'max'
        except OSError:result[name]=None
    stat=pairs(cgroup/'memory.stat');result['memory.stat']={k:stat.get(k) for k in ['anon','file','kernel','file_mapped','file_dirty','inactive_file','active_file']}
    result['memory.events']=pairs(cgroup/'memory.events')
    try:result['memory.pressure']=(cgroup/'memory.pressure').read_text()
    except OSError:result['memory.pressure']=None
    try:
        lines=Path('/proc/self/status').read_text().splitlines();fields={l.split(':')[0]:l.split(':',1)[1].strip() for l in lines if ':' in l}
        for k in ['VmRSS','VmHWM']:result[k+'_bytes']=int(fields[k].split()[0])*1024
    except OSError:pass
    try:
        fields={l.split(':')[0]:l.split(':',1)[1].strip() for l in Path('/proc/self/smaps_rollup').read_text().splitlines() if ':' in l}
        result['Pss_bytes']=int(fields['Pss'].split()[0])*1024
    except (OSError,KeyError):result['Pss_bytes']=None
    result['rusage_hwm_bytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
    return result

class Events:
    def __init__(self,path,tensors=lambda:{}):
        self.path=Path(path);self.start=time.monotonic();self.tensors=tensors
    def emit(self,phase,**metrics):
        # Only call with fixed phase names and aggregate numeric/boolean metadata.
        row={'phase':phase,'elapsed_seconds':time.monotonic()-self.start,'memory':snapshot(),'tracked_tensors':self.tensors(),**metrics}
        data=(json.dumps(row,sort_keys=True)+'\n').encode()
        fd=os.open(self.path,os.O_WRONLY|os.O_APPEND|os.O_CREAT,0o600)
        try:
            pos=0
            while pos<len(data):pos+=os.write(fd,data[pos:])
            os.fsync(fd)
        finally:os.close(fd)
        return row

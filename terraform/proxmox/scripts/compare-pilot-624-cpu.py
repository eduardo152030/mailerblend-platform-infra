#!/usr/bin/env python3
"""Read-only CPU source contrast on PVE, exclusively CT 624. No load is generated."""
import json
from pathlib import Path
import re
import time
import urllib.request

ROOT=Path('/sys/fs/cgroup/lxc/624')
MODES=['user','nice','system','idle','iowait','irq','softirq','steal']


def host():
    cpus=[int(x) for x in ROOT.joinpath('cpuset.cpus.effective').read_text().strip().split(',')]
    assert len(cpus)==1
    line=next(l for l in Path('/proc/stat').read_text().splitlines() if l.startswith('cpu'+str(cpus[0])+' '))
    return dict(zip(MODES,[int(n)/100 for n in line.split()[1:9]]))


def take():
    before=host()
    with urllib.request.urlopen('http://192.168.1.124:9100/metrics',timeout=10) as r:text=r.read().decode()
    values={m.group(1):float(m.group(2)) for m in re.finditer(r'^node_cpu_seconds_total\{[^\n]*mode="([^"\n]+)"[^\n]*\} ([^\s]+)',text,re.M)}
    after=host()
    cgroup={k:int(v) for k,v in (l.split() for l in ROOT.joinpath('cpu.stat').read_text().splitlines())}
    total=re.search(r'^lxc_cpu_usage_seconds_total(?:\{[^}]*\})? (\S+)',text,re.M)
    return {'time':time.time(),'node_lxc_cpu_total':float(total.group(1)) if total else None,'node_cpu_seconds':values,'pve_assigned_core_before':before,'pve_assigned_core_after':after,
        'node_matches_physical_core':all(before[k]-.03<=values[k]<=after[k]+.03 for k in MODES) if values else None,
        'cgroup_usage_seconds':cgroup['usage_usec']/1e6}


if __name__=='__main__':
    assert ROOT.is_dir() and Path('/etc/pve/lxc/624.conf').is_file()
    first=take();time.sleep(20);last=take()
    busy=lambda row:row['node_lxc_cpu_total'] if row['node_lxc_cpu_total'] is not None else sum(row['node_cpu_seconds'][k] for k in ['user','nice','system','irq','softirq','steal'])
    result={'ct':624,'mode':'read-only, no synthetic load','metric_source':'cgroup_v2_textfile' if first['node_lxc_cpu_total'] is not None else 'native_cpu_collector','first':first,'last':last,
        'elapsed_seconds':last['time']-first['time'],'node_busy_delta_seconds':busy(last)-busy(first),
        'lxc_cgroup_usage_delta_seconds':last['cgroup_usage_seconds']-first['cgroup_usage_seconds']}
    print(json.dumps(result,indent=2))

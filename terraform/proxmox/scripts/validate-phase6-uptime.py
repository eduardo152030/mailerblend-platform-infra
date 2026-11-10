#!/usr/bin/env python3
"""Read-only PVE vs Prometheus uptime evidence; reject shared host boot values."""
import importlib.util,json,subprocess,shlex,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('a',ROOT/'scripts/audit-fleet-application-health.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
code=r'''import subprocess,json,time,pathlib
rows=json.loads(subprocess.check_output(['pvesh','get','/nodes/pve/lxc','--output-format','json']))
print(json.dumps({'time':time.time(),'host_uptime':float(pathlib.Path('/proc/uptime').read_text().split()[0]),'ct':{str(r['vmid']):{'name':r['name'],'uptime':r['uptime']} for r in rows}}))'''
r=subprocess.run(['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve',shlex.join(['python3','-c',code])],capture_output=True,timeout=30);assert r.returncode==0
pve=json.loads(r.stdout);boots=a.query('node_boot_time_seconds{job="node_exporter"}');clock=a.query('node_time_seconds{job="node_exporter"}');rows=[]
for b in boots:
 ct=b['metric']['vmid'];inferred=float(b['value'][0])-float(b['value'][1]);truth=pve['ct'][ct]['uptime'];rows.append({'ct':ct,'service':b['metric']['service'],'pve_lxc_uptime_seconds':truth,'node_inferred_uptime_seconds':inferred,'difference_seconds':inferred-truth,'difference_vs_host_seconds':inferred-pve['host_uptime'],'boot_metric_rejected':True})
assert len(rows)==17 and max(abs(r['difference_vs_host_seconds']) for r in rows)<10
assert abs(next(x for x in rows if x['ct']=='618')['difference_seconds'])>86400
result={'timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'source':'PVE API and current Prometheus','host_uptime':pve['host_uptime'],'comparisons':rows,'node_time_is_wall_clock':len(clock)==17,'node_boot_host_scoped_all_17':True,'existing_lxc_or_pve_uptime_metrics':a.query('count by(__name__)({__name__=~"(lxc|pve)_.*(boot|uptime).*"})'),'decision':'Uptime UNKNOWN; no verified LXC boot source; no Docker/exporter surrogate'}
(ROOT/'docs/roadmap/evidence/2026-11-07-d054-uptime.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS: 17 comparisons with PVE; shared host boot rejected; no reliable published LXC uptime')

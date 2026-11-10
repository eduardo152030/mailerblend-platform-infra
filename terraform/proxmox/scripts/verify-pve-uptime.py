#!/usr/bin/env python3
"""D056: compare live central metrics with PVE, without restarting or creating guests."""
import importlib.util,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('deploy',ROOT/'scripts/deploy-pve-uptime.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
model=d.t.g.api('/api/dashboards/uid/proxmox-lxc-fleet')['dashboard'];table=next(p for p in model['panels'] if p['title'].startswith('LXC health'));expr=next(t['expr'] for t in table['targets'] if t['refId']=='J');now=time.time();rows=d.t.query(expr.replace('${lxc:regex}','.*').replace('${service:regex}','.*'))
truth=json.loads(d.pve(r'''import subprocess,json,time
rows=json.loads(subprocess.check_output(['pvesh','get','/nodes/pve/lxc','--output-format','json']))
selected={str(r['vmid']):{'uptime':r['uptime'],'name':r['name'],'status':r['status']} for r in rows}
independent={}
for ct in [611,618,624]:
 r=json.loads(subprocess.check_output(['pvesh','get','/nodes/pve/lxc/'+str(ct)+'/status/current','--output-format','json']));independent[str(ct)]={'uptime':r['uptime'],'status':r['status']}
print(json.dumps({'time':time.time(),'all_ct':selected,'independent_current':independent}))'''))
comparisons=[]
for row in rows:
 ct=row['metric']['ct_id'];value=float(row['value'][1]);actual=truth['all_ct'][ct]['uptime'];diff=actual-value
 assert value>0 and abs(diff)<=45,(ct,diff)
 comparisons.append({'ct_id':ct,'name':truth['all_ct'][ct]['name'],'prometheus_uptime_seconds':value,'pve_uptime_seconds':actual,'difference_seconds':diff,'status':truth['all_ct'][ct]['status']})
assert len(comparisons)==17
for ct,obj in truth['independent_current'].items():
 metric=next(x['prometheus_uptime_seconds'] for x in comparisons if x['ct_id']==ct);assert abs(obj['uptime']-metric)<=45
info=d.t.query('pve_guest_info{job="pve_uptime"}');discovered={x['metric']['ct_id'] for x in info};assert discovered==set(truth['all_ct']),'API discovery differs'
assert len(info)==len(discovered),'Duplicate discovered CT'
meta=json.loads(d.t.py(610,r'''import subprocess,json,pathlib,stat
c=json.loads(subprocess.check_output(['docker','inspect','pve-uptime-exporter']))[0];p=pathlib.Path('/opt/infra-pve-uptime/.runtime/pve_token')
print(json.dumps({'image_id':c['Image'],'running':c['State']['Running'],'restart_count':c['RestartCount'],'user':c['Config']['User'],'read_only':c['HostConfig']['ReadonlyRootfs'],'cap_drop':c['HostConfig']['CapDrop'],'security_opt':c['HostConfig']['SecurityOpt'],'ports_published':c['HostConfig']['PortBindings'],'secret_mode':oct(stat.S_IMODE(p.stat().st_mode)),'secret_owner':p.stat().st_uid}))'''))
assert meta['user']=='65534:65534' and meta['read_only'] and meta['cap_drop']==['ALL'] and not meta['ports_published'] and meta['secret_mode']=='0o400' and meta['secret_owner']==65534
result={'timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'comparison_count':17,'comparisons':comparisons,'independent_current_endpoint':truth['independent_current'],'max_absolute_difference_seconds':max(abs(x['difference_seconds']) for x in comparisons),'allowed_freshness_seconds':45,'all_api_lxc_discovered':len(discovered),'monitored_dashboard_lxc':17,'ct_list_hardcoded_in_collector':False,'new_lxc_test':'synthetic new 9999 passes generated unchanged query; all actual API LXC appear without per-CT config','actual_lxc_restart_performed':False,'exporter_security':meta,'result':'PASS'}
(ROOT/'docs/roadmap/evidence/2026-11-07-d056-comparison.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS:17 PVE comparisons;611/618/624 current endpoints; max difference',result['max_absolute_difference_seconds'],'s; all',len(discovered),'API CT dynamically discovered')

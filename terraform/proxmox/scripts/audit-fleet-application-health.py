#!/usr/bin/env python3
"""Read-only production audit of Fleet Application Health UNKNOWN; local evidence only."""
import importlib.util,json,shlex,subprocess,time,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/roadmap/evidence/2026-11-07-d053-audit.json'
def remote(ct,code):
 r=subprocess.run(['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve',shlex.join(['pct','exec',str(ct),'--','python3','-c',code])],capture_output=True,timeout=45)
 assert r.returncode==0,f'Read failed CT{ct}; output withheld'
 return json.loads(r.stdout)
def query(q):
 with urllib.request.urlopen(urllib.request.Request('http://192.168.1.110:9090/api/v1/query',data=urllib.parse.urlencode({'query':q}).encode()),timeout=20) as r:return json.load(r)['data']['result']
INNER=r'''
import subprocess,json,pathlib,re
ids=subprocess.check_output(['docker','ps','-q'],text=True).split()
cs=json.loads(subprocess.check_output(['docker','inspect']+ids,text=True)) if ids else []
rows=[]
for c in cs:
 hc=c['Config'].get('Healthcheck',{});test=' '.join(hc.get('Test',[]))
 # Never export raw check commands, output logs, container env, or application config.
 mechanisms=[x for x in ['pg_isready','redis-cli','curl','wget','http.client','urllib','health_checker_bin.js','/api/v2/ping','/api/_health','/api/health','/health','/ready','rabbitmq-diagnostics'] if x in test]
 rows.append({'name':c['Name'].lstrip('/'),'id':c['Id'],'image':c['Config']['Image'],'started_at':c['State']['StartedAt'],'restart_count':c['RestartCount'],'status':c['State']['Status'],'health':c['State'].get('Health',{}).get('Status','not_configured'),'healthcheck_configured':bool(hc and hc.get('Test',['NONE'])[0]!='NONE'),'healthcheck_mechanisms':mechanisms,'healthcheck_interval_ns':hc.get('Interval'),'ports':c['NetworkSettings'].get('Ports',{}),'compose_service':c['Config'].get('Labels',{}).get('com.docker.compose.service'),'compose_files':c['Config'].get('Labels',{}).get('com.docker.compose.project.config_files'),'mount_destinations':[m['Destination'] for m in c['Mounts']]})
r=subprocess.run(['systemctl','list-units','--type=service','--state=running','--no-pager','--no-legend','--plain'],capture_output=True,text=True)
units=[l.split()[0] for l in r.stdout.splitlines() if l.strip()]
r=subprocess.run(['ss','-lntpH'],capture_output=True,text=True)
listeners=[]
for l in r.stdout.splitlines():
 a=l.split()
 if len(a)>=4:listeners.append({'address':a[3],'processes':re.findall(r'\(\("([^" ]+)"',l)})
print(json.dumps({'boot_id':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'containers':rows,'running_systemd_units':units,'tcp_listeners':listeners}))
'''
def hashes(ct,base):
 return remote(ct,f'import pathlib,hashlib,json;p=pathlib.Path({base!r});print(json.dumps({{str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.glob("config/**/*") if f.is_file()}}))')
def main():
 spec=importlib.util.spec_from_file_location('fleetdeploy',ROOT/'scripts/deploy-fleet-dashboard.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
 dashboard=g.api('/api/dashboards/uid/proxmox-lxc-fleet')['dashboard']
 table=next(p for p in dashboard['panels'] if p['title'].startswith('LXC health'))
 expr=next(t['expr'] for t in table['targets'] if t['refId']=='D').replace('${lxc:regex}','.*').replace('${service:regex}','.*')
 rows=query(expr);unknown=[r['metric']['ct_id'] for r in rows if float(r['value'][1])==-1]
 inventory=query('lxc:cpu_inventory:expected');names={r['metric']['ct_id']:r['metric']['service'] for r in inventory}
 d={'timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'mode':'read-only','unknown_cts':sorted(unknown,key=int),'dashboard_application_query':expr,'application_values':rows,'before_config_hashes':{'610':hashes(610,'/opt/infra-prom'),'611':hashes(611,'/opt/infra-grafana')},'prometheus':{},'ct':{}}
 for key,q in {'health':'container_health_state{job="cadvisor",name!=""}','last_seen':'container_last_seen{job="cadvisor",name!=""}','probes':'probe_success{job="blackbox"}','up':'up','expected_app_containers':'app:container:expected','health_metric_names':'count by(__name__)({__name__=~".*(health|ready|success).*"})'}.items():
  data=query(q)
  # Probe URLs may contain event identifiers/query data: retain only scheme, host, port and path.
  for row in data:
   for k,v in list(row['metric'].items()):
    if isinstance(v,str) and '://' in v:
     u=urllib.parse.urlsplit(v);row['metric'][k]=urllib.parse.urlunsplit((u.scheme,u.netloc,u.path,'',''))
  d['prometheus'][key]=data
 for ct in sorted(unknown,key=int):
  d['ct'][ct]={'service':names[ct],'before':remote(ct,INNER)}
  OUT.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n');print('Read CT'+ct+' '+names[ct],flush=True)
 d['after_config_hashes']={'610':hashes(610,'/opt/infra-prom'),'611':hashes(611,'/opt/infra-grafana')}
 assert d['before_config_hashes']==d['after_config_hashes'],'Configuration changed during audit'
 for ct in d['ct']:
  after=remote(ct,INNER);before=d['ct'][ct]['before'];assert before['boot_id']==after['boot_id']
  def identities(x):return sorted((c['id'],c['started_at'],c['restart_count']) for c in x['containers'])
  assert identities(before)==identities(after),f'Container drift CT{ct}'
 d['identity_and_configuration_unchanged']=True
 OUT.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n');print('PASS read-only audit; identities/configurations unchanged')
if __name__=='__main__':main()

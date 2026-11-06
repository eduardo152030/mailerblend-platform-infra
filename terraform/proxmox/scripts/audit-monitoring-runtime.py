#!/usr/bin/env python3
import subprocess,json,argparse,re
from pathlib import Path
import yaml
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description='Read-only Proxmox/CT exporter audit; never deploys, restarts or writes remote files.')
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--ssh-alias',default='pve')
args=parser.parse_args()
if not re.fullmatch(r'[a-zA-Z0-9_.-]+',args.ssh_alias):parser.error('Invalid SSH alias')
services=[yaml.safe_load(p.read_text())['service'] for p in sorted((ROOT/'inventory/services').glob('*.yml'))]
collector=r'''
import json,subprocess,re,pathlib,urllib.request,time,sys
r={}
address=sys.argv[1]
def run(args):
 x=subprocess.run(args,capture_output=True,text=True,timeout=12)
 return x.stdout if x.returncode==0 else ''
r['proc_memory_kib']=int(re.search(r'MemTotal:\s+(\d+)',pathlib.Path('/proc/meminfo').read_text()).group(1))
r['proc_cpu_count']=len(re.findall(r'^cpu\d+ ',pathlib.Path('/proc/stat').read_text(),re.M))
r['cgroup2']=pathlib.Path('/sys/fs/cgroup/cgroup.controllers').exists()
for name in ['memory.max','memory.current','memory.swap.current','cpu.max','cpuset.cpus.effective','memory.events','memory.pressure']:
 p=pathlib.Path('/sys/fs/cgroup')/name
 if p.exists():r[name]=p.read_text().strip()
r['proc_mounts']=[{'target':x.split()[1],'filesystem':x.split()[2]} for x in pathlib.Path('/proc/mounts').read_text().splitlines() if x.split()[1] in ['/proc/meminfo','/proc/stat','/proc/cpuinfo','/sys/fs/cgroup']]
ids=run(['docker','ps','-aq']).split()
r['docker_available']=bool(run(['docker','version','--format','{{.Server.Version}}']).strip())
r['docker_version']=run(['docker','version','--format','{{.Server.Version}}']).strip()
r['docker_min_api']=run(['docker','version','--format','{{.Server.MinAPIVersion}}']).strip()
r['containers']=[]
if ids:
 for c in json.loads(run(['docker','inspect']+ids)):
  n=c['Name'].lstrip('/')
  v={'name':n,'id':c['Id'],'image_id':c['Image'],'image_reference':c['Config']['Image'],'running':c['State']['Running'],'health':c['State'].get('Health',{}).get('Status'),'started_at':c['State']['StartedAt'],'restarts':c['RestartCount']}
  if n in ['node_exporter','cadvisor']:
   v.update({'command':c['Config'].get('Cmd'),'pid_mode':c['HostConfig']['PidMode'],'cgroupns':c['HostConfig'].get('CgroupnsMode'),'privileged':c['HostConfig'].get('Privileged'),'mounts':[{'source':m['Source'],'target':m['Destination'],'read_only':not m['RW']} for m in c['Mounts']]})
   if n=='cadvisor':
    log=subprocess.run(['docker','logs','--tail','200',n],capture_output=True,text=True,timeout=10)
    text=log.stdout+log.stderr
    v['diagnostic_flags']={'old_api':bool(re.search(r'client version.*too old',text,re.I)),'api_version_errors':len(re.findall('API version',text,re.I)),'docker_factory_error':bool(re.search('docker.*(failed|error)|failed.*docker',text,re.I)),'cgroup_error':bool(re.search('cgroup.*(failed|error|not found)',text,re.I))}
  r['containers'].append(v)
for port,key in [(9100,'node'),(8085,'cadvisor')]:
 try:
  text=urllib.request.urlopen('http://'+address+':'+str(port)+'/metrics',timeout=8).read().decode()
  result={'http':200}
  metric='node_exporter_build_info' if key=='node' else 'cadvisor_version_info'
  line=next((line for line in text.splitlines() if line.startswith(metric+'{')),'')
  label='version' if key=='node' else 'cadvisorVersion'
  version=re.search(r'(?:[,\{])'+label+r'="([^"\n]+)"',line)
  result['version']=version.group(1) if version else 'UNKNOWN'
  if key=='node':
   m=re.search(r'^node_memory_MemTotal_bytes (\S+)',text,re.M);result['memory_total']=float(m.group(1)) if m else None
   result['cpu_count']=len(re.findall(r'^node_cpu_seconds_total\{[^\n]*mode="idle"',text,re.M))
   result['native_cpu_time_series_count']=result['cpu_count']
   capacity=re.search(r'^lxc_cpu_capacity_cores(?:\{[^}]*\})? (\S+)',text,re.M)
   if capacity:
    result['cpu_count']=int(float(capacity.group(1)));result['cpu_source']='cgroup_v2_textfile'
    for metric,outkey in [('lxc_cpu_collector_success','cpu_collector_success'),('lxc_cpu_collector_timestamp_seconds','cpu_collector_timestamp'),('lxc_cpu_capacity_cores','cpu_capacity_cores'),('lxc_cpu_usage_seconds_total','cpu_usage_seconds'),('lxc_cpu_user_seconds_total','cpu_user_seconds'),('lxc_cpu_system_seconds_total','cpu_system_seconds'),('node_textfile_scrape_error','textfile_scrape_error')]:
     value=re.search(r'^'+metric+r'(?:\{[^}]*\})? (\S+)',text,re.M)
     result[outkey]=float(value.group(1)) if value else None
    identity=re.search(r'^lxc_cpu_usage_seconds_total\{[^\n]*ct_id="([^"\n]+)"',text,re.M)
    result['cpu_ct_id']=identity.group(1) if identity else None
    result['cpu_collector_age_seconds']=time.time()-result['cpu_collector_timestamp'] if result['cpu_collector_timestamp'] else None
   else:result['cpu_source']='procfs_unverified'

  else:
   rows=[l for l in text.splitlines() if l.startswith('container_memory_usage_bytes{')]
   result['memory_series']=len(rows);result['named_memory_series']=sum(bool(re.search(r'(?:^|[,{}])name="[^"\n]+"',l)) for l in rows)
   result['memory_container_names']=sorted({m.group(1).lstrip('/') for line in rows if (m:=re.search(r'(?:^|[,{}])name="([^"\n]+)"',line))})
   cpu=[l for l in text.splitlines() if l.startswith('container_cpu_usage_seconds_total{')]
   result['cpu_container_names']=sorted({m.group(1).lstrip('/') for line in cpu if (m:=re.search(r'(?:^|[,{}])name="([^"\n]+)"',line))})
  r[key+'_endpoint']=result
 except Exception as e:r[key+'_endpoint']={'error':type(e).__name__}
print(json.dumps(r))
'''
remote='''import subprocess,json,re,pathlib
services=SERVICES
collector=COLLECTOR
out={'services':[]}
for s in services:
 r={'service':s['name'],'ct':s['vmid'],'ip':s['ip'].split('/')[0]}
 try:
  c=subprocess.run(['pct','config',str(s['vmid'])],capture_output=True,text=True,timeout=6)
  config=dict(l.split(': ',1) for l in c.stdout.splitlines() if ': ' in l)
  r['proxmox']={k:config.get(k) for k in ['hostname','cores','memory','swap','unprivileged','features']}
  x=subprocess.run(['pct','exec',str(s['vmid']),'--','python3','-',s['ip'].split('/')[0]],input=collector,capture_output=True,text=True,timeout=35)
  if x.returncode==0:r['runtime']=json.loads(x.stdout)
  else:r['diagnostic_error']='Collector failed (details withheld)'
 except Exception as e:r['diagnostic_error']=type(e).__name__
 out['services'].append(r)
out['pve_memory_kib']=int(re.search(r'MemTotal:\\s+(\\d+)',pathlib.Path('/proc/meminfo').read_text()).group(1))
out['pve_cpu_count']=len(re.findall(r'^cpu\\d+ ',pathlib.Path('/proc/stat').read_text(),re.M))
out['lxcfs_version']=subprocess.run(['dpkg-query','-W','-f=${Version}','lxcfs'],capture_output=True,text=True).stdout.strip()
print(json.dumps(out))
'''.replace('SERVICES',repr(services)).replace('COLLECTOR',repr(collector))
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','ConnectTimeout=10','-o','ServerAliveInterval=30',args.ssh_alias,'python3','-'],input=remote,capture_output=True,text=True,timeout=650)
if r.returncode:raise RuntimeError('Read-only PVE audit failed; details withheld')
data=json.loads(r.stdout);data['observed_at']=datetime.now(ZoneInfo('Europe/Madrid')).isoformat();data['mode']='read-only'
p=args.output;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2)+'\n')
for s in data['services']:
 rt=s.get('runtime',{});print(s['service'],s.get('diagnostic_error',''),s['proxmox'],{k:rt.get(k) for k in ['proc_memory_kib','proc_cpu_count','node_endpoint','cadvisor_endpoint','docker_version']},flush=True)
print('PVE:',{k:data[k] for k in ['pve_memory_kib','pve_cpu_count','lxcfs_version']})

#!/usr/bin/env python3
"""Read-only gate for the FIRST authorized real CT. Not run by offline validation.
Writes only local receipt/activation candidates, never Proxmox/Prometheus/Grafana.
"""
import argparse,datetime,hashlib,json,re,shlex,subprocess,time,urllib.request
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--node',required=True);p.add_argument('--pve-host',default='pve');a=p.parse_args()
 root=a.bundle.resolve();manifest=json.loads((root/'manifest.json').read_text());d=manifest['declared'];s=d['service'];ct=s['vmid'];ip=s['ip'].split('/')[0]
 assert not manifest['fixture'],'TEST-NET fixtures cannot be verified or activated against production'
 assert re.fullmatch(r'[a-zA-Z0-9_.-]+',a.node) and re.fullmatch(r'[a-zA-Z0-9_.@-]+',a.pve_host)
 for name,digest in manifest['files'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,'Bundle drift'
 code='''import subprocess,json,pathlib,time
node=NODE;ct=CT
conf=json.loads(subprocess.check_output(['pvesh','get','/nodes/'+node+'/lxc/'+str(ct)+'/config','--output-format','json']))
status=json.loads(subprocess.check_output(['pvesh','get','/nodes/'+node+'/lxc/'+str(ct)+'/status/current','--output-format','json']))
cg=pathlib.Path('/sys/fs/cgroup/lxc')/str(ct);cpu=dict(line.split() for line in (cg/'cpu.stat').read_text().splitlines())
out={'hostname':conf['hostname'],'cores':conf['cores'],'memory':conf['memory'],'net0':conf['net0'],'rootfs':conf['rootfs'],'status':status['status'],'uptime':status['uptime'],'cpu_seconds':int(cpu['usage_usec'])/1e6,'timestamp':time.time(),'guest_addresses':json.loads(subprocess.check_output(['pct','exec',str(ct),'--','ip','-j','-4','addr','show','dev','eth0']))}
print(json.dumps(out))'''.replace('NODE',repr(a.node)).replace('CT',str(ct))
 r=subprocess.run(['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes',a.pve_host,shlex.join(['python3','-c',code])],capture_output=True,timeout=30)
 assert r.returncode==0,'PVE/SSH gate failed; output withheld';actual=json.loads(r.stdout)
 assert actual['hostname']==s['name'] and actual['status']=='running' and actual['uptime']>0
 assert actual['cores']==d['resources']['cpu'] and actual['memory']==d['resources']['memory'] and (('ip=dhcp' in actual['net0']) if d['network'].get('dhcp',False) else ('ip='+s['ip']) in actual['net0'])
 if d['network'].get('dhcp',False):assert any(a['local']==ip for link in actual['guest_addresses'] for a in link.get('addr_info',[])),'DHCP lease differs from declared observed address'
 with urllib.request.urlopen('http://'+ip+':9100/metrics',timeout=10) as response:body=response.read().decode()
 def metric(name):
  rows=re.findall(r'^'+re.escape(name)+r'(\{[^\n]*\})? ([^\s]+)$',body,re.M);assert len(rows)==1,'Missing/duplicate metric: '+name
  return float(rows[0][1]),rows[0][0]
 capacity,labels=metric('lxc_cpu_capacity_cores');assert 'ct_id="'+str(ct)+'"' in labels and capacity==actual['cores']
 timestamp,_=metric('lxc_cpu_collector_timestamp_seconds');assert 0<=time.time()-timestamp<=15
 success,_=metric('lxc_cpu_collector_success');assert success==1
 used,_=metric('lxc_cpu_usage_seconds_total');assert abs(used-actual['cpu_seconds'])<=actual['cores']*15
 memory,_=metric('node_memory_MemTotal_bytes');assert memory==actual['memory']*1024*1024
 assert not re.search(r'^node_cpu_seconds_total',body,re.M),'Physical CPU fallback detected'
 if d['monitoring']['docker']:
  with urllib.request.urlopen('http://'+ip+':8085/metrics',timeout=10) as response:cadvisor=response.read().decode()
  assert 'container_last_seen{' in cadvisor and 'container_cpu_usage_seconds_total{' in cadvisor and 'container_memory_usage_bytes{' in cadvisor
  # Read namespace identities inside this LXC; do not inspect unrelated CTs.
  ns_code="import subprocess,json,pathlib;c=json.loads(subprocess.check_output(['docker','inspect','cadvisor']))[0];dockerd=subprocess.check_output(['pgrep','-xo','dockerd'],text=True).strip();paths=['/proc/1/ns/cgroup','/proc/'+dockerd+'/ns/cgroup','/proc/'+str(c['State']['Pid'])+'/ns/cgroup'];print(json.dumps([str(pathlib.Path(p).readlink()) for p in paths]))"
  result=subprocess.run(['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes',a.pve_host,shlex.join(['pct','exec',str(ct),'--','python3','-c',ns_code])],capture_output=True,timeout=30);assert result.returncode==0
  namespaces=json.loads(result.stdout);assert len(set(namespaces))==1,'cAdvisor/Docker/LXC namespace mismatch'
 for probe in d['monitoring'].get('blackbox',[]):
  with urllib.request.urlopen(probe['url'],timeout=5) as response:
   assert response.status==200
   if probe.get('body_regex'):assert re.search(probe['body_regex'],response.read(65536).decode()),'Functional content mismatch'
 activation=root/'activation';activation.mkdir(exist_ok=True)
 for name in ['node-exporter.json','cadvisor.json','blackbox.json','expected-inventory.yml']:
  data=(root/'monitoring'/name).read_bytes();(activation/name).write_bytes(data)
 nodes=json.loads((activation/'node-exporter.json').read_text());nodes[0]['labels']['cpu_contract']='lxc_cgroup_v1';(activation/'node-exporter.json').write_text(json.dumps(nodes,indent=2)+'\n')
 receipt={'result':'PASS','ct_id':ct,'service':s['name'],'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'read-only PVE+cgroup+Node verification','cpu_source':'cgroup_v2_textfile','state':'RUNNING','allocated_cores':actual['cores'],'memory_mib':actual['memory'],'uptime_seconds':actual['uptime'],'activation':'CANDIDATE_ONLY_NOT_APPLIED','stability_acceptance':'PENDING VERIFICATION','application_health':'declared probe contracts checked; no business UAT'}
 (root/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()

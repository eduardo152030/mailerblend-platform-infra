#!/usr/bin/env python3
"""Run ONLY inside a newly authorized LXC. Installs exporters, never applications.
Root required; --confirm-new-ct and explicit Docker socket approval are safeguards,
not substitutes for owner authorization. No Terraform, DNS or application operations.
"""
import argparse,hashlib,json,os,shutil,subprocess,tarfile,urllib.request
from pathlib import Path
BASE=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--confirm-new-ct',type=int,required=True);p.add_argument('--approve-containerd-socket',action='store_true');a=p.parse_args();c=json.loads((BASE/'install-config.json').read_text())
 assert os.geteuid()==0 and a.confirm_new_ct==c['ct_id'] and Path('/etc/hostname').read_text().strip()==c['hostname'],'Wrong or unverified LXC identity'
 assert 'usage_usec' in Path('/sys/fs/cgroup/cpu.stat').read_text(),'cgroup v2 source absent'
 mem=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemTotal:')))*1024
 assert mem==c['memory_mib']*1024*1024,'RAM view is not the declared LXC allocation'
 if c['docker']:
  assert a.approve_containerd_socket and Path('/run/containerd/containerd.sock').is_socket(),'Exact socket access not approved/available'
  subprocess.run(['docker','info'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 cache=BASE/'artifacts';cache.mkdir(exist_ok=True);archive=cache/c['node_archive']
 if not archive.exists():
  url='https://github.com/prometheus/node_exporter/releases/download/v1.10.2/'+c['node_archive']
  with urllib.request.urlopen(url,timeout=60) as source:archive.write_bytes(source.read())
 assert hashlib.sha256(archive.read_bytes()).hexdigest()==c['node_sha256'],'Archive checksum mismatch'
 dest=Path('/opt/lxc-monitoring');dest.mkdir(exist_ok=True);changed=[]
 def put(path,body,mode=0o644):
  path=Path(path)
  if path.exists() and path.read_bytes()==body:return
  path.write_bytes(body);path.chmod(mode);changed.append(str(path))
 with tarfile.open(archive) as bundle:
  binary=bundle.extractfile('node_exporter-1.10.2.linux-amd64/node_exporter').read()
 put(dest/'node_exporter',binary,0o755);put(dest/'node-cgroup.sh',(BASE/'node-cgroup.sh').read_bytes(),0o755)
 metric=Path('/var/lib/node_exporter/textfile');metric.mkdir(parents=True,exist_ok=True);os.chown(metric,65534,65534)
 for unit in ['node-exporter.service','lxc-cpu.service','lxc-cpu.timer']:put('/etc/systemd/system/'+unit,(BASE/unit).read_bytes())
 if changed:subprocess.run(['systemctl','daemon-reload'],check=True)
 subprocess.run(['systemctl','start','lxc-cpu.service'],check=True)
 for unit in ['lxc-cpu.timer','node-exporter.service']:
  active=subprocess.run(['systemctl','is-active','--quiet',unit]).returncode==0
  if not active:subprocess.run(['systemctl','enable','--now',unit],check=True)
  elif changed and unit=='node-exporter.service':subprocess.run(['systemctl','restart',unit],check=True)
 if c['docker']:
  put(dest/'cadvisor.yml',(BASE/'cadvisor.yml').read_bytes())
  subprocess.run(['docker','compose','-f',str(dest/'cadvisor.yml'),'config','--quiet'],check=True)
  subprocess.run(['docker','compose','-f',str(dest/'cadvisor.yml'),'up','-d','--no-deps','cadvisor'],check=True)
 print(json.dumps({'ct_id':c['ct_id'],'configuration_writes':len(changed),'applications_touched':False,'monitoring_activation':'NOT PERFORMED; run runtime verification first'}))
if __name__=='__main__':main()

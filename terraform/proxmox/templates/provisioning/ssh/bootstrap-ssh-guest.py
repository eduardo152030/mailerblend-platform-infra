#!/usr/bin/env python3
"""Executed only via pct exec in a NEW authorized Debian/Ubuntu CT.
prepare adds a public key and enables public-key access without closing password
methods. harden requires the controller's successful key-authentication gate.
"""
import argparse,base64,hashlib,json,os,shlex,stat,subprocess,time
from pathlib import Path
POLICY=b'''# Managed by future-LXC provisioning.
PermitRootLogin prohibit-password
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
'''
INCLUDE=b'Include /etc/ssh/sshd_config.d/00-lxc-bootstrap.conf\n'

def merge_keys(body,key):
 identity=tuple(key.split()[:2]);lines=body.splitlines();seen=set();result=[];found=False
 for line in lines:
  try:parts=shlex.split(line,comments=True)
  except ValueError:parts=[]
  entry=line
  for i,part in enumerate(parts[:-1]):
   if part.startswith(('ssh-','ecdsa-')):
    entry=tuple(parts[:i+2]);break
  for i,part in enumerate(parts[:-1]):
   if (part,parts[i+1])==identity:found=True
  # Duplicate key+options entries collapse; different options/legitimate keys stay intact.
  if line.strip() and not line.lstrip().startswith('#'):
   if entry in seen:continue
   seen.add(entry)
  result.append(line)
 if not found:result.append(key)
 return '\n'.join(result).rstrip('\n')+'\n'

class Guest:
 def __init__(self,root=Path('/'),run=None,uid=0,gid=0):self.root=Path(root);self.run=run or self.command;self.writes=0;self.uid=uid;self.gid=gid
 def path(self,name):return self.root/name.lstrip('/')
 def command(self,args):
  p=subprocess.run(args,capture_output=True,text=True)
  if p.returncode and args[:2]!=['systemctl','is-active']:raise RuntimeError('SSH bootstrap command failed; sensitive output withheld')
  return p.stdout
 def safe(self,path):
  current=path
  while current!=self.root and current!=current.parent:
   if current.is_symlink():raise RuntimeError('Symlink refused in managed SSH path')
   current=current.parent
 def put(self,path,body,mode=0o600):
  self.safe(path);path.parent.mkdir(parents=True,exist_ok=True)
  if not path.exists() or path.read_bytes()!=body:
   temp=path.with_name(path.name+'.lxc-new');self.safe(temp);temp.write_bytes(body);temp.chmod(mode);os.chown(temp,self.uid,self.gid);os.replace(temp,path);self.writes+=1

  if stat.S_IMODE(path.stat().st_mode)!=mode:path.chmod(mode)
  if (path.stat().st_uid,path.stat().st_gid)!=(self.uid,self.gid):os.chown(path,self.uid,self.gid)
 def state(self):
  path=self.path('/var/lib/lxc-ssh-bootstrap/state.json');self.safe(path);return json.loads(path.read_text())
 def save(self,state):
  folder=self.path('/var/lib/lxc-ssh-bootstrap');folder.mkdir(parents=True,exist_ok=True);folder.chmod(0o700)
  self.put(folder/'state.json',(json.dumps(state,indent=2)+'\n').encode())
 def effective(self,context):
  text=self.run(['/usr/sbin/sshd','-T','-C',context]);return dict(line.split(None,1) for line in text.splitlines() if ' ' in line)
 def check(self):self.run(['/usr/sbin/sshd','-t'])
 def reload(self):
  active=self.run(['systemctl','is-active','ssh.service']).strip()
  self.run(['systemctl','reload','ssh.service'] if active=='active' else ['systemctl','start','ssh.service'])
 def policy(self,body):
  cfg=self.path('/etc/ssh/sshd_config');original=cfg.read_bytes()
  managed=self.path('/etc/ssh/sshd_config.d/00-lxc-bootstrap.conf');self.put(managed,body,0o644)
  if not original.startswith(INCLUDE):self.put(cfg,INCLUDE+original,0o644)
 def prepare(self,payload):
  distro={}
  for line in self.path('/etc/os-release').read_text().splitlines():
   if '=' in line:k,v=line.split('=',1);distro[k]=v.strip('"')
  if distro.get('ID') not in ['ubuntu','debian']:raise RuntimeError('Unsupported SSH OS; no edits performed')
  if not self.path('/usr/sbin/sshd').exists():
   self.run(['env','DEBIAN_FRONTEND=noninteractive','apt-get','update'])
   self.run(['env','DEBIAN_FRONTEND=noninteractive','apt-get','install','-y','openssh-server'])
  runtime=self.path('/run/sshd');runtime.mkdir(parents=True,exist_ok=True)
  self.run(['ssh-keygen','-A']) # Host keys stay in this CT; only .pub is ever returned.
  folder=self.path('/root/.ssh');self.safe(folder);folder.mkdir(parents=True,exist_ok=True)
  if stat.S_IMODE(folder.stat().st_mode)!=0o700:folder.chmod(0o700)
  if (folder.stat().st_uid,folder.stat().st_gid)!=(self.uid,self.gid):os.chown(folder,self.uid,self.gid)
  keys=folder/'authorized_keys';self.safe(keys);old=keys.read_text() if keys.exists() else '';self.put(keys,merge_keys(old,payload['key']).encode())
  store=self.path('/var/lib/lxc-ssh-bootstrap/state.json')
  if store.exists():
   state=self.state();assert state['fingerprint']==payload['fingerprint'],'Different key requires a fresh reviewed bootstrap'
   if state.get('status')=='DONE':
    self.check();values=self.effective(payload['context']);self.assert_final(values);return {'stage':'DONE','writes':self.writes,'host_keys':self.host_keys()}
  else:
   self.check();values=self.effective(payload['context'])
   cfg=self.path('/etc/ssh/sshd_config');managed=self.path('/etc/ssh/sshd_config.d/00-lxc-bootstrap.conf');self.safe(managed)
   state={'status':'PREPARED','fingerprint':payload['fingerprint'],'original_config':base64.b64encode(cfg.read_bytes()).decode(),'original_managed':base64.b64encode(managed.read_bytes()).decode() if managed.exists() else None,'password_before':values.get('passwordauthentication'),'kbd_before':values.get('kbdinteractiveauthentication'),'root_before':values.get('permitrootlogin')};self.save(state)
  values=self.effective(payload['context'])
  # Keep existing root password access if it existed; never enable password auth.
  root=values.get('permitrootlogin','prohibit-password')
  root=root if root in ['yes','prohibit-password','without-password'] else 'prohibit-password'
  transition=('PermitRootLogin '+root+'\nPubkeyAuthentication yes\n').encode()
  self.policy(transition)
  try:
   self.check();after=self.effective(payload['context'])
   assert after.get('passwordauthentication')==state['password_before'] and after.get('kbdinteractiveauthentication')==state['kbd_before'],'Transition would close existing authentication'
   assert after.get('pubkeyauthentication')=='yes' and after.get('permitrootlogin') in ['yes','prohibit-password','without-password']
   self.reload()
  except Exception:self.rollback();raise
  return {'stage':'PREPARED','writes':self.writes,'host_keys':self.host_keys()}
 def host_keys(self):
  # DSA can remain in old templates, but is not an admissible host identity.
  files=sorted(self.path('/etc/ssh').glob('ssh_host_*_key.pub'))
  supported={'ssh-ed25519','ssh-rsa','ecdsa-sha2-nistp256','ecdsa-sha2-nistp384','ecdsa-sha2-nistp521'}
  return [body for p in files if (body:=p.read_text().strip()) and body.split()[0] in supported]
 def assert_final(self,values):
  expected={'passwordauthentication':'no','kbdinteractiveauthentication':'no','pubkeyauthentication':'yes'}
  assert all(values.get(k)==v for k,v in expected.items()),'Effective SSH policy differs'
  assert values.get('permitrootlogin') in ['prohibit-password','without-password']
 def harden(self,payload):
  assert payload.get('key_access_confirmed') is True,'Key access gate has not passed'
  state=self.state();assert state['fingerprint']==payload['fingerprint']
  self.policy(POLICY)
  try:self.check();self.assert_final(self.effective(payload['context']));self.reload()
  except Exception:self.rollback();raise
  return {'stage':'HARDENED','writes':self.writes}
 def confirm(self,payload):
  assert payload.get('key_access_confirmed') is True
  state=self.state();assert state['fingerprint']==payload['fingerprint'];
  if state.get('status')!='DONE':state['status']='DONE';self.save(state)
  return {'stage':'DONE','writes':self.writes}
 def rollback(self):
  state=self.state();cfg=self.path('/etc/ssh/sshd_config');managed=self.path('/etc/ssh/sshd_config.d/00-lxc-bootstrap.conf')
  self.put(cfg,base64.b64decode(state['original_config']),0o644)
  if state['original_managed'] is None:
   if managed.exists():managed.unlink()
  else:self.put(managed,base64.b64decode(state['original_managed']),0o644)
  self.check();self.reload();state['status']='ROLLED_BACK';self.save(state)
  return {'stage':'ROLLED_BACK','authorized_key_retained':True}
if __name__=='__main__':
 import sys
 p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','harden','confirm','rollback']);a=p.parse_args();payload=json.load(sys.stdin)
 assert os.geteuid()==0 and Path('/etc/hostname').read_text().strip()==payload['hostname'],'Wrong LXC identity'
 guest=Guest();out=guest.rollback() if a.action=='rollback' else getattr(guest,a.action)(payload);print(json.dumps(out))

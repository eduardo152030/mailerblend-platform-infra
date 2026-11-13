#!/usr/bin/env python3
"""Automatic post-clone SSH gate, using only trusted Proxmox SSH + pct exec.
Only called for new opt-in Terraform resources. Never runs during prepare/test-plan.
"""
import argparse,hashlib,ipaddress,json,os,re,shlex,socket,subprocess,time
from pathlib import Path
from lxc_ssh import public_key

def ssh_options(known):return ['-o','UserKnownHostsFile='+str(known),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','-o','ConnectTimeout=10']
class Controller:
 def __init__(self,config,node,run=None):
  self.path=Path(config).resolve();self.base=self.path.parent;self.conf=json.loads(self.path.read_text());self.node=node;self.run=run or subprocess.run
  c=self.conf;assert not c['fixture'],'Fictional fixtures cannot execute SSH bootstrap'
  assert isinstance(c['ct_id'],int) and c['ct_id'] not in c['protected_ct_ids'],'Existing CT is protected'
  assert re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_.-]*',node) and re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_.@-]*',c['pve_host'])
  ipaddress.IPv4Address(c['ip']);self.key,self.fingerprint=public_key((self.base/'owner.pub').read_text());assert self.fingerprint==c['key_fingerprint']
 def pve(self,args,body=None):
  p=self.run(['ssh']+ssh_options(Path.home()/'.ssh/known_hosts')+['--',self.conf['pve_host'],shlex.join(args)],input=body,capture_output=True,text=True,timeout=90)
  assert p.returncode==0,'Trusted PVE/pct step failed; output withheld';return p.stdout
 def guest(self,action,confirmed=False):
  payload={'hostname':self.conf['hostname'],'key':self.key,'fingerprint':self.fingerprint,'context':self.context,'key_access_confirmed':confirmed}
  source=(self.base/'bootstrap-ssh-guest.py').read_text()
  return json.loads(self.pve(['pct','exec',str(self.conf['ct_id']),'--','python3','-c',source,action],json.dumps(payload)))
 def verify_key(self):
  public_source=Path(self.conf['owner_public_key_file']).expanduser();assert public_source.suffix=='.pub'
  # Only OpenSSH consumes the local signing identity. Python never opens/copies it.
  identity=public_source.with_suffix('')
  args=['ssh']+ssh_options(self.base/'known_hosts')+['-p','22','-o','IdentitiesOnly=yes','-i',str(identity),'-o','PreferredAuthentications=publickey','-o','PasswordAuthentication=no','-o','KbdInteractiveAuthentication=no','root@'+self.conf['ip'],'true']
  p=self.run(args,capture_output=True,text=True,timeout=60 if self.conf.get("dhcp",False) else 20)
  assert p.returncode==0,'Owner key access not verified; no password fallback; output withheld'
 def execute(self):
  c=self.conf
  # Read only the selected CT; never sweep the 17 accepted LXCs.
  code="import subprocess,json;c=json.loads(subprocess.check_output(['pvesh','get',"+repr('/nodes/'+self.node+'/lxc/'+str(c['ct_id'])+'/config')+",'--output-format','json']));s=json.loads(subprocess.check_output(['pvesh','get',"+repr('/nodes/'+self.node+'/lxc/'+str(c['ct_id'])+'/status/current')+",'--output-format','json']));print(json.dumps({'hostname':c['hostname'],'net0':c['net0'],'status':s['status']}))"
  state=json.loads(self.pve(['python3','-c',code]));assert state['hostname']==c['hostname'] and state['status']=='running' and (('ip=dhcp' in state['net0']) if c.get('dhcp',False) else ('ip='+c['ip']+'/') in state['net0']),'CT identity differs'
  if c.get('dhcp',False):
   addresses=json.loads(self.pve(['pct','exec',str(c['ct_id']),'--','ip','-j','-4','addr','show','dev','eth0']));assert any(a['local']==c['ip'] for link in addresses for a in link.get('addr_info',[])),'DHCP lease mismatch'
  with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
   sock.connect((c['ip'],22));client=sock.getsockname()[0]
  self.context='user=root,host='+client+',addr='+client+',laddr='+c['ip']+',lport=22'
  stage=self.guest('prepare');hostkeys=[]
  for raw in stage['host_keys']:
   key,_=public_key(raw);hostkeys.append(c['ip']+' '+key)
  assert hostkeys,'No host identity returned by trusted console'
  known=self.base/'known_hosts';assert not known.is_symlink();body='\n'.join(sorted(set(hostkeys)))+'\n'
  if not known.exists() or known.read_text()!=body:known.write_text(body);known.chmod(0o600)
  try:
   self.verify_key()
   if stage['stage']!='DONE':
    self.guest('harden',True);self.verify_key();self.guest('confirm',True)
  except Exception:
   if stage['stage']!='DONE':self.guest('rollback')
   raise
  result={'ct_id':c['ct_id'],'result':'PASS','key_fingerprint':self.fingerprint,'owner_key_access':'VERIFIED','password_authentication':'no','keyboard_interactive':'no','root_login':'prohibit-password','host_identity_source':'trusted PVE pct exec, not keyscan','console_recovery_preserved':True,'stage_before':stage['stage'],'guest_prepare_writes':stage['writes']}
  receipt=self.base/'verified.json';text=json.dumps(result,indent=2)+'\n'
  if not receipt.exists() or receipt.read_text()!=text:receipt.write_text(text);receipt.chmod(0o600)
  print(json.dumps({'ct_id':c['ct_id'],'result':'PASS','owner_key_access':'VERIFIED','console_recovery_preserved':True}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,default=os.environ.get('LXC_SSH_CONFIG') or None);p.add_argument('--node',default=os.environ.get('LXC_PVE_NODE'));p.add_argument('--execute',action='store_true');p.add_argument('--if-configured',action='store_true');a=p.parse_args()
 if a.if_configured and not os.environ.get('LXC_SSH_CONFIG') and not a.config:raise SystemExit(0)
 assert a.execute and a.config and a.node,'Explicit execution/authorized new CT required'
 Controller(a.config,a.node).execute()

import base64,importlib.util,json,os,stat,struct,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import yaml
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from lxc_ssh import public_key,render

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
G=load('ssh_guest',ROOT/'templates/provisioning/ssh/bootstrap-ssh-guest.py')
C=load('ssh_controller',ROOT/'scripts/bootstrap-new-lxc-ssh.py')
# Synthetic PUBLIC wire fixture; never a private identity or real signing key.
KEY='ssh-ed25519 '+base64.b64encode(struct.pack('>I',11)+b'ssh-ed25519'+struct.pack('>I',32)+b'a'*32).decode()
OTHER=KEY.replace('YWFh','YmJi')
class SSHBootstrap(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  for path,body in {'etc/os-release':'ID=debian\n','etc/ssh/sshd_config':'PermitRootLogin yes\nPasswordAuthentication yes\nKbdInteractiveAuthentication yes\nPubkeyAuthentication no\n','usr/sbin/sshd':'fixture','etc/ssh/ssh_host_ed25519_key.pub':KEY}.items():
   p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(body)
  self.calls=[];self.bad=False
  def run(args):
   self.calls.append(args)
   if '-T' in args:
    values={};cfg=(self.root/'etc/ssh/sshd_config').read_text();managed=self.root/'etc/ssh/sshd_config.d/00-lxc-bootstrap.conf'
    if cfg.startswith(G.INCLUDE.decode()):cfg=managed.read_text()+cfg
    for line in cfg.splitlines():
     fields=line.split()
     if len(fields)==2:values.setdefault(fields[0].lower(),fields[1])
    return '\n'.join(k+' '+v for k,v in values.items())
   if '-t' in args and self.bad:self.bad=False;raise RuntimeError('synthetic syntax failure')
   return 'active\n' if args[:2]==['systemctl','is-active'] else ''
  self.g=G.Guest(self.root,run,os.getuid(),os.getgid());self.payload={'key':KEY,'fingerprint':public_key(KEY)[1],'context':'user=root,host=localhost,addr=127.0.0.1','key_access_confirmed':True}
 def test_legacy_dsa_host_key_is_not_trusted(self):
  (self.root/'etc/ssh/ssh_host_dsa_key.pub').write_text('ssh-dss legacy')
  self.assertEqual(self.g.host_keys(),[KEY])
  self.assertEqual((self.root/'etc/ssh/ssh_host_dsa_key.pub').read_text(),'ssh-dss legacy')
 def test_key_merge_preserves_keys_options_and_comments(self):
  body='# existing\n'+OTHER+' other\n'+KEY+' owner\n'+KEY+' duplicate-comment\n'
  merged=G.merge_keys(body,KEY);self.assertIn(OTHER,merged);self.assertEqual(merged.count(KEY),1);self.assertEqual(G.merge_keys(merged,KEY),merged)
  restricted='from="192.0.2.1" '+KEY+' restricted\n';self.assertEqual(G.merge_keys(restricted,KEY),restricted)
 def test_permissions_two_phase_policy_and_idempotence(self):
  out=self.g.prepare(self.payload);self.assertEqual(out['stage'],'PREPARED')
  values=self.g.effective(self.payload['context']);self.assertEqual(values['passwordauthentication'],'yes');self.assertEqual(values['kbdinteractiveauthentication'],'yes')
  for path,mode in [('root/.ssh',0o700),('root/.ssh/authorized_keys',0o600)]:
   s=(self.root/path).stat();self.assertEqual(stat.S_IMODE(s.st_mode),mode);self.assertEqual(s.st_uid,os.getuid())
  with self.assertRaises(AssertionError):self.g.harden(dict(self.payload,key_access_confirmed=False))
  self.g.harden(self.payload);self.g.assert_final(self.g.effective(self.payload['context']));self.g.confirm(self.payload)
  reloads=sum(a[:2]==['systemctl','reload'] for a in self.calls);before=self.g.writes
  self.assertEqual(self.g.prepare(self.payload)['stage'],'DONE');self.g.confirm(self.payload)
  self.assertEqual(self.g.writes,before);self.assertEqual(sum(a[:2]==['systemctl','reload'] for a in self.calls),reloads)
  for i,args in enumerate(self.calls):
   if args[:2]==['systemctl','reload']:self.assertIn(['/usr/sbin/sshd','-t'],self.calls[:i])
 def test_failed_syntax_restores_original_and_retains_key(self):
  original=(self.root/'etc/ssh/sshd_config').read_bytes();self.g.prepare(self.payload);self.bad=True
  with self.assertRaises(RuntimeError):self.g.harden(self.payload)
  self.assertEqual((self.root/'etc/ssh/sshd_config').read_bytes(),original);self.assertIn(KEY,(self.root/'root/.ssh/authorized_keys').read_text());self.assertEqual(self.g.state()['status'],'ROLLED_BACK')
 def test_effective_policy_conflict_restores_original(self):
  self.g.prepare(self.payload);original=self.g.effective
  def conflicting(context):
   result=original(context);result['passwordauthentication']='yes';return result
  self.g.effective=conflicting
  with self.assertRaises(AssertionError):self.g.harden(self.payload)
  self.assertEqual(self.g.state()['status'],'ROLLED_BACK')
 def test_package_install_only_when_missing(self):
  (self.root/'usr/sbin/sshd').unlink();self.g.prepare(self.payload)
  self.assertTrue(any(a[-1]=='openssh-server' for a in self.calls));self.assertFalse(any('docker' in ' '.join(a) for a in self.calls))
 def test_unsupported_os_and_symlink_refused(self):
  (self.root/'etc/os-release').write_text('ID=alpine\n')
  with self.assertRaises(RuntimeError):self.g.prepare(self.payload)
  self.assertEqual(self.g.writes,0)
  (self.root/'etc/os-release').write_text('ID=debian\n');(self.root/'root').mkdir();(self.root/'root/.ssh').symlink_to(self.root/'etc')
  with self.assertRaises(RuntimeError):self.g.prepare(self.payload)
 def test_public_source_and_docker_independence_no_secrets(self):
  pub=self.root/'owner.pub';pub.write_text(KEY+' comment\n');outputs=[]
  for docker in [False,True]:
   data=yaml.safe_load((ROOT/'examples/new-lxc/service.yml').read_text());data['monitoring']['docker']=docker
   out=self.root/str(docker);render(ROOT,out,data,pub,[624]);outputs.append(out)
   conf=json.loads((out/'bootstrap.json').read_text());self.assertEqual(conf['docker'],docker);self.assertTrue(conf['fixture']);self.assertEqual((out/'owner.pub').read_text(),KEY+'\n')
   self.assertFalse(any('PRIVATE KEY' in p.read_text() for p in out.iterdir()))
   with self.assertRaises(AssertionError):C.Controller(out/'bootstrap.json','pve')
  self.assertEqual((outputs[0]/'00-lxc-bootstrap.conf').read_bytes(),(outputs[1]/'00-lxc-bootstrap.conf').read_bytes())
  with self.assertRaises(ValueError):public_key('-----BEGIN OPENSSH PRIVATE KEY-----')
  with self.assertRaises(ValueError):render(ROOT,self.root/'bad',data,pub.with_suffix(''),[])
 def controller(self):
  out=self.root/'controller';pub=self.root/'owner.pub';pub.write_text(KEY);data=yaml.safe_load((ROOT/'examples/new-lxc/service.yml').read_text());render(ROOT,out,data,pub,[624]);p=out/'bootstrap.json';conf=json.loads(p.read_text());conf['fixture']=False;p.write_text(json.dumps(conf));return C.Controller(p,'pve')
 def test_controller_gates_and_rollback(self):
  for fail in [0,1,2]:
   c=self.controller() if fail==0 else c;actions=[];checks=[]
   c.pve=lambda *a,**k:json.dumps({'hostname':c.conf['hostname'],'net0':'ip='+c.conf['ip']+'/24','status':'running'})
   def guest(action,confirmed=False):actions.append(action);return {'stage':'PREPARED','writes':1,'host_keys':[KEY]}
   c.guest=guest
   def verify():
    checks.append(len(actions))
    if len(checks)==fail:raise AssertionError('fixture access failure')
   c.verify_key=verify
   with patch.object(C.socket,'socket') as sock:
    sock.return_value.__enter__.return_value.getsockname.return_value=('127.0.0.1',50000)
    if fail:
     with self.assertRaises(AssertionError):c.execute()
     self.assertEqual(actions[-1],'rollback');self.assertNotIn('confirm',actions)
     if fail==1:self.assertNotIn('harden',actions)
    else:c.execute();self.assertEqual(actions,['prepare','harden','confirm']);self.assertEqual(checks,[1,2])
 def test_strict_client_flags_and_protected_ct(self):
  c=self.controller();commands=[]
  class Result:returncode=0
  c.run=lambda args,**kw:(commands.append(args) or Result());c.verify_key();cmd=' '.join(commands[0]);self.assertIn('BatchMode=yes',cmd);self.assertIn('StrictHostKeyChecking=yes',cmd);self.assertIn('PasswordAuthentication=no',cmd);self.assertIn('root@',cmd)
  conf=c.conf;conf['ct_id']=624;c.path.write_text(json.dumps(conf))
  with self.assertRaises(AssertionError):C.Controller(c.path,'pve')
if __name__=='__main__':unittest.main()

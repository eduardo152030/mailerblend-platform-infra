import copy,importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('sgtm_recovery',ROOT/'scripts/recover-sgtm-614.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class RecoveryTests(unittest.TestCase):
 def container(self):return {'Config':{'Image':'same','Env':['A=1','B=2'],'Entrypoint':['/nodejs/bin/node'],'Cmd':['/app/server_bin.js']},'HostConfig':{'Memory':0,'MemorySwap':0,'NanoCpus':0,'PortBindings':{'8080/tcp':[{'HostPort':'8091'}]},'NetworkMode':'infra-nucleoedge_default'},'Image':'sha256:same','Mounts':[],'NetworkSettings':{'Networks':{'infra-nucleoedge_default':{}}}}
 def test_configuration_image_ports_secrets_resources_cannot_change(self):
  old=self.container();m.equivalent(old,copy.deepcopy(old))
  for where,key,value in [('Config','Env',['A=changed']),('Config','Image','other'),('HostConfig','Memory',512),('HostConfig','PortBindings',{}),('HostConfig','NetworkMode','other')]:
   new=copy.deepcopy(old);new[where][key]=value
   with self.assertRaises(AssertionError):m.equivalent(old,new)
  new=copy.deepcopy(old);new['Image']='sha256:new'
  with self.assertRaises(AssertionError):m.equivalent(old,new)
 def test_environment_order_is_not_a_configuration_change(self):
  old=self.container();new=copy.deepcopy(old);new['Config']['Env'].reverse();m.equivalent(old,new)
 def test_main_cannot_be_recreated_before_preview_acceptance(self):
  with tempfile.TemporaryDirectory() as d:
   here=Path(d);(here/'state.json').write_text(json.dumps({'steps':['health_only_candidate_verified']}))
   with patch.object(m,'compose') as compose:
    with self.assertRaises(AssertionError):m.remote_action('apply-main',here)
    compose.assert_not_called()
 def test_mutation_requires_verified_offhost_backup(self):
  with tempfile.TemporaryDirectory() as d:
   here=Path(d);(here/'state.json').write_text(json.dumps({'steps':['snapshot_verified'],'backup_sha256':'hash'}))
   with self.assertRaises(FileNotFoundError):m.remote_action('install',here)
 def test_other_containers_must_not_restart_or_change_identity(self):
  c={'Id':'id','Image':'image','RestartCount':0,'State':{'StartedAt':'before','Running':True}};before={'node_exporter':c};after=copy.deepcopy(before);m.others_unchanged(before,after);after['node_exporter']['State']['StartedAt']='after'
  with self.assertRaises(AssertionError):m.others_unchanged(before,after)
 def test_null_and_empty_dns_defaults_are_equivalent_but_explicit_dns_must_not_change(self):
  old=self.container();old['HostConfig'].update(Dns=[],DnsSearch=[]);new=copy.deepcopy(old);new['HostConfig'].update(Dns=None,DnsSearch=None);m.equivalent(old,new)
  old['HostConfig']['Dns']=['192.168.1.1']
  with self.assertRaises(AssertionError):m.equivalent(old,new)
 def test_preview_protects_current_restored_main_identity_not_historical_id(self):
  old=self.container();old.update(Id='original-main',RestartCount=0,State={'Running':True,'StartedAt':'old','OOMKilled':False,'Health':{'Status':'healthy'}})
  current=copy.deepcopy(old);current['Id']='restored-main'
  preview=copy.deepcopy(current);preview['Id']='new-preview'
  before={m.NAMES['sgtm']:old,m.NAMES['sgtm_preview']:old}
  now={m.NAMES['sgtm']:current,m.NAMES['sgtm_preview']:preview}
  with tempfile.TemporaryDirectory() as d:
   here=Path(d);overlay=here/'overlay';overlay.write_text('overlay')
   (here/'state.json').write_text(json.dumps({'steps':['health_only_candidate_verified'],'overlay_sha256':m.sha(overlay)}))
   (here/'baseline.private.json').write_text(json.dumps({'containers':before,'file_hashes':{}}))
   with patch.object(m,'OVERLAY',overlay),patch.object(m,'inspect_all',return_value=now),patch.object(m,'compose'),patch.object(m,'http',return_value=200),patch.object(m,'cmd',return_value=''):
    m.remote_action('apply-preview',here);m.remote_action('check-preview',here)
   state=json.loads((here/'state.json').read_text());self.assertEqual(state['serving_id_before_preview'],'restored-main');self.assertTrue(state['preview_accepted_current'])
 def test_historical_preview_acceptance_cannot_authorize_new_main_recreation(self):
  with tempfile.TemporaryDirectory() as d:
   here=Path(d);(here/'state.json').write_text(json.dumps({'steps':['health_only_candidate_verified','preview_healthy'],'preview_accepted_current':False}))
   with patch.object(m,'compose') as compose:
    with self.assertRaises(AssertionError):m.remote_action('apply-main',here)
    compose.assert_not_called()
 def test_recovery_does_not_recreate_main_from_an_earlier_attempt(self):
  old=self.container();old.update(Id='id',RestartCount=0,State={'Running':True,'StartedAt':'old'})
  before={n:copy.deepcopy(old) for n in m.NAMES.values()}
  with tempfile.TemporaryDirectory() as d:
   here=Path(d);(here/'state.json').write_text(json.dumps({'steps':['apply-main_started'],'current_attempt_services':['sgtm_preview']}));(here/'baseline.private.json').write_text(json.dumps({'containers':before,'file_hashes':{}}))
   with patch.object(m,'inspect_all',return_value=before),patch.object(m,'compose') as compose:
    m.remote_action('recover',here)
    self.assertEqual([c.args[1] for c in compose.call_args_list],[['sgtm_preview']])
if __name__=='__main__':unittest.main()

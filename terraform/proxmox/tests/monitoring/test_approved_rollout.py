"""D025 gates and failure boundaries, without network or production actions."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
ROOT=Path(__file__).resolve().parents[2]
def load(n):
 s=importlib.util.spec_from_file_location(n,ROOT/'scripts'/n);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class ApprovedRolloutTests(unittest.TestCase):
 def test_scope_excludes_recovered_apps_and_has_exact_order(self):
  m=load('rollout-approved-exporters.py')
  self.assertEqual(m.ORDER,[621,620,619,623,617,615,614,61211,611,616,610])
  for ct in [618,622,624,613,100]:
   with self.assertRaises(AssertionError):m.allowed(ct)
  self.assertIn('StrictHostKeyChecking=yes',m.SSH);self.assertIn('UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),m.SSH);self.assertIn('BatchMode=yes',m.SSH)
 def test_any_gate_failure_prevents_every_dependent_operation(self):
  m=load('rollout-approved-exporters.py');steps=['preflight','prepare','pull','mutate','observe_and_telegram','finish']
  for fail in steps:
   with tempfile.TemporaryDirectory() as d:
    r=object.__new__(m.Runner);r.ct=621;r.here=Path(d);r.state={'result':'IN_PROGRESS'}
    for step in steps:setattr(r,step,Mock(side_effect=RuntimeError('controlled failure') if step==fail else None))
    with patch.object(m,'execution_gate',return_value=None):
     with self.assertRaises(RuntimeError):r.execute()
    for step in steps[steps.index(fail)+1:]:getattr(r,step).assert_not_called()
    self.assertEqual(json.loads((r.here/'state.json').read_text())['result'],'BLOCKED')
 def test_r2_builder_preserves_111_digest_and_compiles_without_remote_calls(self):
  m=load('prepare-approved-exporters.py')
  with tempfile.TemporaryDirectory() as d:
   out=Path(d);a={'hostname':'infra-project-gestion','allocation':{'cores':'2','memory':'2048'}}
   with patch('subprocess.run') as remote:r=m.render(621,out,a);remote.assert_not_called()
   self.assertIn('d375b27b',r['node_image']);self.assertEqual(r['initial_seconds'],180)
   for name in r['file_sha256']:
    if name.endswith('.py'):compile((out/name).read_text(),name,'exec')
 def test_unreviewed_generator_contract_stops_before_staging(self):
  m=load('prepare-approved-exporters.py')
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(AssertionError):m.render(618,Path(d),{})
   self.assertEqual(list(Path(d).iterdir()),[])

 def test_other_bundles_match_live_allocations_and_preserve_pins(self):
  m=load('prepare-approved-exporters.py')
  rows=json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-rollout-authenticated-preflight.json').read_text())
  # No calls to servers: validate all prepared target-specific model and collector contracts.
  lock=json.loads((ROOT/'services/common/phase4-images.json').read_text())
  for ct in [619,623,617,615,614,61211,611,616,610]:
   a=next(r for r in rows if r['ct']==ct)
   with tempfile.TemporaryDirectory() as d:
    out=Path(d);r=m.render(ct,out,a);cpu=int(a['allocation']['cores']);mem=int(a['allocation']['memory'])
    self.assertEqual(r['node_image'],lock['node'][a['hostname']]['image'])
    self.assertEqual(r['initial_seconds'],600 if ct in [611,616,610] else 180)
    helper=(out/'pilot.py').read_text();collector=(out/'node-cgroup.sh').read_text();observer=(out/'observe.py').read_text()
    self.assertIn(f"mem['MemTotal'] == {mem} * 1024 and cpus == {cpu}",helper)
    self.assertIn(f'cores%s {cpu}\\n',collector)
    self.assertIn(f"['cpu_count']=={cpu}",observer)
    self.assertIn(f'=={mem}*1024*1024',observer)
 def test_orbit_checks_backend_200_separately_from_acl_403(self):
  import urllib.error
  m=load('prepare-approved-exporters.py');a=next(r for r in json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-rollout-authenticated-preflight.json').read_text()) if r['ct']==617)
  with tempfile.TemporaryDirectory() as d:
   out=Path(d);m.render(617,out,a);spec=importlib.util.spec_from_file_location('orbit',out/'pilot.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
   from unittest.mock import MagicMock
   response=MagicMock();response.__enter__.return_value.status=200
   inspect_result=json.dumps([{'NetworkSettings':{'Networks':{'internal':{'IPAddress':'172.20.0.2'}}}}]).encode()
   denied=urllib.error.HTTPError('http://example.invalid',403,'denied',{},None)
   with patch.object(helper.subprocess,'check_output',return_value=inspect_result),patch.object(helper.urllib.request,'urlopen',side_effect=[denied,response]):
    result=helper.application_probe();self.assertEqual(result['status'],200);self.assertEqual([x['status'] for x in result['read_only_application_checks']],[403,200])
   response.__enter__.return_value.status=503
   with patch.object(helper.subprocess,'check_output',return_value=inspect_result),patch.object(helper.urllib.request,'urlopen',side_effect=[denied,response]):
    with self.assertRaises(AssertionError):helper.application_probe()
 def test_probe_failure_keeps_private_detail_out_of_exception(self):
  m=load('rollout-approved-exporters.py')
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'bundle').mkdir();(root/'bundle/sample.py').write_text('pass')
   r=object.__new__(m.Runner);r.ct=621;r.here=root
   r.remote=Mock(return_value=json.dumps({'probe_error':True,'ct_traceback':'File "sample.py", line 123\nAssertionError: private-value'}))
   with self.assertRaises(RuntimeError) as err:r.sample()
   self.assertIn('123',str(err.exception));self.assertNotIn('private-value',str(err.exception))

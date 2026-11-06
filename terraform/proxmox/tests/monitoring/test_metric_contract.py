import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

class ContractTests(unittest.TestCase):
 def setUp(self):
  self.m=load('exporter_metric_contract.py');self.cpu=load('exporter-cpu-alignment.py');self.ram=load('exporter-memory-alignment.py');self.cid='a'*64;self.actual=json.loads((ROOT/'tests/monitoring/fixtures/phase4-actual-incidents.json').read_text())
 def test_real_61211_timestamp_is_parsed_by_one_shared_implementation(self):
  f=self.actual['timestamp61211'];self.assertEqual(self.m.timestamp(f['timestamp']),f['expected_epoch'])
  for kind in ['cpu','memory']:
   ns={'__name__':'inline'};exec(self.m.render_alignment_source(kind).split("\nif __name__=='__main__':")[0],ns)
   self.assertEqual(ns['timestamp'](f['timestamp']),f['expected_epoch']);self.assertNotIn('__file__',ns)
 def test_timestamp_variants_invalid_naive_and_units_fail_closed(self):
  for text in ['2026-11-06T11:06:36','NaN','2026-11-06T11:06:36.1234567890Z','2026-99-06T11:06:36Z']:
   with self.assertRaises((ValueError,AssertionError)):self.m.timestamp(text)
  for val in [None,True,'1',float('nan'),float('inf'),-1]:
   with self.assertRaises(AssertionError):self.m.cpu_seconds(val,'ns')
  self.assertEqual(self.m.cpu_seconds(1000000000,'ns'),1);self.assertEqual(self.m.cpu_seconds(1000000,'us'),1)
  with self.assertRaises(AssertionError):self.m.cpu_seconds(1,'percent')
 def test_full_leaf_identity_rejects_prefix_suffix_parent_and_traversal(self):
  for path in [self.cid,'/docker/'+self.cid,'/system.slice/docker-'+self.cid+'.scope']:self.assertTrue(self.m.exact_id(path,self.cid))
  for path in [self.cid+'b','/docker-'+self.cid+'.scope/nested','/../docker/'+self.cid,'/docker-'+self.cid[:12]+'.scope']:self.assertFalse(self.m.exact_id(path,self.cid))
  with self.assertRaises(AssertionError):self.m.exact_id(self.cid,'a'*12)
 def test_missing_invalid_and_duplicate_samples_are_never_replaced_by_zero(self):
  for text in ['m NaN','m Inf','m -1','m 1 abc','m 1 2 garbage']:
   with self.assertRaises((AssertionError,ValueError)):self.m.prom_rows(text,'m')
  self.assertEqual(self.m.prom_rows('other 3','m'),[])
  rows=self.m.prom_rows('m{id="'+self.cid+'",name="app"} 1 1793963196740','m');self.assertEqual(rows[0]['timestamp'],1793963196.740)
  c={'id':self.cid,'name':'app','started_at':'gen','running':True};s={'cadvisor':{'m':rows*2},'containers':[c]}
  with self.assertRaises(AssertionError):self.m.metric(s,'m',c)
  with self.assertRaises(AssertionError):self.m.active(s|{'containers':[c,c]})
 def test_cpu_total_is_not_confused_with_legitimate_per_core_series(self):
  c={'id':self.cid,'name':'app','started_at':'gen','running':True};r={'labels':{'id':self.cid,'name':'app','cpu':'total'},'value':5,'timestamp':100};core=copy.deepcopy(r);core['labels']['cpu']='cpu00'
  s={'cadvisor':{'container_cpu_usage_seconds_total':[r,core]}}
  self.assertEqual(self.m.metric(s,'container_cpu_usage_seconds_total',c),r)
  s['cadvisor']['container_cpu_usage_seconds_total']=[core]
  with self.assertRaises(AssertionError):self.m.metric(s,'container_cpu_usage_seconds_total',c)
 def test_history_duplicate_reverse_nonfinite_and_partial_append(self):
  for points in [[{'time':1},{'time':1}],[{'time':2},{'time':1}],[{'time':float('nan')},{'time':2}],[{'time':1},{'time':4}]]:
   with self.assertRaises(AssertionError):self.m.bracket(points,1.5)
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'h';p.write_text('{"time":1}\n{"partial":');self.assertEqual(self.m.read_history(p,0,2),[{'time':1}])
   p.write_text('{"bad":\n')
   with self.assertRaises(ValueError):self.m.read_history(p,0,2)
 def test_real_619_cached_comparison_fails_and_measured_bounds_pass_original_tolerance(self):
  for p in self.actual['cpu619']:
   self.assertGreater(abs(p['cadvisor_seconds']-p['unaligned_current_docker_seconds']),self.cpu.tolerance(p['unaligned_current_docker_seconds']))
   for k in ['aligned_docker_seconds','aligned_cgroup_seconds']:
    self.assertLessEqual(abs(p['cadvisor_seconds']-p[k]),self.cpu.tolerance(p[k]))
   for bounds in p['bounds'].values():
    for value in bounds:self.assertLessEqual(abs(p['cadvisor_seconds']-value),self.cpu.tolerance(value))
 def test_real_623_cadence_violation_is_not_hidden_by_last_seen(self):
  p=self.actual['cadence623'];self.assertFalse(p['original_failed_sample_available'])
  with self.assertRaises(AssertionError):self.m.fresh(1793963000,1793963000+p['gap_seconds'])
  self.assertEqual(self.m.LIMITS['metric_age_seconds'],p['limit_seconds'])
 def test_real_617_ram_error_preserves_absence_of_historical_evidence(self):
  p=self.actual['ram617'];self.assertFalse(p['ram_history_at_metric_time_available'])
  self.assertGreater(abs(p['cadvisor_bytes']-p['docker_bytes']),self.ram.allowance(p['docker_bytes'],p['container']))
  self.assertEqual(self.ram.allowance(p['docker_bytes'],p['container']),p['original_allowance_bytes'])
 def test_actual_live_ram_brackets_replay_under_the_strict_common_contract(self):
  proof=self.actual['ram_live'];s={'containers':[],'cadvisor':{'container_memory_usage_bytes':[]},'measurement_scope':'legacy-replay-ct623'};history=[]
  for cid,p in proof.items():
   for point in p['bracket']:point['measurement_scope']='legacy-replay-ct623'
   s['containers'].append({'id':cid,'name':p['name'],'started_at':p['started_at'],'running':True});s['cadvisor']['container_memory_usage_bytes'].append({'labels':{'id':cid,'name':p['name']},'value':p['cadvisor_bytes'],'timestamp':p['time']});history.extend(p['bracket'])
  with patch.object(self.ram.time,'time',return_value=max(p['time'] for p in proof.values())+1):self.assertEqual(self.ram.aligned_evidence(s,history),proof)
 def test_memory_accounting_views_include_file_and_shared_without_double_counting(self):
  views=self.m.memory_views(100,{'file':40,'shmem':10,'inactive_file':20});self.assertEqual((views['usage_bytes'],views['working_set_bytes'],views['docker_cli_bytes'],views['proxmox_net_bytes']),(100,80,80,60))
  # Docker CLI and cAdvisor differ at the defensive inactive>=usage boundary.
  views=self.m.memory_views(100,{'file':100,'shmem':0,'inactive_file':100});self.assertEqual((views['working_set_bytes'],views['docker_cli_bytes']),(0,100))
  with self.assertRaises(AssertionError):self.m.memory_views(100,{'file':40,'shmem':41,'inactive_file':20})
 def test_dead_or_reused_collector_pid_is_an_explicit_framework_error(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'memory-history.jsonl';p.with_name('memory-history-process.json').write_text('{"pid":123}')
   with patch.object(self.m.Path,'read_bytes',return_value=b''):
    with self.assertRaisesRegex(AssertionError,'collector stopped'):self.m.require_collector(p,'memory-alignment.py')
   with patch.object(self.m.Path,'read_bytes',return_value=b'python3\0unrelated.py\0'):
    with self.assertRaises(AssertionError):self.m.require_collector(p,'memory-alignment.py')
 def test_cpu_proof_cannot_be_tampered_independently_of_raw_metric(self):
  r={'labels':{'id':self.cid,'name':'app'},'value':10,'timestamp':101};s={'containers':[{'id':self.cid,'name':'app','started_at':'gen','running':True}],'cadvisor':{'container_cpu_usage_seconds_total':[r]},'cpu_alignment':{self.cid:{'name':'app','started_at':'gen','time':101,'cadvisor_seconds':11,'docker_seconds':11,'cgroup_seconds':11,'bounds':{'docker_seconds':[11,11],'cgroup_seconds':[11,11]}}}}
  s['measurement_scope']='fixture';s['cpu_alignment'][self.cid]['measurement_scope']='fixture'
  with patch.object(self.cpu.time,'time',return_value=102),self.assertRaisesRegex(AssertionError,'raw metric'):self.cpu.validate_alignment(s)

 def test_identical_cloned_docker_ids_cannot_mix_lxc_histories(self):
  c={'id':self.cid,'name':'app','started_at':'cloned-generation','running':True};sample={'containers':[c],'measurement_contract_schema':self.m.SCHEMA,'measurement_scope':'ct624|cgroup:1'}
  scoped=self.m.active(sample)[self.cid]
  history=[{'id':self.cid,'name':'app','started_at':'cloned-generation','time':t,'docker_seconds':1,'cgroup_seconds':1,'measurement_scope':'ct626|cgroup:2'} for t in [100,101]]
  with self.assertRaisesRegex(AssertionError,'scope mismatch'):self.m.points(history,scoped,['docker_seconds','cgroup_seconds'])
  for p in history:p['measurement_scope']=sample['measurement_scope']
  self.assertEqual(self.m.points(history,scoped,['docker_seconds','cgroup_seconds']),history)
 def test_reentry_revision_is_stable_and_changes_with_validation_inputs(self):
  builder=load('prepare-617-memory.py');audit=next(r for r in json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-rollout-authenticated-preflight.json').read_text()) if r['ct']==61211)
  with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
   first=builder.render(Path(a),audit);second=builder.render(Path(b),audit)
   self.assertEqual(first['framework_revision'],second['framework_revision'])
   self.assertIn(first['framework_revision'],(Path(a)/'pilot.py').read_text());self.assertNotIn('-ram-v1-held',(Path(a)/'pilot.py').read_text())
   self.assertEqual(first['measurement_contract_sha256'],second['measurement_contract_sha256'])
   generic=load('prepare-aligned-exporters.py');names=first['file_sha256'];before=generic.revision_for(Path(a),names)
   self.assertEqual(before,first['framework_revision']);path=Path(a)/'memory-alignment.py';path.write_text(path.read_text()+'\n# different validation source\n');self.assertNotEqual(generic.revision_for(Path(a),names),before)
 def test_capture_keeps_real_units_and_docker_identity_and_timestamp(self):
  import time
  with tempfile.TemporaryDirectory() as d:
   cg=Path(d)/('docker-'+self.cid+'.scope');cg.mkdir();(cg/'cpu.stat').write_text('usage_usec 1000000\n');(cg/'memory.current').write_text('100\n');(cg/'memory.stat').write_text('anon 50\nfile 40\nshmem 10\ninactive_file 20\n')
   def read():
    return {'id':self.cid,'name':'/app','read':'2026-11-06T11:06:36.74017Z','cpu_stats':{'cpu_usage':{'total_usage':1000000000}},'memory_stats':{'usage':100,'stats':{'file':40,'shmem':10,'inactive_file':20}}}
   when=self.m.timestamp(read()['read'])
   with patch.object(time,'time',side_effect=[when-.001,when+.001]):p=self.m.capture(cg,read,self.cid,'app','gen')
   self.assertEqual(p['cpu']['docker_seconds'],1);self.assertEqual(p['cpu']['cgroup_seconds'],1);self.assertEqual(p['memory']['docker_bytes'],100);self.assertEqual(p['memory']['cgroup_before'],100)
   def wrong():return read()|{'id':'b'*64}
   with patch.object(time,'time',side_effect=[when-.001,when+.001]),self.assertRaisesRegex(AssertionError,'ID mismatch'):self.m.capture(cg,wrong,self.cid,'app','gen')

 def test_overlapping_cpu_window_bounds_can_have_signed_lower_delta_without_negative_counter(self):
  c={'id':self.cid,'name':'app','started_at':'gen','running':True}
  def sample(t):return {'measurement_scope':'fixture','containers':[c],'cadvisor':{'container_cpu_usage_seconds_total':[{'labels':{'id':self.cid,'name':'app'},'value':1,'timestamp':t}]},'cpu_alignment':{self.cid:{'name':'app','started_at':'gen','time':t,'measurement_scope':'fixture','cadvisor_seconds':1,'docker_seconds':1.2,'cgroup_seconds':1.2,'bounds':{'docker_seconds':[1,1.4],'cgroup_seconds':[1,1.4]}}}}
  with patch.object(self.cpu.time,'time',return_value=102):self.cpu.validate_alignment(sample(101.2),sample(100.8))


 def test_common_candidate_factory_preserves_conventional_and_observability_windows(self):
  builder=load('prepare-aligned-exporters.py');audits=json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-rollout-authenticated-preflight.json').read_text())
  for ct in [61211,611,616,610]:
   with tempfile.TemporaryDirectory() as d:
    manifest=builder.render(Path(d),next(r for r in audits if r['ct']==ct))
    self.assertEqual((manifest['initial_seconds'],manifest['initial_minimum_samples']),(600,21) if ct==610 else (180,7))
    self.assertIn('memory_alignment',manifest);self.assertEqual(manifest['measurement_contract_schema'],self.m.SCHEMA)
 def test_generated_sampler_uses_the_same_parser_without_external_module_installation(self):
  import ast
  builder=load('prepare-aligned-exporters.py');audit=next(r for r in json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-rollout-authenticated-preflight.json').read_text()) if r['ct']==61211)
  with tempfile.TemporaryDirectory() as d:
   out=Path(d);builder.render(out,audit);tree=ast.parse((out/'sample.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='rows')
   ns={'Path':Path,'CPU_HISTORY_PATH':str(out/'cpu-history.jsonl')};exec(compile(ast.Module(body=[fn],type_ignores=[]),'rows','exec'),ns)
   self.assertEqual(ns['rows']('metric 2 1793963196740','metric')[0]['timestamp'],1793963196.740)


 def test_optimized_python_cannot_disable_validation_gates(self):
  import subprocess,sys
  result=subprocess.run([sys.executable,'-O',str(ROOT/'scripts/exporter_metric_contract.py')],capture_output=True,text=True)
  self.assertNotEqual(result.returncode,0);self.assertIn('assertions disabled',result.stderr)


 def test_live_validation_rejects_unspecified_lxc_or_engine_scope(self):
  with self.assertRaisesRegex(AssertionError,'Measurement scope required'):self.m.active({'containers':[{'id':self.cid,'name':'app','started_at':'gen','running':True}]})


if __name__=='__main__':unittest.main()

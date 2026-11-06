"""Incremental merge must preserve legacy configuration and refuse unproved promotion."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('incremental',ROOT/'scripts/prepare-incremental-monitoring.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class IncrementalTests(unittest.TestCase):
 def setUp(self):
  self.services=m.generator.load_services()
  self.state=yaml.safe_load((ROOT/'services/common/exporter-migration.yml').read_text())
  # Freeze historical P0 independently of later successful live migrations.
  journals={'624','625','626'}
  for key in ['cpu_contract_verified','exporters_validated']:
   self.state[key]={k:v for k,v in self.state[key].items() if str(k) in journals}
  self.state['prometheus_integrated']=[];self.state['telegram_chain_verified']=[]
  self.state['remaining_order']=[613,621,620,619,623,617,615,614,61211,618,622,611,616,610]
  pending=[s for s in self.services if int(s['vmid']) not in [624,625,626]]
  config={'scrape_configs':[{'job_name':job,'file_sd_configs':[{'files':['/etc/prometheus/targets/'+name+'.json']}]} for job,name in [('node','node-exporter'),('cadvisor','cadvisor')]]}
  self.baseline={'files':{'prometheus.yml':yaml.safe_dump(config),'targets/node-exporter.json':json.dumps(m.generator.groups_for(pending,9100,'node_exporter')),'targets/cadvisor.json':json.dumps(m.generator.groups_for(pending,8085,'cadvisor')),'targets/blackbox.json':'["sentinel-preserve"]','rules/infra-hosts.yml':(ROOT/'services/infra-prom/config/rules/infra-hosts.yml').read_text()}}

  rows=json.loads(self.baseline['files']['targets/node-exporter.json'])
  for row in rows:row['labels'].pop('cpu_contract',None)
  self.baseline['files']['targets/node-exporter.json']=json.dumps(rows)

 def test_exact_merge_and_repeated_preparation_are_identical(self):
  files,report=m.build(self.baseline,self.state,self.services)
  self.assertEqual((files,report),m.build(self.baseline,self.state,self.services))
  self.assertEqual(files['prometheus.yml'],self.baseline['files']['prometheus.yml'])
  self.assertEqual(files['targets/blackbox.json'],'["sentinel-preserve"]')
  rows=json.loads(files['targets/node-exporter.json'])
  for old in json.loads(self.baseline['files']['targets/node-exporter.json']):self.assertIn(old,rows)
  self.assertEqual(len(rows),17);self.assertEqual(sum(x['labels'].get('cpu_contract')=='lxc_cgroup_v1' for x in rows),3)
  self.assertEqual(report['prometheus_chain_verified_cts'],[])

 def test_duplicate_target_is_rejected(self):
  r=json.loads(self.baseline['files']['targets/node-exporter.json']);r.append(r[0]);self.baseline['files']['targets/node-exporter.json']=json.dumps(r)
  with self.assertRaises(AssertionError):m.build(self.baseline,self.state,self.services)

 def test_prepared_r1_cannot_be_promoted_without_validated_evidence(self):
  self.state['exporters_validated']['613']='docs/roadmap/evidence/2026-11-02-journal626-execution.json'
  with self.assertRaises(AssertionError):m.build(self.baseline,self.state,self.services)

 def test_unrelated_memory_threshold_change_refuses_candidate(self):
  self.baseline['files']['rules/infra-hosts.yml']=self.baseline['files']['rules/infra-hosts.yml'].replace('100 < 10','100 < 11')
  with self.assertRaises(AssertionError):m.build(self.baseline,self.state,self.services)

 def test_missing_target_alert_is_generated_only_for_corrected_inventory(self):
  files,_=m.build(self.baseline,self.state,self.services)
  rs=yaml.safe_load(files['rules/lxc-cpu-inventory.yml'])['groups'][0]['rules']
  self.assertEqual({r['labels']['ct_id'] for r in rs},{'624','625','626'})

 def test_chain_cannot_be_declared_verified_before_integration(self):
  self.state['telegram_chain_verified']=[624]
  with self.assertRaises(AssertionError):m.build(self.baseline,self.state,self.services)

 def test_next_ct_promotion_keeps_previously_integrated_contracts(self):
  import tempfile
  files,_=m.build(self.baseline,self.state,self.services)
  with tempfile.TemporaryDirectory() as tmp:
   proof=Path(tmp)/'point.json';proof.write_text(json.dumps({'ct':613,'result':'PASS','cpu_source':'cgroup_v2_textfile'}))
   self.state['cpu_contract_verified']['613']=str(proof);self.state['remaining_order'].remove(613)
   promoted,report=m.build({'files':files},self.state,self.services)
  self.assertEqual(report['reliable_exporters_cts'],[613,624,625,626])
  rows=json.loads(promoted['targets/node-exporter.json'])
  self.assertEqual(sum(r['labels'].get('cpu_contract')=='lxc_cgroup_v1' for r in rows),4)
  self.assertEqual(len(yaml.safe_load(promoted['rules/lxc-cpu-inventory.yml'])['groups'][0]['rules']),4)


 def test_ram_compatibility_allows_only_exact_source_guard(self):
  files,_=m.build(self.baseline,self.state,self.services)
  doc=yaml.safe_load(files['rules/infra-hosts.yml']);rule=next(r for g in doc['groups'] for r in g['rules'] if r.get('alert')=='HostMemoryFillingFast')
  self.assertEqual(rule['for'],'15m');self.assertIn('4 * 3600',rule['expr']);self.assertIn('changes(node_memory_MemTotal_bytes',rule['expr'])
  old=yaml.safe_load(self.baseline['files']['rules/infra-hosts.yml']);rule=next(r for g in old['groups'] for r in g['rules'] if r.get('alert')=='HostMemoryFillingFast');rule['expr']=rule['expr'].replace('4 * 3600','5 * 3600');self.baseline['files']['rules/infra-hosts.yml']=yaml.safe_dump(old)
  with self.assertRaises(AssertionError):m.build(self.baseline,self.state,self.services)


if __name__=='__main__':unittest.main()

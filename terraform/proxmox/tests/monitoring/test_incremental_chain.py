import copy
import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('chain',ROOT/'scripts/check-incremental-chain.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ChainTests(unittest.TestCase):
 def good(self):return {'ct':613,'targets':[{'labels':{'job':j,'vmid':'613','cpu_contract':'lxc_cgroup_v1'},'health':'up'} for j in ['node_exporter','cadvisor']],'cpu_percent':[{'value':[0,'0']}],'cpu_valid':[{}],'native_cpu':[],'rules':[{'name':n,'health':'ok'} for n in ['HostHighCpuUsage','LxcCpuCollectorInvalid','LxcCpuTargetMissing']]}
 def test_real_zero_is_allowed_but_absence_nan_and_duplicates_fail(self):
  self.assertEqual(m.assess(self.good()),[])
  for rows in [[],[{'value':[0,'NaN']}],[{'value':[0,'0']}]*2]:
   d=self.good();d['cpu_percent']=rows;self.assertTrue(m.assess(d))
 def test_duplicate_targets_and_shared_native_cpu_are_not_accepted(self):
  for field,value in [('native_cpu',[{}]),('cpu_valid',[])]:
   d=self.good();d[field]=value;self.assertTrue(m.assess(d))
  d=self.good();d['targets'].append(d['targets'][0]);self.assertTrue(m.assess(d))
 def test_controlled_notification_uses_actual_exporter_backed_record(self):
  rule=m.verification_rule(613,'R1_test')['groups'][0]['rules'][0]
  self.assertEqual(rule['expr'],'lxc:cpu_usage:percent{ct_id="613"} >= 0')
  self.assertTrue(m.verification_rule(613,'R1_test',False)['groups'][0]['rules'][0]['expr'].endswith('< 0'))
 def test_rule_unhealthy_or_missing_is_not_chain_success(self):
  d=self.good();d['rules'][0]['health']='err';self.assertTrue(m.assess(d))
if __name__=='__main__':unittest.main()

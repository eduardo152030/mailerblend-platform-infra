import importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import yaml
ROOT=Path(__file__).resolve().parents[2]
s=importlib.util.spec_from_file_location('proposal',ROOT/'scripts/prepare-619-recovery.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class ProposalTests(unittest.TestCase):
 def test_only_cadvisor_memory_changes_and_proposal_remains_unapproved(self):
  audit=next(r for r in json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-rollout-authenticated-preflight.json').read_text()) if r['ct']==619)
  spec=importlib.util.spec_from_file_location('base',ROOT/'scripts/prepare-approved-exporters.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
  with tempfile.TemporaryDirectory() as d:
   a=Path(d)/'old';b=Path(d)/'new'
   with patch('subprocess.run') as remote:old=base.render(619,a,audit);new=m.render(b,audit);remote.assert_not_called()
   self.assertTrue(new['approval_required']);self.assertEqual(new['initial_seconds'],600);self.assertEqual(old['cadvisor_image'],new['cadvisor_image']);self.assertEqual(old['node_image'],new['node_image'])
   changed={n for n in old['file_sha256'] if (a/n).read_bytes()!=(b/n).read_bytes()};self.assertEqual(changed,{'pilot.py','cadvisor-limits.yml'})
   ns={'__name__':'recovery_helper'};exec((b/'pilot.py').read_text(),ns)
   ns['ALLOW_CONTAINERD_SOCKET']=True;ns['USE_LXC_CGROUP_CPU']=True
   self.assertTrue(ns['project']('cadvisor').endswith('-cadvisor-containerd-m256'))
   self.assertTrue(ns['project']('node_exporter').endswith('-node-cgroup'))
   for suffix in ['-cadvisor-containerd','-cadvisor-containerd-m256']:
    self.assertTrue(ns['managed']({'Config':{'Labels':{'com.docker.compose.project':ns['PROJECT']+suffix}}}))
   before=yaml.safe_load((a/'cadvisor-limits.yml').read_text());after=yaml.safe_load((b/'cadvisor-limits.yml').read_text());self.assertEqual(before['services']['cadvisor']['cpus'],after['services']['cadvisor']['cpus']);self.assertEqual(after['services']['cadvisor']['mem_limit'],'256m')
 def test_wrong_target_cannot_prepare_override(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(AssertionError):m.render(Path(d),{'ct':618,'hostname':'infra-composable-crm'})

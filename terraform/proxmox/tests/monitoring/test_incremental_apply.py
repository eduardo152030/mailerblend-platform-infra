import importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('apply_inc',ROOT/'scripts/apply-incremental-config.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ApplyTests(unittest.TestCase):
 def test_unchanged_apply_never_reloads(self):
  with tempfile.TemporaryDirectory() as d:
   base=Path(d)/'live';work=Path(d)/'stage'
   for p in [base/'config/rules',base/'config/targets',work/'candidate/rules']:p.mkdir(parents=True)
   (base/'config/prometheus.yml').write_text('scrape_configs: []');(base/'config/rules/infra-hosts.yml').write_text('groups: []')
   (work/'candidate/rules/infra-hosts.yml').write_text('groups: []')
   hashes={p:m.digest(base/'config'/p) for p in ['prometheus.yml','rules/infra-hosts.yml']}
   (work/'manifest.json').write_text(json.dumps({'baseline_sha256':hashes,'candidate_sha256':hashes}))
   (work/'state.json').write_text(json.dumps({'identity':{'stable':True},'applied':[],'backup_sha256':'hash'}))
   (work/'backup-verified.json').write_text('{"offhost_verified":true,"sha256":"hash"}')
   with patch.object(m,'BASE',base),patch.object(m,'identity',return_value={'stable':True}),patch.object(m,'reload') as reload:
    m.install(work,['rules/infra-hosts.yml']);m.install(work,['rules/infra-hosts.yml']);reload.assert_not_called()
 def test_unverified_backup_blocks_all_writes(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'manifest.json').write_text('{}');(p/'state.json').write_text('{"backup_sha256":"hash"}');(p/'backup-verified.json').write_text('{"offhost_verified":false}')
   with patch.object(m,'replace_file') as replace:
    with self.assertRaises(AssertionError):m.install(p,m.RULES)
    replace.assert_not_called()
 def test_atomic_write_keeps_mode_and_skips_identical_content(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'rule';p.write_bytes(b'old');p.chmod(0o640)
   self.assertTrue(m.replace_file(p,b'new'));self.assertEqual(p.stat().st_mode&0o777,0o640)
   self.assertFalse(m.replace_file(p,b'new'))
 def test_snapshot_includes_real_root_compose_file_and_restores_it_in_staging(self):
  import tarfile
  with tempfile.TemporaryDirectory() as tmp:
   base=Path(tmp)/'live';work=Path(tmp)/'stage';work.mkdir()
   for name in ['config/rules','config/targets','.runtime']:(base/name).mkdir(parents=True,exist_ok=True)
   (base/'config/prometheus.yml').write_text('scrape_configs: []');(base/'docker-compose.yml').write_text('services: {}')
   for n in ['alertmanager.yml','telegram_bot_token']:(base/'.runtime'/n).write_text('fixture-not-a-real-secret')
   hashes={'prometheus.yml':m.digest(base/'config/prometheus.yml')}
   (work/'manifest.json').write_text(json.dumps({'baseline_sha256':hashes}))
   with patch.object(m,'BASE',base),patch.object(m,'identity',return_value={'stable':True}):m.snapshot(work)
   with tarfile.open(work/'integration-before.tar') as a:self.assertIn('docker-compose.yml',a.getnames())
   self.assertEqual((work/'restore-check/docker-compose.yml').read_text(),'services: {}')

if __name__=='__main__':unittest.main()

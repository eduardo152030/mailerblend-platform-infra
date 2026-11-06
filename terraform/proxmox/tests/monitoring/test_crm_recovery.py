import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest import mock
import yaml

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('crm_backup',ROOT/'scripts/crm-cold-backup.py')
backup=importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup)
identity_spec=importlib.util.spec_from_file_location('crm_identity',ROOT/'scripts/validate-crm-recovery.py')
identity=importlib.util.module_from_spec(identity_spec)
identity_spec.loader.exec_module(identity)


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)
        self.root=self.base/'rootfs'
        self.root.mkdir()
        self.plan=json.loads(backup.PLAN.read_text())
        self.bundle=self.base/'bundle'
        for role,name in self.plan['volumes'].items():
            p=self.root/'var/lib/docker/volumes'/name/'_data'
            p.mkdir(parents=True)
            (p/'persistent-data').write_text(role+' fixture only')
            (p/'persistent-data').chmod(0o640)
        p=self.root/self.plan['configuration_path']
        p.mkdir(parents=True)
        (p/'.env').write_text('FIXTURE_SECRET=never-production\n')
        (p/'.env').chmod(0o600)

    def test_full_bundle_roundtrip_preserves_all_dependencies_and_modes(self):
        backup.backup(self.root,self.bundle,self.plan)
        restored=self.base/'restored'
        backup.restore(self.bundle,restored)
        for role in self.plan['volumes']:
            self.assertEqual((restored/role/'persistent-data').read_text(),role+' fixture only')
            self.assertEqual((restored/role/'persistent-data').stat().st_mode & 0o777,0o640)
        self.assertEqual((restored/'configuration/.env').stat().st_mode & 0o777,0o600)
        self.assertEqual(self.bundle.stat().st_mode & 0o777,0o700)

    def test_corruption_is_rejected_before_restore(self):
        backup.backup(self.root,self.bundle,self.plan)
        p=self.bundle/'budibase-app.tar'
        with p.open('ab') as f:f.write(b'corrupt')
        with self.assertRaisesRegex(ValueError,'checksum'):
            backup.restore(self.bundle,self.base/'restore')
        self.assertFalse((self.base/'restore').exists())

    def test_repeated_backup_verifies_existing_point_without_overwrite(self):
        first=backup.backup(self.root,self.bundle,self.plan)
        stamp=(self.bundle/'manifest.json').stat().st_mtime_ns
        second=backup.backup(self.root,self.bundle,self.plan)
        self.assertEqual(first,second)
        self.assertEqual(stamp,(self.bundle/'manifest.json').stat().st_mtime_ns)

    def test_restore_refuses_nonempty_destination(self):
        backup.backup(self.root,self.bundle,self.plan)
        dest=self.base/'restore';dest.mkdir();(dest/'existing-data').write_text('keep')
        with self.assertRaises(ValueError):backup.restore(self.bundle,dest)
        self.assertEqual((dest/'existing-data').read_text(),'keep')

    def test_unsafe_archive_path_is_rejected(self):
        p=self.base/'unsafe.tar'
        with tarfile.open(p,'w') as t:
            entry=tarfile.TarInfo('../escape');entry.size=1;t.addfile(entry,io.BytesIO(b'x'))
        with self.assertRaises(ValueError):backup.archive_safe(p)

    def test_backup_cannot_be_written_inside_source_root(self):
        with self.assertRaises(ValueError):backup.backup(self.root,self.root/'backup',self.plan)

    def test_cli_writes_require_execute_and_plan_is_read_only(self):
        r=subprocess.run([sys.executable,str(ROOT/'scripts/crm-cold-backup.py'),'backup'],capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0)
        r=subprocess.run([sys.executable,str(ROOT/'scripts/crm-cold-backup.py'),'plan'],capture_output=True,text=True)
        self.assertEqual(r.returncode,0)

    def test_running_ct_blocks_backup_before_writes(self):
        args=['crm-cold-backup.py','backup','--execute','--rootfs',str(self.root),'--destination',str(self.bundle)]
        with mock.patch.object(sys,'argv',args), mock.patch.object(backup.subprocess,'check_output',return_value='status: running'):
            with self.assertRaisesRegex(ValueError,'already be stopped'):
                backup.main()
        self.assertFalse(self.bundle.exists())

    def test_symlink_destination_is_rejected(self):
        backup.backup(self.root,self.bundle,self.plan)
        target=self.base/'target';target.mkdir()
        link=self.base/'link';link.symlink_to(target,target_is_directory=True)
        with self.assertRaises(ValueError):backup.restore(self.bundle,link)
        self.assertEqual(list(target.iterdir()),[])

    def test_identity_guard_rejects_swapped_volumes_and_mutable_image(self):
        values={line.split('=',1)[0]:line.split('=',1)[1] for line in
                (ROOT/'services/infra-composable-crm/recovery/recovery.env.example').read_text().splitlines()
                if line and not line.startswith('#')}
        identity.validate(values,self.plan)
        swapped=values.copy()
        swapped['BUDIBASE_APP_DATA_VOLUME']=values['BUDIBASE_WORKER_DATA_VOLUME']
        with self.assertRaises(ValueError):identity.validate(swapped,self.plan)
        changed=values.copy();changed['BUDIBASE_RECOVERY_IMAGE']='budibase/budibase:latest'
        with self.assertRaises(ValueError):identity.validate(changed,self.plan)

    def test_recovery_overlay_keeps_both_external_volumes_and_pins_image(self):
        overlay=yaml.safe_load((ROOT/'services/infra-composable-crm/compose/budibase/docker-compose.recovery.yml').read_text())
        self.assertEqual(overlay['services']['budibase-worker']['profiles'],['legacy-duplicate-worker'])
        for service in ['budibase-app','budibase-worker']:
            self.assertEqual(overlay['services'][service]['pull_policy'],'never')
            self.assertIn('/data',overlay['services'][service]['volumes'][0])
        self.assertTrue(all(v['external'] for v in overlay['volumes'].values()))
        self.assertEqual(self.plan['observed_release'],'3.27.4')
        self.assertTrue(self.plan['image'].startswith('budibase/budibase@sha256:'))


if __name__=='__main__':
    unittest.main()

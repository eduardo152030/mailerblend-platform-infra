"""Safety checks for prepared Phase 2 changes; no remote commands or Docker engine."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import yaml

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('budibase_preflight', ROOT/'scripts/validate-budibase-topology.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Phase2SafetyTests(unittest.TestCase):
    def test_current_duplicate_monolith_is_blocked(self):
        config = yaml.safe_load(module.DEFAULT.read_text())
        with self.assertRaisesRegex(ValueError, 'second complete stack'):
            module.validate(config)

    def test_anonymous_monolith_data_cannot_be_recreated_blindly(self):
        with self.assertRaisesRegex(ValueError, 'existing /data volume'):
            module.validate({'services':{'budibase-app':{'image':'budibase/budibase:tested'}}})

    def test_explicit_data_mount_for_single_stack_passes(self):
        module.validate({'services':{'budibase-app':{'image':'budibase/budibase:tested',
                                                   'volumes':['preserved-data:/data']}}})

    def test_dedicated_worker_is_not_mistaken_for_a_monolith(self):
        module.validate({'services':{'budibase-app':{'image':'budibase/apps:tested'},
                                    'budibase-worker':{'image':'budibase/worker:tested'}}})

    def test_start_script_does_not_call_docker_when_preflight_fails(self):
        with tempfile.TemporaryDirectory() as td:
            directory = Path(td)
            marker = directory/'docker-called'
            docker = directory/'docker'
            docker.write_text('#!/bin/sh\ntouch "$CHECK_DOCKER_LOG"\nexit 0\n')
            docker.chmod(0o700)
            env = dict(os.environ, PATH=str(directory)+os.pathsep+os.environ['PATH'], CHECK_DOCKER_LOG=str(marker))
            result = subprocess.run(['bash',str(ROOT/'services/infra-composable-crm/scripts/up-budibase.sh')],
                                    env=env,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertFalse(marker.exists())

    def test_eva_log_retention_is_bounded(self):
        config = yaml.safe_load((ROOT/'services/infra-eva-assistant-bot/compose/docker-compose.yml').read_text())
        for name, service in config['services'].items():
            self.assertEqual(service['logging'], {'driver':'json-file','options':{'max-size':'20m','max-file':'5'}},name)

    def test_eva_maintenance_never_deletes_data(self):
        config = yaml.safe_load((ROOT/'services/infra-eva-assistant-bot/compose/docker-compose.yml').read_text())
        command = config['services']['docker-cleanup']['entrypoint'][-1]
        self.assertIn('docker system df',command)
        self.assertNotIn('prune',command)
        self.assertNotIn('rm ',command)
        self.assertNotIn('truncate',command)


if __name__ == '__main__':
    unittest.main()

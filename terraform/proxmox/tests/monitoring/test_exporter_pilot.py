"""Conservative pilot guards, without SSH or a real Docker daemon."""
import importlib.util
from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('pilot',ROOT/'scripts/exporter-pilot-624.py')
pilot=importlib.util.module_from_spec(spec);spec.loader.exec_module(pilot)


class PilotTests(unittest.TestCase):
    def test_wrong_host_is_rejected_before_docker(self):
        with patch.object(pilot.socket,'gethostname',return_value='infra-eva-assistant-bot'),patch.object(pilot,'run') as run:
            with self.assertRaises(AssertionError):pilot.scope_guard()
            run.assert_not_called()

    def test_wrong_ip_is_rejected(self):
        with patch.object(pilot.socket,'gethostname',return_value='infra-journal-web'),patch.object(pilot,'run',return_value=b'[]'):
            with self.assertRaises(AssertionError):pilot.scope_guard()

    def test_model_cannot_include_application_or_mutable_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            for config in [{'services':{'app':{}}},{'services':{'cadvisor':{'image':'cadvisor:latest'}}}]:
                with patch.object(pilot,'run',return_value=json.dumps(config).encode()):
                    with self.assertRaises(AssertionError):pilot.model(Path(tmp),'cadvisor')

    def test_compose_numeric_memory_strings_are_normalized(self):
        config={'services':{'node_exporter':{'image':pilot.NODE_IMAGE,'pull_policy':'never','container_name':'node_exporter','volumes':[{'read_only':True}],'mem_limit':str(48*1024*1024)}}}
        with patch.object(pilot,'run',return_value=json.dumps(config).encode()):
            model,fingerprint=pilot.model(Path('/tmp/fixture'),'node_exporter')
            self.assertEqual(len(fingerprint),64)

    def test_new_socket_cannot_be_selected_without_explicit_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp);(path/'cadvisor-containerd.yml').write_text('services: {}')
            self.assertNotIn(str(path/'cadvisor-containerd.yml'),pilot.compose(path,'cadvisor'))
            with patch.object(pilot,'ALLOW_CONTAINERD_SOCKET',True):
                self.assertIn(str(path/'cadvisor-containerd.yml'),pilot.compose(path,'cadvisor'))
                self.assertNotIn(str(path/'cadvisor-containerd.yml'),pilot.compose(path,'node_exporter'))

    def test_revising_cadvisor_requires_explicit_socket_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(AssertionError):pilot.revise_cadvisor(Path(tmp))

    def test_apply_cannot_run_without_verified_offhost_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)
            (path/'baseline.json').write_text('{"archives":{}}')
            (path/'external-backup-verified.json').write_text('{"offhost_verified":false,"archives":{}}')
            with patch.object(pilot,'run') as run:
                with self.assertRaises(AssertionError):pilot.apply(path)
                run.assert_not_called()

    def test_model_drift_refuses_up_before_stopping_exporter(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)
            (path/'baseline.json').write_text('{"archives":{},"exporters":{}}')
            (path/'external-backup-verified.json').write_text('{"offhost_verified":true,"archives":{}}')
            (path/'applied.json').write_text('{"node_exporter":{"hash":"old","id":"id"}}')
            current={'Id':'id','Config':{'Labels':{'com.docker.compose.project':pilot.PROJECT}}}
            with patch.object(pilot,'unchanged'),patch.object(pilot,'capacity'),patch.object(pilot,'model',return_value=({},'new')),patch.object(pilot,'run',return_value=b'[{"Id":"image"}]') as run,patch.object(pilot,'docker_info',return_value=current),patch.object(pilot,'stop') as stop:
                with self.assertRaises(AssertionError):pilot.apply(path)
                stop.assert_not_called()
                self.assertFalse(any('up' in c.args[0] for c in run.call_args_list))

    def test_repeated_apply_never_stops_or_recreates_exporters(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)
            (path/'baseline.json').write_text('{"archives":{},"exporters":{}}')
            (path/'external-backup-verified.json').write_text('{"offhost_verified":true,"archives":{}}')
            records={name:{'id':name,'hash':'approved'} for name in pilot.SERVICES}
            (path/'applied.json').write_text(json.dumps(records))
            def info(name):
                if name not in pilot.SERVICES:return None
                node=name=='node_exporter'
                return {'Id':name,'Image':'image','Config':{'Labels':{'com.docker.compose.project':pilot.PROJECT}},'HostConfig':{'Memory':(48 if node else 128)*1024*1024,'NanoCpus':200000000 if node else 500000000},'Mounts':[{'RW':False}]}
            def command(args,**kwargs):
                return b'[{"Id":"image"}]' if args[1:3]==['image','inspect'] else b''
            with patch.object(pilot,'unchanged'),patch.object(pilot,'capacity'),patch.object(pilot,'model',return_value=({},'approved')),patch.object(pilot,'ready'),patch.object(pilot,'docker_info',side_effect=info),patch.object(pilot,'run',side_effect=command) as run,patch.object(pilot,'stop') as stop:
                pilot.apply(path);pilot.apply(path)
                stop.assert_not_called()
                calls=[c.args[0] for c in run.call_args_list if 'up' in c.args[0]]
                self.assertEqual(len(calls),4)
                self.assertTrue(all('--no-recreate' in c for c in calls))
                self.assertFalse(any('rename' in c.args[0] for c in run.call_args_list))

    def test_mount_order_does_not_change_configuration_identity(self):
        c={'Config':{'Cmd':['web']},'HostConfig':{'Memory':0},'Mounts':[{'Source':'/b','Destination':'/b'},{'Source':'/a','Destination':'/a'}]}
        before=pilot.config_hash(c)
        c['Mounts'].reverse()
        self.assertEqual(pilot.config_hash(c),before)
        c['Config']['Cmd']=['changed']
        self.assertNotEqual(pilot.config_hash(c),before)

    def test_revised_cadvisor_uses_distinct_project_to_avoid_adopting_rejected(self):
        original=pilot.project('cadvisor')
        with patch.object(pilot,'ALLOW_CONTAINERD_SOCKET',True):
            self.assertNotEqual(pilot.project('cadvisor'),original)
            self.assertEqual(pilot.project('node_exporter'),pilot.PROJECT)
            self.assertTrue(pilot.managed({'Config':{'Labels':{'com.docker.compose.project':pilot.project('cadvisor')}}}))

    def test_stop_has_no_kill_fallback(self):
        with patch.object(pilot,'docker_info',return_value={'State':{'Running':True}}),patch.object(pilot.subprocess,'run') as run:
            run.return_value.returncode=1
            with self.assertRaises(AssertionError):pilot.stop('cadvisor')
            self.assertEqual(run.call_args.args[0],['docker','stop','-t','-1','cadvisor'])

    def test_rollback_is_available_after_failed_web_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)
            (path/'baseline.json').write_text('{"exporters":{"node_exporter":null,"cadvisor":null}}')
            with patch.object(pilot,'docker_info',return_value=None),patch.object(pilot,'unchanged',side_effect=AssertionError('web unavailable')) as unchanged:
                with self.assertRaises(AssertionError):pilot.rollback(path)
                # Called at end, not as a prerequisite that could prevent rollback.
                self.assertEqual(unchanged.call_count,1)


if __name__=='__main__':unittest.main()

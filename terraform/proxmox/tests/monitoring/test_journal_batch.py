"""Preparation is local-only; runtime idempotence must still be demonstrated after approval."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('journal_prepare',ROOT/'scripts/prepare-journal-exporters.py')
prepare=importlib.util.module_from_spec(spec);spec.loader.exec_module(prepare)


class JournalBatchTests(unittest.TestCase):
    def load(self,ct,path):
        prepare.render(ct,path)
        spec=importlib.util.spec_from_file_location('journal_'+str(ct),path/'pilot.py')
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        m.ALLOW_CONTAINERD_SOCKET=True;m.USE_LXC_CGROUP_CPU=True
        return m

    def test_only_two_approved_for_preparation_cts(self):
        with tempfile.TemporaryDirectory() as d:
            for ct in [624,618,622,100]:
                with self.assertRaises(ValueError):prepare.render(ct,Path(d))

    def test_preparation_is_reproducible_and_never_connects(self):
        with tempfile.TemporaryDirectory() as d,patch.object(subprocess,'run') as run:
            for ct in [625,626]:
                path=Path(d)/str(ct);a=prepare.render(ct,path);before={p.name:p.read_bytes() for p in path.iterdir()}
                self.assertEqual(a,prepare.render(ct,path));self.assertEqual(before,{p.name:p.read_bytes() for p in path.iterdir()})
            run.assert_not_called()

    def test_snapshot_directory_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'baseline.json').write_text('{}')
            with self.assertRaises(AssertionError):prepare.render(625,p)

    def test_real_two_cpu_collector_and_malformed_counters(self):
        for ct in [625,626]:
            with self.subTest(ct=ct),tempfile.TemporaryDirectory() as d:
                p=Path(d);bundle=p/'bundle';prepare.render(ct,bundle)
                root=p/'host'
                for part in ['etc','proc','sys/fs/cgroup']:(root/part).mkdir(parents=True,exist_ok=True)
                (root/'etc/hostname').write_text(prepare.TARGETS[ct][0]+'\n')
                (root/'proc/stat').write_text('cpu 0\ncpu1 0\ncpu2 0\n')
                stat=root/'sys/fs/cgroup/cpu.stat';stat.write_text('usage_usec 1000000\nuser_usec 600000\nsystem_usec 400000\n')
                env=dict(os.environ,PILOT_HOST_ROOT=str(root),PILOT_METRIC_DIR=str(p/'metrics'))
                cmd=['sh',str(bundle/'node-cgroup.sh'),'--once']
                r=subprocess.run(cmd,env=env,capture_output=True);self.assertEqual(r.returncode,0)
                text=(p/'metrics/lxc-cpu.prom').read_text();self.assertIn('ct_id="'+str(ct)+'"',text)
                self.assertRegex(text,r'lxc_cpu_capacity_cores\{[^}]+\} 2\n')
                stat.write_text('usage_usec invalid\nuser_usec 1\nsystem_usec 1\n')
                self.assertNotEqual(subprocess.run(cmd,env=env,capture_output=True).returncode,0)
                self.assertNotIn('lxc_cpu_usage_seconds_total',(p/'metrics/lxc-cpu.prom').read_text())

    def test_helper_refuses_socket_and_cpu_without_explicit_flags(self):
        with tempfile.TemporaryDirectory() as d:
            m=self.load(625,Path(d));m.ALLOW_CONTAINERD_SOCKET=False
            with self.assertRaises(AssertionError):m.apply(Path(d))

    def test_generated_observer_accepts_two_cpu_samples_and_rejects_wrong_ct(self):
        import copy
        for ct in [625,626]:
            with self.subTest(ct=ct),tempfile.TemporaryDirectory() as d:
                p=Path(d);prepare.render(ct,p)
                spec=importlib.util.spec_from_file_location('batch_observer',p/'observe.py')
                observer=importlib.util.module_from_spec(spec);spec.loader.exec_module(observer)
                sample=json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-pilot624-metric-samples.json').read_text())['first']
                name='infra-journal-db-db-1' if ct==625 else 'infra-journal-api-api-1'
                sample=json.loads(json.dumps(sample).replace('infra-journal-web-web-1',name).replace('infra-journal-web','infra-journal-db' if ct==625 else 'infra-journal-api').replace('"ct_id": "624"','"ct_id": "'+str(ct)+'"'))
                sample['resources']['memory.max']=str(2048*1024*1024)
                sample['lxc_proc']['cpu_count']=2
                sample['node']['node_memory_MemTotal_bytes'][0]['value']=2048*1024*1024
                sample['node']['lxc_cpu_capacity_cores'][0]['value']=2
                for row in sample['cadvisor']['container_memory_usage_bytes']:
                    if row['labels'].get('name')==name:row['labels']['container_label_com_docker_compose_service']='db' if ct==625 else 'api'
                observer.validate(sample,sample)
                bad=copy.deepcopy(sample);bad['node']['lxc_cpu_usage_seconds_total'][0]['labels']['ct_id']='624'
                with self.assertRaises(AssertionError):observer.validate(bad,sample)

    def test_two_applies_keep_exporter_identity_and_do_not_stop_or_recreate(self):
        for ct in [625,626]:
            with self.subTest(ct=ct),tempfile.TemporaryDirectory() as d:
                p=Path(d);m=self.load(ct,p)
                (p/'baseline.json').write_text('{"archives":{},"exporters":{}}')
                (p/'external-backup-verified.json').write_text('{"offhost_verified":true,"archives":{}}')
                (p/'applied.json').write_text(json.dumps({n:{'id':n,'hash':'planned'} for n in m.SERVICES}))
                def info(n):
                    if n not in m.SERVICES:return None
                    node=n=='node_exporter'
                    return {'Id':n,'Image':'image','Config':{'Labels':{'com.docker.compose.project':m.project(n)}},'HostConfig':{'Memory':(48 if node else 128)*1024*1024,'NanoCpus':200000000 if node else 500000000},'Mounts':[{'RW':False}]}
                def run(a,**kw):return b'[{"Id":"image"}]' if a[1:3]==['image','inspect'] else b''
                with patch.object(m,'containerd_socket_ready',return_value=True),patch.object(m,'unchanged'),patch.object(m,'capacity'),patch.object(m,'ready'),patch.object(m,'model',return_value=({},'planned')),patch.object(m,'docker_info',side_effect=info),patch.object(m,'run',side_effect=run) as command,patch.object(m,'stop') as stop:
                    m.apply(p);m.apply(p)
                    stop.assert_not_called()
                    ups=[c.args[0] for c in command.call_args_list if 'up' in c.args[0]]
                    self.assertEqual(len(ups),4);self.assertTrue(all('--no-recreate' in a and 'never' in a for a in ups))


if __name__=='__main__':unittest.main()

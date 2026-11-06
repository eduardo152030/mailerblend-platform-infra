import copy
import json
import tempfile
import os
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
import yaml

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('eva_model',ROOT/'scripts/generate-eva-storage-compose.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class StorageModelTests(unittest.TestCase):
    def setUp(self):
        self.base=yaml.safe_load((ROOT/'services/infra-eva-assistant-bot/compose/docker-compose.yml').read_text())
        self.images={name:'sha256:'+'a'*64 for name in self.base['services']}

    def test_model_preserves_data_environment_commands_and_resources(self):
        before=copy.deepcopy(self.base)
        compiled=module.compile_config(self.base,self.images)
        self.assertEqual(self.base,before)
        for name,service in self.base['services'].items():
            actual=compiled['services'][name].copy();actual.pop('pull_policy');actual['image']=service['image']
            self.assertEqual(actual,service)
        self.assertEqual(compiled['networks'],{'default':{'name':'eva-network','external':True}})

    def test_missing_image_and_mutable_image_are_rejected(self):
        missing=self.images.copy();missing.pop(next(iter(missing)))
        with self.assertRaises(ValueError):module.compile_config(self.base,missing)
        wrong=self.images.copy();wrong[next(iter(wrong))]='image:latest'
        with self.assertRaises(ValueError):module.compile_config(self.base,wrong)

    def test_runtime_preflight_uses_image_defaults_and_rejects_environment_drift(self):
        source=(ROOT/'scripts/apply-eva-preserving-logging.sh').read_text()
        checker=source.split("<<'PY_CHECK'\n",1)[1].split('\nPY_CHECK',1)[0]
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            docker=directory/'docker'
            docker.write_text("#!/usr/bin/env python3\nimport json,sys,os\nmodel={'image':'sha256:fixed','command':None,'entrypoint':None,'environment':{'PRIVATE':'kept'}}\nimage={'Id':'sha256:fixed','Config':{'Env':['BASE=ok'],'Cmd':['server'],'Entrypoint':['entry']}}\nruntime={'Image':'sha256:fixed','Config':{'Env':['BASE=ok','PRIVATE='+os.environ.get('TEST_PRIVATE','kept')],'Cmd':['server'],'Entrypoint':['entry']}}\nif os.environ.get('TEST_ENTRYPOINT'): model['entrypoint']=['entry'];runtime['Config']['Cmd']=None\nprint(json.dumps({'services':{'eva-api':model}} if sys.argv[1]=='compose' else [image if sys.argv[1]=='image' else runtime]))\n")
            docker.chmod(0o700)
            env=dict(os.environ,PATH=tmp+os.pathsep+os.environ['PATH'])
            good=subprocess.run([sys.executable,'-c',checker,'eva-api','eva-api'],env=env,capture_output=True,text=True)
            self.assertEqual(good.returncode,0,good.stderr)
            overridden=subprocess.run([sys.executable,'-c',checker,'eva-api','eva-api'],env=dict(env,TEST_ENTRYPOINT='1'),capture_output=True,text=True)
            self.assertEqual(overridden.returncode,0,overridden.stderr)
            bad=subprocess.run([sys.executable,'-c',checker,'eva-api','eva-api'],env=dict(env,TEST_PRIVATE='private-sentinel'),capture_output=True,text=True)
            self.assertNotEqual(bad.returncode,0)
            self.assertNotIn('private-sentinel',bad.stdout+bad.stderr)

    def test_readiness_timeout_aborts_before_database_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            script=directory/'rollout-eva-storage.sh'
            script.write_text((ROOT/'scripts/rollout-eva-storage.sh').read_text())
            (directory/'apply-eva-preserving-logging.sh').write_text('#!/bin/sh\nexit 0\n')
            (directory/'python3').write_text('#!/bin/sh\nif [ "$2" = api ]; then exit 1; fi\nexec '+sys.executable+' "$@"\n')
            (directory/'docker').write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$DOCKER_TRACE"\n')
            for name in ['python3','docker']:(directory/name).chmod(0o700)
            record=directory/'verified.json';record.write_text(json.dumps(dict(backup_verified=True,offhost_verified=True,restore_verified=True)))
            baseline=directory/'baseline.json';baseline.write_text('[]')
            trace=directory/'docker.trace'
            env=dict(os.environ,PATH=tmp+os.pathsep+os.environ['PATH'],DOCKER_TRACE=str(trace),READINESS_TIMEOUT='1',READINESS_INTERVAL='1')
            result=subprocess.run(['bash',str(script),'--execute',str(record),str(baseline)],env=env,capture_output=True,text=True,timeout=10)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('Readiness timeout',result.stderr)
            self.assertNotIn('stop',trace.read_text() if trace.exists() else '')

    def test_force_exception_rejects_active_tasks_and_application_mounts(self):
        source=(ROOT/'scripts/stop-eva-container.sh').read_text()
        checker=source.split("<<'PY_IDLE'\n",1)[1].split('\nPY_IDLE',1)[0]
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp);docker=directory/'docker'
            docker.write_text("#!/usr/bin/env python3\nimport json,sys,os\nif sys.argv[1]=='top': print('PID COMMAND\\n1 '+('docker' if os.environ.get('ACTIVE_JOB') else 'sh')+'\\n2 sleep')\nelse: print(json.dumps([{'State':{'Running':True},'Mounts':[{'Destination':'/app/data' if os.environ.get('APP_DATA') else '/var/run/docker.sock'}]}]))\n")
            docker.chmod(0o700)
            env=dict(os.environ,PATH=tmp+os.pathsep+os.environ['PATH'])
            for extra,success in [({},True),({'ACTIVE_JOB':'1'},False),({'APP_DATA':'1'},False)]:
                result=subprocess.run([sys.executable,'-c',checker,'eva-docker-cleanup'],env=dict(env,**extra),capture_output=True,text=True)
                self.assertEqual(result.returncode==0,success,result.stderr)

    def test_mutating_helpers_require_explicit_execution(self):
        for script in ['eva-storage-maintenance.sh','apply-eva-preserving-logging.sh','apply-crm-preserving-recovery.sh','rollout-eva-storage.sh','stop-eva-container.sh']:
            r=subprocess.run(['bash',str(ROOT/'scripts'/script)],capture_output=True,text=True)
            self.assertEqual(r.returncode,2,script)


if __name__=='__main__':unittest.main()

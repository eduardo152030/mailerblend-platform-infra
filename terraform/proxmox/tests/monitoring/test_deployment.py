"""Local deployment state-machine tests. Docker, curl and remote services are stubs."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / 'scripts/apply-monitoring.sh'
STUB = r'''#!/usr/bin/env python3
import json, os, pathlib, sys
p=pathlib.Path(os.environ['MOCK_STATE']); d=json.loads(p.read_text()); args=sys.argv[1:]
if pathlib.Path(sys.argv[0]).name == 'docker':
    if args[0]=='inspect':
        service=args[-1]; s=d['services'][service]
        if 'exit=' in args[2]: print('status='+s['status']+' exit=2 restarting=false')
        else: print(s['id'],s['started'],s['status'])
    elif args[0]=='logs':
        print('failed token='+d['secret']+' https://api.telegram.org/bot'+d['secret']+'/sendMessage')
    elif args[0]=='kill':
        service=args[-1]; d['signals'].append(service)
        if not d.get('no_confirmation'): d['stamp'][service]+=1
    elif args[:3]==['compose','up','-d']:
        for service, change in d.get('changes',{}).items(): d['services'][service].update(change)
else:
    service='prometheus' if ':9090/' in args[-1] else 'alertmanager'
    if args[-1].endswith('/-/ready'):
        d['polls'][service]+=1
        if d.get('timeout') or d['polls'][service] <= d.get('delay',0):
            p.write_text(json.dumps(d));sys.exit(22)
    else:
        print(service+'_config_last_reload_success_timestamp_seconds',d['stamp'][service])
        print(service+'_config_last_reload_successful',0 if d.get('reject') and d['signals'] else 1)
p.write_text(json.dumps(d))
'''


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'bin').mkdir()
        for name in ['docker', 'curl']:
            p = self.root/'bin'/name
            p.write_text(STUB)
            p.chmod(0o700)
        for name in ['config/rules', 'config/targets', 'config/alertmanager/templates', '.runtime']:
            (self.root/name).mkdir(parents=True, exist_ok=True)
        (self.root/'config/prometheus.yml').write_text('initial prometheus')
        (self.root/'.runtime/alertmanager.yml').write_text('initial alertmanager')
        self.secret = '123456789:TEST_SECRET_MUST_NOT_APPEAR'
        (self.root/'.runtime/telegram_bot_token').write_text(self.secret)
        self.data = {'services': {s: {'id':s+'-id', 'started':'old', 'status':'running'}
                                  for s in ['prometheus', 'alertmanager']},
                     'stamp':{'prometheus':1,'alertmanager':1}, 'polls':{'prometheus':0,'alertmanager':0},
                     'signals':[], 'secret':self.secret}
        self.state = self.root/'state.json'
        self.env = dict(os.environ, PATH=str(self.root/'bin')+os.pathsep+os.environ['PATH'],
                        MONITORING_DIR=str(self.root), MOCK_STATE=str(self.state))

    def run_mode(self, mode, success=True, timeout=3):
        self.state.write_text(json.dumps(self.data))
        result = subprocess.run(['bash',str(SCRIPT),mode,str(timeout),'1'],env=self.env,
                                capture_output=True,text=True,timeout=15)
        self.data = json.loads(self.state.read_text())
        self.assertEqual(result.returncode == 0, success, result.stdout+result.stderr)
        self.assertNotIn(self.secret,result.stdout+result.stderr)
        return result

    def change_config(self):
        (self.root/'.runtime/alertmanager.yml').write_text('new chat id')

    def test_unchanged_running_containers_are_not_signalled(self):
        self.run_mode('snapshot'); self.run_mode('apply')
        self.assertEqual(self.data['signals'],[])

    def test_only_changed_running_service_reloads_and_repeat_is_noop(self):
        self.run_mode('snapshot'); self.change_config(); self.run_mode('apply')
        self.assertEqual(self.data['signals'],['alertmanager'])
        self.run_mode('snapshot'); self.run_mode('apply')
        self.assertEqual(self.data['signals'],['alertmanager'])

    def test_recreated_containers_are_not_signalled(self):
        self.run_mode('snapshot'); self.change_config()
        self.data['changes']={s:{'id':'new-'+s,'started':'new'} for s in self.data['services']}
        self.run_mode('apply'); self.assertEqual(self.data['signals'],[])

    def test_same_id_restarted_is_not_signalled(self):
        self.run_mode('snapshot'); self.change_config()
        self.data['changes']={'alertmanager':{'started':'new'}}
        self.run_mode('apply'); self.assertEqual(self.data['signals'],[])

    def test_stopped_container_started_by_compose_is_not_signalled(self):
        self.data['services']['alertmanager']['status']='exited'
        self.run_mode('snapshot'); self.change_config()
        self.data['changes']={'alertmanager':{'started':'new','status':'running'}}
        self.run_mode('apply'); self.assertEqual(self.data['signals'],[])

    def test_missing_container_created_by_compose_is_not_signalled(self):
        self.data['services']['alertmanager'].update(id='missing',started='missing',status='missing')
        self.run_mode('snapshot'); self.change_config()
        self.data['changes']={'alertmanager':{'id':'new','started':'new','status':'running'}}
        self.run_mode('apply'); self.assertEqual(self.data['signals'],[])

    def test_exit_diagnostics_and_failure_status(self):
        self.run_mode('snapshot')
        self.data['changes']={'alertmanager':{'status':'exited'}}
        r=self.run_mode('apply',success=False)
        self.assertIn('exit=2',r.stderr);self.assertIn('[REDACTED]',r.stderr)
        self.assertEqual(self.data['signals'],[])

    def test_readiness_timeout_fails(self):
        self.run_mode('snapshot');self.data['timeout']=True
        r=self.run_mode('apply',success=False,timeout=1)
        self.assertIn('readiness timed out',r.stderr)

    def test_rejected_reload_fails_and_retry_reloads(self):
        self.run_mode('snapshot');self.change_config();self.data['reject']=True
        r=self.run_mode('apply',success=False)
        self.assertIn('rejected',r.stderr)
        self.data['reject']=False
        self.run_mode('snapshot');self.run_mode('apply')
        self.assertEqual(self.data['signals'],['alertmanager','alertmanager'])

    def test_delayed_readiness_retries_before_reload(self):
        self.run_mode('snapshot');self.change_config();self.data['delay']=1
        self.run_mode('apply',timeout=4)
        self.assertGreaterEqual(self.data['polls']['alertmanager'],2)
        self.assertEqual(self.data['signals'],['alertmanager'])

    def test_missing_reload_confirmation_fails(self):
        self.run_mode('snapshot');self.change_config();self.data['no_confirmation']=True
        r=self.run_mode('apply',success=False,timeout=1)
        self.assertIn('did not confirm',r.stderr)

    def test_invalid_timeout_rejected(self):
        r=subprocess.run(['bash',str(SCRIPT),'apply','invalid','1'],env=self.env,capture_output=True,text=True)
        self.assertEqual(r.returncode,2)


if __name__ == '__main__':
    unittest.main()

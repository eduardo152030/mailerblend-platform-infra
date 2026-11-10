#!/usr/bin/env python3
"""Healthcheck behavior with real local HTTP responses; no production writes."""
import importlib.util,json,subprocess,threading,unittest,sys,copy
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
s=importlib.util.spec_from_file_location('recipes',ROOT/'scripts/generate-d051-healthchecks.py');recipes=importlib.util.module_from_spec(s);s.loader.exec_module(recipes)
s=importlib.util.spec_from_file_location('budibase',ROOT/'services/infra-composable-crm/recovery/healthchecks/budibase.py');budibase=importlib.util.module_from_spec(s);s.loader.exec_module(budibase)
s=importlib.util.spec_from_file_location('repair',ROOT/'scripts/repair-d051-healthchecks.py');repair=importlib.util.module_from_spec(s);s.loader.exec_module(repair)
class HTTP(BaseHTTPRequestHandler):
 code=200;body=b'{"db":"ok"}'
 def do_GET(self):self.send_response(self.code);self.end_headers();self.wfile.write(self.body)
 def log_message(self,*args):pass
class Checks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.server=ThreadingHTTPServer(('127.0.0.1',0),HTTP);cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
 @classmethod
 def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
 def run_probe(self,name):
  cmd=recipes.recipes()[name]['test'][1:];cmd=[x.replace(':8080/',':'+str(self.server.server_port)+'/').replace('/8000','/'+str(self.server.server_port)) for x in cmd]
  if cmd[0]=='python':cmd[0]=sys.executable
  return subprocess.run(cmd,capture_output=True,timeout=6).returncode
 def test_focalboard_200_passes(self):HTTP.code=200;self.assertEqual(self.run_probe('focalboard'),0)
 def test_focalboard_400_fails(self):HTTP.code=400;self.assertNotEqual(self.run_probe('focalboard'),0)
 def test_focalboard_503_fails(self):HTTP.code=503;self.assertNotEqual(self.run_probe('focalboard'),0)
 def test_api_ready_passes(self):HTTP.code=200;HTTP.body=b'{"db":"ok"}';self.assertEqual(self.run_probe('crm-api'),0)
 def test_api_db_down_fails(self):HTTP.code=200;HTTP.body=b'{"db":"down"}';self.assertNotEqual(self.run_probe('crm-api'),0)
 def test_api_503_fails(self):HTTP.code=503;self.assertNotEqual(self.run_probe('crm-api'),0)
 def budi(self,pong='PONG',passing=True,couch='ok'):
  def get(url,auth=False):
   if '/api/system/status' in url:return json.dumps({'health':{'passing':passing}}).encode()
   if '/_up' in url:return json.dumps({'status':couch}).encode()
   return b'ok'
  def run(args,**kw):
   if args[0]=='redis-cli':
    self.assertIn('redis.internal',args);self.assertIn('6380',args);self.assertNotIn('s@cret',str(args));self.assertEqual(kw['env']['REDISCLI_AUTH'],'s@cret')
    return subprocess.CompletedProcess(args,0,pong,'')
   return subprocess.CompletedProcess(args,0,'','')
  with patch.dict('os.environ',{'REDIS_URL':'redis://default:s%40cret@redis.internal:6380','COUCH_DB_URL':'http://u:p@couch.internal:5984'}),patch.object(budibase,'get',get),patch.object(budibase.subprocess,'run',run):budibase.check()
 def test_budibase_external_authenticated_topology_passes(self):self.budi()
 def test_budibase_wrongpass_fails(self):
  with self.assertRaises(RuntimeError):self.budi(pong='WRONGPASS')
 def test_budibase_health_false_fails(self):
  with self.assertRaises(RuntimeError):self.budi(passing=False)
 def test_budibase_couch_down_fails(self):
  with self.assertRaises(RuntimeError):self.budi(couch='down')
 def test_budibase_http_503_fails(self):
  with patch.object(budibase,'get',side_effect=RuntimeError('HTTP503')),self.assertRaises(RuntimeError):budibase.check()
class Invariants(unittest.TestCase):
 def fixture(self):return {'Config':{'Env':['A=1']},'HostConfig':{'Dns':[]},'Image':'same','Mounts':[{'Type':'volume','Source':'/data/original','Destination':'/data','RW':True}],'NetworkSettings':{'Networks':{'existing':{}}},'State':{'OOMKilled':False}}
 def test_empty_dns_representations_are_equivalent(self):
  a=self.fixture();b=copy.deepcopy(a);b['HostConfig']['Dns']=None;repair.invariant(a,b)
 def test_bind_api_representations_preserve_effective_mounts(self):
  a=self.fixture();b=copy.deepcopy(a);a['HostConfig']['Binds']=['/data/original:/data:rw'];b['HostConfig']['Binds']=None;repair.invariant(a,b)
 def test_real_dns_change_is_rejected(self):
  a=self.fixture();b=copy.deepcopy(a);b['HostConfig']['Dns']=['192.0.2.1']
  with self.assertRaises(AssertionError):repair.invariant(a,b)
 def test_data_volume_replacement_is_rejected(self):
  a=self.fixture();b=copy.deepcopy(a);b['Mounts'][0]['Source']='/data/different'
  with self.assertRaises(AssertionError):repair.invariant(a,b)
 def test_environment_change_is_rejected(self):
  a=self.fixture();b=copy.deepcopy(a);b['Config']['Env']=['A=2']
  with self.assertRaises(AssertionError):repair.invariant(a,b)
if __name__=='__main__':unittest.main()

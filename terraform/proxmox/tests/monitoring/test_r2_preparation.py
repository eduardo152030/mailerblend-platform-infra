import ast,importlib.util,json,os,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('r2',ROOT/'scripts/prepare-r2-exporters.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class R2Tests(unittest.TestCase):
 def test_only_r2_and_exact_installed_versions_are_prepared(self):
  lock=json.loads((ROOT/'services/common/phase4-images.json').read_text())
  with tempfile.TemporaryDirectory() as d:
   for ct in [621,620]:
    p=Path(d)/str(ct);r=m.render(ct,p);self.assertEqual(r['node_image'],lock['node'][m.TARGETS[ct]['host']]['image']);self.assertEqual(r['initial_seconds'],180);self.assertEqual(r['interval_seconds'],30)
    for f in p.glob('*.py'):ast.parse(f.read_text())
   with self.assertRaises(AssertionError):m.render(618,Path(d)/'bad')
 def test_generation_is_stable_across_python_hash_seeds(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);values=[]
   for seed in ['1','77']:
    out=p/seed;subprocess.run(['python3',str(ROOT/'scripts/prepare-r2-exporters.py'),'--ct','620','--output',str(out)],env=dict(os.environ,PYTHONHASHSEED=seed),stdout=subprocess.DEVNULL,check=True);values.append(json.loads((out/'manifest.json').read_text()))
   self.assertEqual(values[0],values[1])
 def test_watch_initial_gate_then_anomaly_extends_and_keeps_halt(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);m.render(621,p);spec=importlib.util.spec_from_file_location('r2watch',p/'observe.py');watch=importlib.util.module_from_spec(spec);spec.loader.exec_module(watch)
   tracker=watch.WindowTracker(180,7,900)
   for t in [0,30,60,90,120,150,180]:status=tracker.observe(t,True)
   self.assertTrue(status['initial_window_passed']);self.assertFalse(status['alert_for_runtime_firing_validated'])
   status=tracker.observe(850,False);self.assertTrue(status['halt_advance']);self.assertFalse(status['initial_window_passed']);self.assertEqual(status['end_after'],1450)
   self.assertFalse(tracker.finished(900));self.assertTrue(tracker.finished(1450))
 def test_application_probe_uses_only_health_and_redis_ping(self):
  from unittest.mock import patch,MagicMock
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);m.render(620,p);spec=importlib.util.spec_from_file_location('r2sample',p/'sample.py');sample=importlib.util.module_from_spec(spec)
   with patch('socket.gethostname',return_value='infra-excraper'):spec.loader.exec_module(sample)
   response=MagicMock();response.__enter__.return_value.status=200;response.__enter__.return_value.read.return_value=b'{"status":"healthy"}'
   with patch.object(sample.urllib.request,'urlopen',return_value=response) as request,patch.object(sample.subprocess,'check_output',return_value=b'PONG') as ping:
    self.assertEqual(sample.application_probe()['status'],200);self.assertEqual(request.call_count,2);self.assertEqual(ping.call_args.args[0],['docker','exec','infra-excraper-redis-1','redis-cli','ping'])
   with patch.object(sample.urllib.request,'urlopen',return_value=response),patch.object(sample.subprocess,'check_output',return_value=b'NOAUTH'):
    with self.assertRaises(AssertionError):sample.application_probe()

if __name__=='__main__':unittest.main()

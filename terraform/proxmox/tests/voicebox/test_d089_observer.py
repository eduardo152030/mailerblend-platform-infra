"""Network loss cannot submit TTS or mutate a completed job."""
import importlib.util,io,json,tempfile,unittest,urllib.error,wave
from pathlib import Path
from unittest.mock import patch
SRC=Path(__file__).resolve().parents[2]/'services/infra-voicebox/validation-d089/resume/observer.py'
spec=importlib.util.spec_from_file_location('d089_read_observer',SRC);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ID='9a8ba53a-6032-4ab0-bfa6-8521e4d1de77'
class Observer(unittest.TestCase):
 def test_network_fallback_reads_same_existing_job(self):
  seen=[]
  def fail(path):seen.append(('direct',path));raise urllib.error.URLError('No route to host')
  def good(path):seen.append(('pve',path));return b'{"status":"completed"}'
  data,route=m.read_api('/history/'+ID,'direct',fail,good)
  self.assertEqual(json.loads(data)['status'],'completed');self.assertTrue(route['fallback']);self.assertEqual(seen,[('direct','/history/'+ID),('pve','/history/'+ID)])
 def test_mutating_endpoints_are_rejected(self):
  for path in ['/generate','/generate/'+ID+'/cancel','/history/'+ID+'?delete=true','/audio/../../generate']:
   with self.assertRaises(ValueError):m.safe_path(path)
 def test_audio_connection_loss_records_observer_error_not_job_failure(self):
  calls=[]
  def read(path,via):
   calls.append(path)
   if path.startswith('/history/'):return b'{"status":"completed"}',{'transport':'fake'}
   raise ConnectionError('synthetic route loss')
  with tempfile.TemporaryDirectory() as d,patch.object(m,'read_api',read):
   p=Path(d)
   with self.assertRaises(ConnectionError):m.observe(ID,p)
   e=json.loads((p/'observer-error.json').read_text());self.assertEqual(e['observation'],'unavailable');self.assertFalse(e['generation_state_modified']);self.assertFalse(e['inference_submitted']);self.assertFalse((p/'verified.json').exists())
   self.assertEqual(json.loads((p/'history.private.json').read_text())['status'],'completed')
  self.assertEqual(calls,['/history/'+ID,'/audio/'+ID])
 def test_truncated_wav_is_rejected(self):
  b=io.BytesIO()
  with wave.open(b,'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(b'\0\0'*240)
  self.assertEqual(m.wav_seconds(b.getvalue()),.01)
  with self.assertRaises(AssertionError):m.wav_seconds(b.getvalue()[:-2])
if __name__=='__main__':unittest.main()

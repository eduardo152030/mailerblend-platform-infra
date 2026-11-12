"""D079 existing-job errors use synthetic local folders, without starting jobs."""
import asyncio,importlib.util,json
from pathlib import Path
import tempfile,time,unittest,uuid
SOURCE=Path(__file__).resolve().parents[2]/'services/infra-voicebox/production-d079/isolated_backend.py'
class RetryMessage(unittest.IsolatedAsyncioTestCase):
 async def check(self,checkpoint):
  spec=importlib.util.spec_from_file_location('d079_fixture',SOURCE);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  with tempfile.TemporaryDirectory() as folder:
   m.ROOT=Path(folder);m.atomic(m.ROOT/'agent-heartbeat.json',{'timestamp':time.time(),'ct':627,'status':'healthy'})
   ident=uuid.uuid4();m.start_context(str(ident));p=m.ROOT/ident.hex;p.mkdir();(p/'original-evidence').write_bytes(b'preserve')
   if checkpoint:(p/'checkpoint').mkdir()
   with self.assertRaises(ValueError) as error:await m.IsolatedQwenBackend().generate('test',{'profile_id':m.OWNER})
   self.assertEqual((p/'original-evidence').read_bytes(),b'preserve');self.assertFalse((p/'request.json').exists());return str(error.exception)
 async def test_absent_does_not_claim_saved_checkpoint(self):
  text=await self.check(False);self.assertIn('no tiene checkpoint',text);self.assertIn('nueva inferencia explícita',text)
 async def test_directory_alone_not_treated_as_valid(self):
  text=await self.check(True);self.assertIn('integridad no se ha verificado',text);self.assertIn('no se repite Talker automáticamente',text)
if __name__=='__main__':unittest.main()

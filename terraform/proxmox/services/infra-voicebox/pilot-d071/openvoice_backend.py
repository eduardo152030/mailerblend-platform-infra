"""Async Voicebox adapter; all ML runs in a separate killable worker process."""
import asyncio,contextvars,io,json,os,time,uuid,urllib.request,urllib.error
from pathlib import Path
import numpy as np,soundfile as sf
OWNER='1fd00418-2a79-4178-883f-af6c3f5e07ee';context=contextvars.ContextVar('openvoice_generation',default=(None,None))
def start_context(ident):context.set((ident,time.monotonic()+360))
class OpenVoiceBackend:
 def __init__(self):self.device='cpu';self.model_size='default';self.ready=False;self.active=None
 def is_loaded(self):return self.ready
 def unload_model(self):self.ready=False
 def _is_model_cached(self):
  try:return self._sync('/health')['status']=='healthy'
  except Exception:return False
 def _sync(self,path,value=None):
  req=urllib.request.Request(os.environ.get('OPENVOICE_URL','http://openvoice:8080')+path,data=None if value is None else json.dumps(value).encode(),headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=8) as r:return json.load(r)
 async def api(self,path,value=None):return await asyncio.to_thread(self._sync,path,value)
 async def load_model(self,*args):
  if (await self.api('/health'))['status']!='healthy':raise ValueError('OpenVoice worker unavailable')
  self.ready=True
 async def create_voice_prompt(self,audio_path,reference_text,use_cache=True):
  expected=Path('/app/data/profiles')/OWNER/'8840f5e1-990b-463e-b94e-e72beef61917.wav'
  if Path(audio_path).resolve()!=expected.resolve() or not expected.is_file() or not reference_text.strip():raise ValueError('Actual owner reference and transcript required')
  return {'profile_id':OWNER},False
 async def combine_voice_prompts(self,*args):raise ValueError('Use the verified owner reference; extra references need review')
 async def generate(self,text,voice_prompt,language='es',seed=None,instruct=None):
  assert language=='es' and voice_prompt['profile_id']==OWNER
  parent,deadline=context.get();deadline=deadline or time.monotonic()+180
  ident=str(uuid.uuid4());self.active=ident
  submission=asyncio.create_task(self.api('/jobs',{'request_id':ident,'profile_id':OWNER,'text':text,'parent_generation_id':parent,'timeout_seconds':max(1,min(240,int(deadline-time.monotonic())))}))
  try:
   await asyncio.shield(submission)
   while time.monotonic()<deadline:
    state=await self.api('/jobs/'+ident)
    if state['status']=='completed':break
    if state['status'] in ['failed','cancelled']:raise ValueError('OpenVoice '+state.get('error',state['status']))
    await asyncio.sleep(.5)
   else:raise TimeoutError('OpenVoice total generation deadline exceeded')
   def download():
    with urllib.request.urlopen(os.environ.get('OPENVOICE_URL','http://openvoice:8080')+'/jobs/'+ident+'/audio',timeout=8) as r:return r.read()
   audio,rate=sf.read(io.BytesIO(await asyncio.to_thread(download)),dtype='float32');return audio,rate
  except BaseException:
   # Wait for known-ID submission so cancellation cannot race an untracked job.
   try:await asyncio.shield(submission)
   except Exception:pass
   try:
    result=await asyncio.shield(self.api('/jobs/'+ident+'/cancel',{}))
    if result['status'] not in ['completed','failed','cancelled']:raise RuntimeError('Worker cancellation did not terminate inference')
   except urllib.error.HTTPError as e:
    if e.code!=404:raise
   raise
  finally:self.active=None

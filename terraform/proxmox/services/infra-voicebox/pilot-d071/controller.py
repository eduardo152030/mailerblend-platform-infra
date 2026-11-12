"""Single-inference internal worker; real process-group cancellation and bounded queue."""
import asyncio,os,json,time,uuid,signal,hashlib
from pathlib import Path
from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse,PlainTextResponse
from pydantic import BaseModel,Field
OWNER='1fd00418-2a79-4178-883f-af6c3f5e07ee';ROOT=Path('/jobs');ROOT.mkdir(exist_ok=True);os.umask(0o077)
app=FastAPI(title='Voicebox personal CPU worker');jobs={};active=None;wake=asyncio.Event();process=None;lock=asyncio.Lock()
class Request(BaseModel):
 profile_id:str
 request_id:str
 text:str=Field(min_length=1,max_length=12000)
 parent_generation_id:str|None=None
 timeout_seconds:int=Field(default=180,ge=1,le=240)
def persist(j):
 (ROOT/j['id']/'state.json').write_text(json.dumps(j,indent=2))
def public(j):return {k:v for k,v in j.items() if k not in ['text']}
async def terminate(proc):
 if proc and proc.returncode is None:
  try:os.killpg(proc.pid,signal.SIGTERM)
  except ProcessLookupError:pass
  try:await asyncio.wait_for(proc.wait(),5)
  except asyncio.TimeoutError:os.killpg(proc.pid,signal.SIGKILL);await proc.wait()
async def run_queue():
 global active,process
 while True:
  queued=next((j for j in jobs.values() if j['status']=='queued'),None)
  if not queued:wake.clear();await wake.wait();continue
  j=queued;active=j['id'];j.update(status='running',started_at=time.time());persist(j);p=ROOT/j['id'];log=(p/'child.log').open('wb')
  try:
   process=await asyncio.create_subprocess_exec('python','/worker/infer.py',str(p),stdout=log,stderr=asyncio.subprocess.STDOUT,start_new_session=True)
   j['pid']=process.pid;persist(j)
   try:
    while process.returncode is None:
     if j['status']=='cancelling':await terminate(process);break
     if time.time()-j['started_at']>j['timeout_seconds']:j['error']='execution_timeout';await terminate(process);break
     # Stop before container's3GiB limit; no model or database resides in this API process.
     current=int(Path('/sys/fs/cgroup/memory.current').read_text())
     j['peak_container_bytes']=max(j.get('peak_container_bytes',0),current)
     if current>=int(2.8*2**30):j['error']='worker_memory_safety_stop';await terminate(process);break
     await asyncio.sleep(.25)
    await process.wait()
   finally:
    if process.returncode is None:await terminate(process)
   if j['status']=='cancelling':j['status']='cancelled'
   elif process.returncode==0 and (p/'result.json').is_file():j.update(status='completed',result=json.loads((p/'result.json').read_text()))
   else:j.update(status='failed',error=j.get('error','inference_failed'))
  except BaseException as e:
   await terminate(process);j.update(status='failed',error=type(e).__name__)
  finally:
   log.close();j['finished_at']=time.time();j['pid']=None;persist(j);process=None;active=None
@app.on_event('startup')
async def startup():
 for p in ROOT.glob('*/state.json'):
  j=json.loads(p.read_text())
  if j['status'] in ['running','queued','cancelling']:j.update(status='failed',error='worker_restarted',pid=None);persist(j)
  jobs[j['id']]=j
 asyncio.create_task(run_queue())
@app.get('/health')
def health():
 ready=all(Path('/models',p).is_file() for p in ['converter/checkpoint.pth','melo/checkpoint.pth','source-es.pth','tokenizer/vocab.txt']) and Path('/references/8840f5e1-990b-463e-b94e-e72beef61917.wav').is_file()
 if not ready:raise HTTPException(503,'Pinned models/reference missing')
 return {'status':'healthy','active_jobs':int(active is not None),'queued_jobs':sum(j['status']=='queued' for j in jobs.values())}
@app.post('/jobs',status_code=202)
async def submit(r:Request):
 if r.profile_id!=OWNER:raise HTTPException(403,'Owner profile only')
 async with lock:
  if sum(j['status'] in ['queued','running','cancelling'] for j in jobs.values())>=2:raise HTTPException(429,'Queue full')
  ident=str(uuid.UUID(r.request_id))
  if ident in jobs:
   if jobs[ident]['profile_id']!=r.profile_id or jobs[ident]['text']!=r.text:raise HTTPException(409,'Request ID conflict')
   return public(jobs[ident])
  p=ROOT/ident;p.mkdir(mode=0o700);d=r.model_dump();(p/'request.json').write_text(json.dumps(d,ensure_ascii=False));j={**d,'id':ident,'status':'queued','created_at':time.time()};jobs[ident]=j;persist(j);wake.set();return public(j)
@app.get('/jobs/{ident}')
def status(ident:str):
 if ident not in jobs:raise HTTPException(404,'Unknown job')
 return public(jobs[ident])
@app.post('/jobs/{ident}/cancel')
async def cancel(ident:str):
 if ident not in jobs:raise HTTPException(404,'Unknown job')
 j=jobs[ident]
 if j['status']=='queued':j.update(status='cancelled',finished_at=time.time());persist(j)
 elif j['status']=='running':
  j['status']='cancelling';persist(j)
  for _ in range(80):
   if j['status']!='cancelling':break
   await asyncio.sleep(.1)
  if j['status']=='cancelling':raise HTTPException(503,'Cancellation not reaped yet')
 return public(j)
@app.get('/jobs/{ident}/audio')
def audio(ident:str):
 j=jobs.get(ident)
 if not j:raise HTTPException(404,'Unknown job')
 if j['status']!='completed':raise HTTPException(409,'Job not completed')
 return FileResponse(ROOT/ident/'output.wav',media_type='audio/wav')
@app.get('/metrics',response_class=PlainTextResponse)
def metrics():
 lines=[]
 for s in ['completed','failed','cancelled','queued','running']:
  lines.append(f'voicebox_worker_jobs{{status="{s}"}} {sum(j["status"]==s for j in jobs.values())}')
 lines.append('voicebox_worker_generation_seconds_total '+str(sum(j.get('result',{}).get('elapsed_seconds',0) for j in jobs.values())))
 return '\n'.join(lines)+'\n'

@app.post('/generations/{parent}/cancel')
async def cancel_parent(parent:str):
 for j in list(jobs.values()):
  if j.get('parent_generation_id')==parent and j['status'] in ['queued','running','cancelling']:await cancel(j['id'])
 return {'active_jobs':sum(j.get('parent_generation_id')==parent and j['status'] in ['queued','running','cancelling'] for j in jobs.values())}

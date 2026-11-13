#!/usr/bin/env python3
"""PVE: validación API real630. Sin secretos stdout; descarga entre cargas y guarda21GiB."""
import pathlib,subprocess,json,urllib.request,urllib.error,time,threading,datetime,base64,sys
root=pathlib.Path('/root/ia-local');dest=root/'validation-api.json'
key=subprocess.run(['pct','exec','630','--','cat','/etc/llama/api.key'],capture_output=True,text=True,check=True).stdout.strip()
base='http://192.168.1.67:8080';aliases=['gemma-4-26b','qwen3.6-35b'];out=json.loads(dest.read_text()) if dest.exists() else {}
def save():dest.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
def call(path,data=None,auth=True,timeout=1800):
 req=urllib.request.Request(base+path,data=json.dumps(data).encode() if data is not None else None,headers=({'Authorization':'Bearer '+key} if auth else {})|{'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=timeout) as r:return r.status,json.load(r)
 except urllib.error.HTTPError as e:
  try:body=json.loads(e.read())
  except Exception:body={'error':'HTTP '+str(e.code)}
  return e.code,body

def memory():
 host={x.split(':')[0]:int(x.split()[1])*1024 for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith(('MemAvailable:','SwapTotal:','SwapFree:'))}
 ct={}
 for id in ['630','631']:
  p=pathlib.Path('/sys/fs/cgroup/lxc')/id
  if not (p/'memory.current').exists():continue
  stat={x.split()[0]:int(x.split()[1]) for x in (p/'memory.stat').read_text().splitlines()}
  current=int((p/'memory.current').read_text());maxmem=int((p/'memory.max').read_text())
  ct[id]={'current':current,'working_set':max(0,current-stat.get('inactive_file',0)),'max':maxmem,'anon':stat.get('anon'),'file':stat.get('file'),'mapped_file':stat.get('file_mapped',0),'kernel':stat.get('kernel',0),'resident_tasks':min(current,stat.get('anon',0)+stat.get('file_mapped',0)+stat.get('kernel',0)),'inactive_file':stat.get('inactive_file'),'swap':int((p/'memory.swap.current').read_text()),'events':(p/'memory.events').read_text()}
 procs=[];p=pathlib.Path('/sys/fs/cgroup/lxc/630/ns/system.slice/llama-server.service/cgroup.procs')
 for pid in p.read_text().split() if p.exists() else []:
  try:
   status=pathlib.Path('/proc/'+pid+'/status').read_text();rss=next(int(x.split()[1])*1024 for x in status.splitlines() if x.startswith('VmRSS:'))
   hwm=next((int(x.split()[1])*1024 for x in status.splitlines() if x.startswith('VmHWM:')),rss)
   names=sorted({pathlib.Path(x.split()[-1]).name for x in pathlib.Path('/proc/'+pid+'/maps').read_text().splitlines() if '/models/' in x and '.gguf' in x and 'mmproj' not in x})
   procs.append({'pid':int(pid),'rss':rss,'hwm':hwm,'model_files':names})
  except (OSError,StopIteration):pass
 return {'host':host,'ct':ct,'processes':procs,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}

def unload():
 for a in aliases:call('/models/unload',{'model':a},timeout=60)
 time.sleep(2)

def guard(label):
 m=memory();out.setdefault('guards',[]).append({'label':label,**m});save()
 if m['host']['MemAvailable']<21*1024**3:raise SystemExit('HALT host MemAvailable<21GiB: '+label)
 return m

def request_chat(label,model,prompt,thinking=False,max_tokens=96,unload_first=True,image=None):
 transition_start=time.monotonic()
 if unload_first:unload();guard(label)
 unload_elapsed=time.monotonic()-transition_start
 data={'model':model,'messages':[{'role':'user','content':prompt if image is None else [{'type':'text','text':prompt},{'type':'image_url','image_url':{'url':'data:image/png;base64,'+image}}]}],'stream':True,'max_tokens':max_tokens,'chat_template_kwargs':{'enable_thinking':thinking},'temperature':0.1,'stream_options':{'include_usage':True}}
 samples=[];stop=threading.Event();over=[]
 def watch():
  while not stop.is_set():
   m=memory();samples.append(m)
   distinct={n for p in m['processes'] for n in p['model_files']}
   if len(distinct)>1:over.append('dos modelos grandes mapeados')
   if max(m['ct']['630']['resident_tasks'],sum(p['rss'] for p in m['processes']),sum(p.get('hwm',p['rss']) for p in m['processes']))>0.9*m['ct']['630']['max']:over.append('memoria CT>90%')
   if over:
    subprocess.run(['pct','exec','630','--','systemctl','stop','llama-server'],capture_output=True);return
   stop.wait(1)
 watcher=threading.Thread(target=watch);watcher.start();start=time.monotonic();first=None;content='';reasoning='';usage={};timings={};error=None
 try:
  req=urllib.request.Request(base+'/v1/chat/completions',data=json.dumps(data).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=1800) as r:
   for line in r:
    line=line.decode().strip()
    if not line.startswith('data: ') or line=='data: [DONE]':continue
    item=json.loads(line[6:]);usage=item.get('usage') or usage;timings=item.get('timings') or timings
    if item.get('error'):raise RuntimeError(str(item['error']))
    for choice in item.get('choices',[]):
     delta=choice.get('delta',{});c=delta.get('content') or '';re=delta.get('reasoning_content') or ''
     if (c or re) and first is None:first=time.monotonic()-start
     content+=c;reasoning+=re
 except Exception as e:error=str(e)
 finally:stop.set();watcher.join()
 elapsed=time.monotonic()-start
 result={'model':model,'thinking':thinking,'content':content,'reasoning_chars':len(reasoning),'ttft_s':first,'elapsed_s':elapsed,'unload_guard_s':unload_elapsed,'transition_total_s':time.monotonic()-transition_start,'usage':usage,'timings':timings,'tokens_s':timings.get('predicted_per_second') or (usage.get('completion_tokens',0)/max(.001,elapsed-(first or 0))),'samples':samples,'anomalies':over,'error':error}
 out.setdefault('attempts',[]).append({'label':label,**result});out[label]=result;save()
 if over:raise SystemExit('HALT interno630: '+str(over))
 if error:raise SystemExit('FALLO '+label+': '+error)
 print(label,'HTTP OK',round(elapsed,2),'s',repr(content[:100]),'reasoning_chars',len(reasoning),flush=True)
 return result

stage=sys.argv[1] if len(sys.argv)>1 else 'api'
if stage=='library':pass
elif stage=='api':
 good=call('/v1/models');bad=call('/v1/models',auth=False)
 out['api']={'with_key':good,'without_key':bad};save();assert good[0]==200 and bad[0]==401
 assert set(aliases).issubset({x['id'] for x in good[1]['data']});print('API PASS',flush=True)
elif stage=='chat':
 for i,model in enumerate([aliases[0],aliases[1],aliases[0]],1):
  label='final-cycle-'+str(i)+'-'+model
  r=request_chat(label,model,'Responde en español en una frase: ¿cuánto es 2 + 2?',max_tokens=64)
  assert r['content'].strip()
elif stage=='chat-gemma-return':
 request_chat('chat-gemma-4-26b-return',aliases[0],'Responde en español en una frase: ¿cuánto es 2 + 2?',max_tokens=64)
elif stage=='chat-qwen-reduced':
 request_chat('chat-qwen3.6-35b',aliases[1],'Responde en español en una frase: ¿cuánto es 2 + 2?',max_tokens=64)
 request_chat('chat-gemma-4-26b-return',aliases[0],'Responde en español en una frase: ¿cuánto es 2 + 2?',max_tokens=64)
elif stage=='vision':
 code="from PIL import Image,ImageDraw,ImageFont; im=Image.new('RGB',(900,240),'white'); f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',68); ImageDraw.Draw(im).text((40,80),'PRUEBA 4821',fill='black',font=f); im.save('/root/prueba.png')"
 subprocess.run(['pct','exec','630','--','python3','-c',code],check=True)
 image=base64.b64encode(subprocess.run(['pct','exec','630','--','cat','/root/prueba.png'],capture_output=True,check=True).stdout).decode()
 for model in aliases:
  r=request_chat('vision-'+model,model,'Lee el número de la imagen. Responde solo con el número.',image=image,max_tokens=64);assert '4821' in r['content'],'Vision no leyó4821'
elif stage=='thinking':
 prompt='Ana es mayor que Bea y Bea es mayor que Carla. ¿Quién es la menor? Responde en español.'
 off=request_chat('thinking-off',aliases[1],prompt,thinking=False,max_tokens=128)
 on=request_chat('thinking-on',aliases[1],prompt,thinking=True,max_tokens=384,unload_first=False)
 assert off['reasoning_chars']==0 and on['reasoning_chars']>0 and 'Carla' in on['content'],'Thinking no demostrado'
elif stage=='unload':unload();print('Modelos descargados')
else:raise SystemExit('stage inválida')

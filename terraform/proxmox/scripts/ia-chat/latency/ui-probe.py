#!/usr/bin/env python3
"""Ejecutar dentro de WebUI. Ruta UI real HTTP stream + Socket.IO autenticado.
Solo chats de la fixture; no imprime ni exporta el token. Las respuestas son sintéticas.
"""
import asyncio,json,pathlib,time,uuid,sys,datetime,urllib.request,os
import aiohttp,socketio
BASE='http://127.0.0.1:8080';AUTH=json.loads(pathlib.Path('/app/backend/data/.ia-latency-auth.json').read_text());TOKEN=AUTH['token'];MODEL=os.environ.get('IA_PROBE_MODEL','gemma-4-26b')
def first_token_time(events):
 for item in events:
  event=item.get('event',{});data=event.get('data',{})
  if event.get('type') not in ['response:completion','chat:completion']:continue
  if data.get('type')=='response.output_text.delta' and data.get('delta'):return item['elapsed_s']
  if any(choice.get('delta',{}).get('content') for choice in data.get('choices',[])):return item['elapsed_s']
  if data.get('content'):return item['elapsed_s']
 return None

async def main():
 stage=sys.argv[1];messages=['Hola, ¿qué tal?'] if len(sys.argv)<3 else json.loads(sys.argv[2]);sio=socketio.AsyncClient();received=[];current={};done=asyncio.Event()
 @sio.on('events')
 async def event(data):
  if data.get('message_id')!=current.get('mid'):return
  elapsed=time.monotonic()-current['start'];item=data.get('data',{});received.append({'elapsed_s':elapsed,'event':item})
  if item.get('type') in ['chat:completion','response:completion']:
   val=item.get('data',{});text=val.get('content','')
   if val.get('type')=='response.output_text.delta':
    text=val.get('delta','')
    if text and current.get('ttft') is None:current['ttft']=elapsed
    current['text']+=text;return
   if not text:
    for c in val.get('choices',[]):text+=c.get('delta',{}).get('content','') or ''
   if not text:
    for o in val.get('output',[]):
     for c in o.get('content',[]):text+=c.get('text','') or ''
   if text and current.get('ttft') is None:current['ttft']=elapsed
   if text:current['text']=text
   if val.get('done'):current['usage']=val.get('usage');done.set()
  if item.get('type')=='chat:message:error':current['error']=item.get('data');done.set()
 async with aiohttp.ClientSession(headers={'Authorization':'Bearer '+TOKEN}) as http:
  async def api(path,body):
   async with http.post(BASE+path,json=body,timeout=aiohttp.ClientTimeout(total=1800)) as r:
    assert r.status==200,(path,r.status);return await r.json()
  await sio.connect(BASE,socketio_path='ws/socket.io',auth={'token':TOKEN},transports=['websocket']);sid=sio.get_sid()
  history={};chain=[];parent=None;chat_id=None;results=[]
  for index,prompt in enumerate(messages):
   uid=str(uuid.uuid4());mid=str(uuid.uuid4());now=int(time.time());user={'id':uid,'parentId':parent,'childrenIds':[mid],'role':'user','content':prompt,'timestamp':now};assistant={'id':mid,'parentId':uid,'childrenIds':[],'role':'assistant','content':'','model':MODEL,'done':False,'timestamp':now}
   if parent:history[parent]['childrenIds']=[uid]
   history.update({uid:user,mid:assistant});chain.append({'role':'user','content':prompt})
   chat={'title':'IA latency '+stage,'models':[MODEL],'messages':[history[k] for k in history],'history':{'messages':history,'currentId':mid}}
   if chat_id:await api('/api/v1/chats/'+chat_id,{'chat':chat})
   else:chat_id=(await api('/api/v1/chats/new',{'chat':chat}))['id']
   current.clear();current.update({'mid':mid,'start':time.monotonic(),'ttft':None,'text':''});done.clear();received.clear()
   payload={'model':MODEL,'messages':chain,'stream':True,'session_id':sid,'chat_id':chat_id,'id':mid,'parent_id':parent,'user_message':user,'features':{'web_search':stage.startswith('web-search'),'code_interpreter':False,'image_generation':False},'variables':{'CURRENT_DATE':datetime.datetime.now().strftime('%Y-%m-%d'),'CURRENT_WEEKDAY':datetime.datetime.now().strftime('%A')},'background_tasks':{'title_generation':index==0,'tags_generation':True,'follow_up_generation':True}}
   ack=await api('/api/chat/completions',payload);await asyncio.wait_for(done.wait(),timeout=1500)
   await asyncio.sleep(30) # Capture post-response title tasks before ending the journal window.
   results.append({'message':prompt,'ttft_s':first_token_time(received),'elapsed_s':time.monotonic()-current['start']-30,'text':current['text'],'usage':current.get('usage'),'error':current.get('error'),'events':list(received),'ack_keys':list(ack)})
   chain.append({'role':'assistant','content':current['text']});history[mid].update({'content':current['text'],'done':True});parent=mid
  await sio.disconnect()
  dest=pathlib.Path('/app/backend/data/.ia-latency-'+stage+'.json');dest.write_text(json.dumps({'stage':stage,'chat_id':chat_id,'results':results},indent=2));dest.chmod(0o600)
  print(json.dumps({'stage':stage,'results':[{k:v for k,v in r.items() if k not in ['events']} for r in results]},ensure_ascii=False))
asyncio.run(main())

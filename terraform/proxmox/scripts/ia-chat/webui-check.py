#!/usr/bin/env python3
"""Dentro631: prueba local con usuario técnico efímero; nunca imprime tokens."""
import json,pathlib,urllib.request,urllib.error,secrets,sys,time,subprocess,re,unicodedata,os
base='http://127.0.0.1:3000';cred=pathlib.Path('/root/ia-validation-auth.json');result=pathlib.Path(os.getenv('IA_RESULT_PATH','/root/ia-webui-validation.json'));out=json.loads(result.read_text()) if result.exists() else {}
def save():result.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
def api(path,data=None,method=None,token=None,raw=None,content_type=None):
 headers={}
 if token:headers['Authorization']='Bearer '+token
 if raw is not None:body=raw;headers['Content-Type']=content_type
 elif data is not None:body=json.dumps(data).encode();headers['Content-Type']='application/json'
 else:body=None
 req=urllib.request.Request(base+path,data=body,headers=headers,method=method)
 try:
  with urllib.request.urlopen(req,timeout=1800) as r:
   b=r.read()
   return r.status,json.loads(b) if 'json' in r.headers.get('Content-Type','') else {'bytes':len(b)}
 except urllib.error.HTTPError as e:
  b=e.read()
  return e.code,json.loads(b) if b.startswith(b'{') else {'error':'HTTP '+str(e.code)}
def check(code,data):
 if not 200<=code<300:raise RuntimeError('HTTP '+str(code)+' '+str(data)[:250])
 return data

def upload(path,name,mime,token):
 boundary='ia-'+secrets.token_hex(16)
 body=('--'+boundary+'\r\nContent-Disposition: form-data; name="file"; filename="'+name+'"\r\nContent-Type: '+mime+'\r\n\r\n').encode()+path.read_bytes()+('\r\n--'+boundary+'--\r\n').encode()
 return check(*api('/api/v1/files/?process=true&process_in_background=false',raw=body,content_type='multipart/form-data; boundary='+boundary,token=token))

stage=sys.argv[1]
if stage=='init':
 if cred.exists():auth=json.loads(cred.read_text())
 else:
  password=secrets.token_urlsafe(36);auth=check(*api('/api/v1/auths/signup',{'name':'Verificación técnica temporal IA','email':'ia-chat-validation@example.com','password':password}))
  cred.write_text(json.dumps({'token':auth['token'],'id':auth['id'],'email':auth['email'],'password':password}));cred.chmod(0o600);auth=json.loads(cred.read_text())
 token=auth['token']
 profile=json.loads(pathlib.Path('/opt/ia-chat/chat-performance.json').read_text())
 for id,name in [('gemma-4-26b','Gemma 4 · Chat'),('qwen3.6-35b','Qwen3.6 · Código y razonamiento')]:
  payload={'id':id,'base_model_id':None,'name':name,'meta':{'capabilities':{'vision':True,'file_context':True,'web_search':True,'builtin_tools':profile['builtin_tools']}},'params':{'system':profile['system'],'function_calling':profile['function_calling'],'custom_params':{'cache_prompt':profile['cache_prompt']},'chat_template_kwargs':{'enable_thinking':False},'model_controls':{'thinking':{'label':'Razonamiento','default':'off','options':{'off':{'label':'Desactivado','params':{'chat_template_kwargs':{'enable_thinking':False}}},'on':{'label':'Activado','params':{'chat_template_kwargs':{'enable_thinking':True}}}}}}}}
  code,data=api('/api/v1/models/create',payload,token=token)
  if code>=300:
   if 'taken' in str(data).lower() or 'already registered' in str(data).lower():check(*api('/api/v1/models/model/update',payload,token=token))
   else:check(code,data)
 models=check(*api('/api/models',token=token))
 out['models']=[{'id':x['id'],'name':x.get('name'),'vision':x.get('info',{}).get('meta',{}).get('capabilities',{}).get('vision')} for x in models['data']]
 if 'history_fixture' not in out:
  chat=check(*api('/api/v1/chats/new',{'chat':{'title':'Comprobación HISTORIAL_IA_4821','models':['gemma-4-26b'],'messages':[{'id':'fixture-4821','role':'user','content':'HISTORIAL_IA_4821'}],'history':{'messages':{'fixture-4821':{'id':'fixture-4821','role':'user','content':'HISTORIAL_IA_4821','parentId':None,'childrenIds':[]}},'currentId':'fixture-4821'}}},token=token))
  out['history_fixture']={'id':chat['id']}
 search=check(*api('/api/v1/chats/search?text=HISTORIAL_IA_4821',token=token));assert any(x['id']==out['history_fixture']['id'] for x in search)
 out['history_search']=True
 out['ui']=api('/')[0];out['anonymous_config']=check(*api('/api/config'));save();print('WebUI init PASS, usuario técnico temporal; secretos en '+str(cred))
elif stage=='rag-prepare':
 token=json.loads(cred.read_text())['token'];p=pathlib.Path('/root/ia-faro-test.md');p.write_text('El código del proyecto Faro es 7731.\n')
 file=upload(p,'ia-faro-test.md','text/markdown',token)
 knowledge=check(*api('/api/v1/knowledge/create',{'name':'Prueba técnica Faro temporal','description':'Eliminar tras validación'},token=token))
 added=check(*api('/api/v1/knowledge/'+knowledge['id']+'/file/add',{'file_id':file['id']},token=token))
 out['rag_fixture']={'file_id':file['id'],'knowledge_id':knowledge['id'],'added':bool(added)};save();print('RAG fixture PASS')
elif stage=='warm-embedding':
 token=json.loads(cred.read_text())['token'];fid=out['rag_fixture']['file_id'];data=check(*api('/api/v1/retrieval/query/doc',{'collection_name':'file-'+fid,'query':'código del proyecto Faro','k':3},token=token));assert '7731' in str(data);print('Embedding local calentado, sin cargar LLM')
elif stage=='rag-chat':
 token=json.loads(cred.read_text())['token'];kid=out['rag_fixture']['knowledge_id']
 start=time.monotonic();data=check(*api('/api/chat/completions',{'model':'gemma-4-26b','messages':[{'role':'user','content':'¿Cuál es el código del proyecto Faro? Responde solo con el código del documento.'}],'files':[{'type':'collection','id':kid,'name':'Prueba técnica Faro temporal','status':'processed'}],'stream':False,'max_tokens':64,'chat_template_kwargs':{'enable_thinking':False}},token=token))
 text=data.get('choices',[{}])[0].get('message',{}).get('content','');out['rag']={'content':text,'elapsed_s':time.monotonic()-start,'ok':'7731' in text};save();assert out['rag']['ok'],str(data)[:500];print('RAG chat PASS',text)
elif stage=='stt':
 token=json.loads(cred.read_text())['token'];path=pathlib.Path('/root/ia-stt-test.wav');subprocess.run(['espeak-ng','-v','es','-s','120','-g','10','-w',str(path),'Hola. Esto es una prueba.'],check=True)
 boundary='ia-'+secrets.token_hex(16);body=('--'+boundary+'\r\nContent-Disposition: form-data; name="file"; filename="ia-stt-test.wav"\r\nContent-Type: audio/wav\r\n\r\n').encode()+path.read_bytes()+('\r\n--'+boundary+'--\r\n').encode()
 if 'stt' in out:out.setdefault('stt_attempts',[]).append(out['stt'])
 start=time.monotonic();data=check(*api('/api/v1/audio/transcriptions',token=token,raw=body,content_type='multipart/form-data; boundary='+boundary));text=data.get('text','')
 reference='hola esto es una prueba'.split();words=re.findall(r'[a-z]+',unicodedata.normalize('NFKD',text.lower()).encode('ascii','ignore').decode());row=list(range(len(words)+1))
 for i,w in enumerate(reference,1):
  new=[i]
  for j,v in enumerate(words,1):new.append(min(new[-1]+1,row[j]+1,row[j-1]+(w!=v)))
  row=new
 wer=row[-1]/len(reference)
 out['stt']={'text':text,'elapsed_s':time.monotonic()-start,'word_error_rate':wer,'ok_approximate':wer<=0.20,'exact':wer==0,'criterion':'Transcripción parecida: WER<=20%; registrar explícitamente cualquier error'};save();assert out['stt']['ok_approximate'],text;print('STT aproximado',text,'WER',wer,'exacto',wer==0)
elif stage=='history-after-reboot':
 token=json.loads(cred.read_text())['token'];cid=out['history_fixture']['id']
 stored=check(*api('/api/v1/chats/'+cid,token=token));search=check(*api('/api/v1/chats/search?text=HISTORIAL_IA_4821',token=token));assert any(x['id']==cid for x in search)
 out['history_after_reboot']={'same_id':stored['id']==cid,'search_ok':True};out['ui_after_reboot']=api('/')[0];save();print('Historial persistente/búsqueda tras reboot PASS')
elif stage=='rag-clean':
 token=json.loads(cred.read_text())['token'];fixture=out.get('rag_fixture',{})
 if fixture:
  check(*api('/api/v1/knowledge/'+fixture['knowledge_id']+'/delete',method='DELETE',token=token));check(*api('/api/v1/files/'+fixture['file_id'],method='DELETE',token=token));out['rag_fixture']['deleted']=True;save()
 print('RAG fixture eliminado')
else:raise SystemExit('stage inválido')

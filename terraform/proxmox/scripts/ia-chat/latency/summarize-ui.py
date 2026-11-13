#!/usr/bin/env python3
"""Resume cada petición de logs y contrasta derivación KV con usage de la ruta UI.
input_tokens = KV al liberar - tokens generados + 1 (último token aún no evaluado).
La derivación se verifica contra los contadores API de todas las respuestas principales.
"""
import pathlib,json,re
ROOT=pathlib.Path(__file__).resolve().parents[3];P=ROOT/'docs/roadmap/evidence/ia-chat-latency-2026-11-13';out={}
for f in sorted(P.glob('*-llama.log')):
 stage=f.name.removesuffix('-llama.log');response=P/(stage+'.json')
 if not response.exists():continue
 records={};ordered=[]
 for line in f.read_text().splitlines():
  match=re.search(r'\[(\d+)\].*?id\s+(\d+)\s*\|\s*task\s+(-?\d+)\s*\|\s*(.*)',line)
  if not match:continue
  pid,slot,task,text=match.groups()
  if task=='-1':continue
  key=(pid,slot,task)
  if 'processing task' in text:
   records[key]={'slot':int(slot),'task':int(task),'pid':int(pid)};ordered.append(key)
  if key not in records:continue
  row=records[key]
  p=re.search(r'prompt eval time =\s*([\d.]+) ms /\s*(\d+) tokens',text)
  if p:row.update(prompt_ms=float(p[1]),prompt_processed=int(p[2]))
  g=re.search(r'^\s*eval time =\s*([\d.]+) ms /\s*(\d+) tokens.*?([\d.]+) tokens per second',text)
  if g:row.update(generation_ms=float(g[1]),generated_tokens=int(g[2]),generation_tokens_s=float(g[3]))
  end=re.search(r'stop processing: n_tokens = (\d+)',text)
  if end:row['kv_tokens_at_release']=int(end[1])
 rows=[]
 for key in ordered:
  row=records[key]
  if not all(k in row for k in ['prompt_processed','generated_tokens','kv_tokens_at_release']):raise AssertionError((stage,'Incomplete journal',row))
  row['input_tokens']=row['kv_tokens_at_release']-row['generated_tokens']+1;row['cached_tokens']=row['input_tokens']-row['prompt_processed'];assert row['cached_tokens']>=0
  rows.append(row)
 data=json.loads(response.read_text());main=data['results'];indices=[0] if len(main)==1 else list(range(len(main)))
 for index,r in zip(indices,main):
  api=r.get('usage') or {};row=rows[index];assert row['input_tokens']==api['input_tokens'],(stage,'KV derivation differs from API input',row,api);assert row['cached_tokens']==api['cache_n'],(stage,'KV derivation differs from API cache');row['verified_against_ui_usage']=True;row['ttft_s']=r['ttft_s']
 out[stage]={'requests':rows,'messages':len(main),'requests_per_message':len(rows)/len(main)}
(P/'ui-request-summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({stage:[{'input':r['input_tokens'],'cached':r['cached_tokens'],'new':r['prompt_processed'],'slot':r['slot'],'ttft':r.get('ttft_s')} for r in d['requests']] for stage,d in out.items()},indent=2))

#!/usr/bin/env python3
"""Read pinned Base0.6B tensor headers only; never download/load model weights."""
import json,math,struct,urllib.request
repo='Qwen/Qwen3-TTS-12Hz-0.6B-Base'
with urllib.request.urlopen('https://huggingface.co/api/models/'+repo,timeout=30) as r:meta=json.load(r)
revision=meta['sha'];rows=[]
for name in ['model.safetensors','speech_tokenizer/model.safetensors']:
 url='https://huggingface.co/'+repo+'/resolve/'+revision+'/'+name
 req=urllib.request.Request(url,headers={'Range':'bytes=0-7'})
 with urllib.request.urlopen(req,timeout=45) as r:head=r.read(8)
 size=struct.unpack('<Q',head)[0];assert size<1024**2
 req=urllib.request.Request(url+'?header=d067',headers={'Range':'bytes=0-'+str(size+7)})
 with urllib.request.urlopen(req,timeout=45) as r:buf=r.read(size+8)
 assert struct.unpack('<Q',buf[:8])[0]==size
 tensors=json.loads(buf[8:]);counts={}
 for k,v in tensors.items():
  if k=='__metadata__':continue
  counts[v['dtype']]=counts.get(v['dtype'],0)+math.prod(v['shape'])
 rows.append({'file':name,'parameters_by_dtype':counts,'fp32_bytes':sum(counts.values())*4,'bf16_bytes':sum(counts.values())*2,'header_bytes_read':size+8})
print(json.dumps({'repo':repo,'revision':revision,'measurements':rows,'fp32_weights_bytes':sum(x['fp32_bytes'] for x in rows),'bf16_weights_bytes':sum(x['bf16_bytes'] for x in rows),'load_rss':'NOT_MEASURED','inference_peak':'NOT_MEASURED','backend_installed':'CPU FP32; BF16 patch D066 only affects CustomVoice','next_gate':'separate BF16 Base candidate and real recordings; no Base load in D067'},indent=2))

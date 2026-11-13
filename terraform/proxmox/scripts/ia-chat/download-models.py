#!/usr/bin/env python3
"""Dentro de630: wget -c, dos intentos máximos por fichero; verifica bytes+SHA."""
import pathlib,subprocess,hashlib,json,datetime
files=[('qwen3.6-35b-a3b','unsloth/Qwen3.6-35B-A3B-GGUF','Qwen3.6-35B-A3B-UD-IQ4_XS.gguf',17730509792,'649d7508507b84638732c4f52c24c8b15843c6dca2f3ff793ae07c14a67ebbb3'),('qwen3.6-35b-a3b','unsloth/Qwen3.6-35B-A3B-GGUF','mmproj-F16.gguf',899283680,'8971ee4f331ff0a4c609374f32984b3d4e6dc086c0aa35f1d637fad1829e887f'),('gemma-4-26b-a4b','unsloth/gemma-4-26B-A4B-it-qat-GGUF','gemma-4-26B-A4B-it-qat-UD-Q4_K_XL.gguf',14249047104,'a7c5bc715f5ff8e99a3e8901ce7d2b42b402c669bf24f7c5250747633d0f5891'),('gemma-4-26b-a4b','unsloth/gemma-4-26B-A4B-it-qat-GGUF','mmproj-F16.gguf',1193058784,'d00f211a7d4f7fb19bd9b75d8e9342eccffb5920b08fd9562167560fdfcc5dd1')]
results=[]
for folder,repo,name,size,sha in files:
 p=pathlib.Path('/models')/folder/name;p.parent.mkdir(parents=True,exist_ok=True)
 for attempt in [1,2]:
  if not p.exists() or p.stat().st_size!=size:
   with open('/var/log/ia-model-download.log','a') as log:
    subprocess.run(['wget','-c','--progress=dot:giga','--tries=3','--timeout=60','-O',str(p),'https://huggingface.co/'+repo+'/resolve/main/'+name],stdout=log,stderr=log)
  actual=hashlib.sha256()
  if p.is_file():
   with p.open('rb') as f:
    for chunk in iter(lambda:f.read(8*1024*1024),b''):actual.update(chunk)
  if p.is_file() and p.stat().st_size==size and actual.hexdigest()==sha:break
  if attempt==1 and p.exists():p.rename(p.with_name(p.name+'.failed-attempt-1'))
 else:raise SystemExit('HALT checksum tras dos intentos: '+name)
 result={'path':str(p),'bytes':size,'sha256':actual.hexdigest(),'attempt':attempt,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};results.append(result)
 print(json.dumps(result),flush=True)
 pathlib.Path('/root/ia-models-verified.json').write_text(json.dumps(results,indent=2)+'\n')

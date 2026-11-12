#!/usr/bin/env python3
"""D063: aceptación real Voicebox por API, crea un perfil de prueba y audio español."""
import argparse,array,datetime,hashlib,io,json,re,time,urllib.request,wave
from pathlib import Path
BASE='http://192.168.1.127:17493'
TEXT='Hola, esta es una prueba de generación de voz de Voicebox, ejecutándose dentro de nuestra infraestructura Proxmox.'
def request(path,data=None):
 raw=json.dumps(data).encode() if data is not None else None
 with urllib.request.urlopen(urllib.request.Request(BASE+path,data=raw,headers={'Content-Type':'application/json'}),timeout=30) as r:return json.load(r)
def sample():
 with urllib.request.urlopen('http://192.168.1.127:9100/metrics',timeout=10) as r:b=r.read().decode()
 def value(name):return float(re.search('^'+name+r'(?:\{[^\n]*\})? ([^\s]+)',b,re.M)[1])
 return {'ct_memory_used_bytes':value('node_memory_MemTotal_bytes')-value('node_memory_MemAvailable_bytes'),'cpu_seconds':value('lxc_cpu_usage_seconds_total')}
def main(out):
 assert not (out/'request.json').exists(),'Solicitud anterior registrada: reconciliar su ID; no repetir POST ni sobrescribir evidencia'
 out.mkdir(parents=True,exist_ok=True,mode=0o700)
 health=request('/health');assert health['status']=='healthy' and health['backend_variant']=='cpu'
 profiles=request('/profiles');matches=[p for p in profiles if p['name']=='Prueba IaC español D063'];assert len(matches)<=1
 profile=matches[0] if matches else request('/profiles',{'name':'Prueba IaC español D063','description':'Perfil preset español para validación infraestructura','language':'es','voice_type':'preset','preset_engine':'kokoro','preset_voice_id':'ef_dora','default_engine':'kokoro'})
 assert profile['voice_type']=='preset' and profile['preset_engine']=='kokoro' and profile['preset_voice_id']=='ef_dora' and profile['language']=='es','Perfil existente incompatible'
 start=time.monotonic();samples=[sample()];generation=request('/generate',{'profile_id':profile['id'],'text':TEXT,'language':'es','engine':'kokoro','personality':False});ident=generation['id'];(out/'request.json').write_text(json.dumps({'profile_id':profile['id'],'generation_id':ident},indent=2)+'\n')
 while time.monotonic()-start<600:
  generation=request('/history/'+ident);samples.append(sample())
  if generation['status'] in ['completed','failed','cancelled']:break
  time.sleep(2)
 elapsed=time.monotonic()-start
 (out/'generation.json').write_text(json.dumps(generation,indent=2)+'\n')
 assert generation['status']=='completed',str(generation.get('error') or generation['status'])
 with urllib.request.urlopen(BASE+'/audio/'+ident,timeout=30) as r:audio=r.read();content_type=r.headers.get('Content-Type')
 (out/'voicebox-es.wav').write_bytes(audio)
 with wave.open(io.BytesIO(audio)) as w:
  duration=w.getnframes()/w.getframerate();rate=w.getframerate();channels=w.getnchannels();width=w.getsampwidth();frames=w.readframes(w.getnframes())
 assert 1<duration<120 and rate==24000 and channels==1 and width==2
 pcm=array.array('h',frames);assert max(abs(x) for x in pcm)>100,'Audio sin señal'
 result={'result':'PASS','observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ct_id':627,'engine':'kokoro','preset_voice_id':'ef_dora','language':'es','profile_id':profile['id'],'generation_id':ident,'generation_seconds':round(elapsed,2),'duration_seconds':duration,'sample_rate':rate,'channels':channels,'format':'WAV PCM16','bytes':len(audio),'sha256':hashlib.sha256(audio).hexdigest(),'audio_url':BASE+'/audio/'+ident,'cpu_seconds_during_test':samples[-1]['cpu_seconds']-samples[0]['cpu_seconds'],'peak_sampled_ct_used_bytes':max(s['ct_memory_used_bytes'] for s in samples),'samples':len(samples),'content_type':content_type}
 (out/'tts-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();main(a.output)

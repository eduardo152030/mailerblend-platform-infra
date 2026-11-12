"""Local offline ASR validation of the generated WAV; never load a model in CT627."""
from pathlib import Path
import json,hashlib,re,difflib,subprocess,wave,time,sys
import torch,whisper,numpy as np
p=Path.home()/'.local/share/mailerblend-recovery/voicebox-d081';wav=p/'Eduardo-D081-continuo.wav';assert wav.is_file()
checkpoint=Path.home()/'.cache/whisper/small.pt';assert checkpoint.is_file(),'No download permitted'
# Verify existing local weights against the installed Whisper package's URL digest.
expected=whisper._MODELS['small'].split('/')[-2];h=hashlib.sha256()
with checkpoint.open('rb') as f:
 for b in iter(lambda:f.read(1024**2),b''):h.update(b)
assert h.hexdigest()==expected
start=time.monotonic();torch.set_num_threads(3);torch.set_num_interop_threads(1)
model=whisper.load_model(str(checkpoint),device='cpu')
r=model.transcribe(str(wav),language='es',fp16=False,temperature=(0.0,),verbose=None)
(p/'asr.private.json').write_text(json.dumps(r,ensure_ascii=False));(p/'asr.private.json').chmod(0o600)
def words(s):return re.findall(r'[^\W_]+',s.lower(),flags=re.UNICODE)
a=words((p/'text.txt').read_text());b=words(r['text']);ops=difflib.SequenceMatcher(a=a,b=b,autojunk=False).get_opcodes();diffs=[{'operation':op,'expected':' '.join(a[i:j]),'heard_by_asr':' '.join(b[k:l])} for op,i,j,k,l in ops if op!='equal']
# Independent PCM measurements, no resampling, padding or time stretching.
with wave.open(str(wav)) as w:
 rate=w.getframerate();frames=w.getnframes();assert w.getnchannels()==1 and w.getsampwidth()==2;x=np.frombuffer(w.readframes(frames),dtype='<i2').astype(np.float64)/32768
silence=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(wav),'-af','silencedetect=noise=-40dB:d=0.8','-f','null','-'],capture_output=True,text=True,check=True)
durations=[float(z) for z in re.findall(r'silence_duration: ([0-9.]+)',silence.stderr)]
result={'method':'offline local Whisper small CPU, no initial prompt, no CT627 model load','model_sha256':expected,'asr_seconds':time.monotonic()-start,'expected_words':len(a),'asr_words':len(b),'normalized_words_identical':a==b,'differences':diffs,'segments':len(r['segments']),'max_no_speech_probability':max((s['no_speech_prob'] for s in r['segments']),default=0),'wave_seconds':frames/rate,'rms':float(np.sqrt(np.mean(x*x))),'peak_abs':float(np.max(np.abs(x))),'silences_at_least_0_8s':len(durations),'max_detected_silence_seconds':max(durations,default=0),'acoustic_acceptance':'PENDING owner listening','limitation':'ASR is an independent indication, not proof of every word or vocal fidelity'}
(p/'content-validation.json').write_text(json.dumps(result,ensure_ascii=False));print(json.dumps(result,ensure_ascii=False))

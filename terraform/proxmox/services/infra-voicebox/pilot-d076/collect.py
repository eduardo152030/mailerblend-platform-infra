"""Collect isolated pilot evidence and private WAV; never put personal audio in Git."""
from pathlib import Path
import argparse,subprocess,shlex,json,os,hashlib
ap=argparse.ArgumentParser();ap.add_argument('attempt',choices=['01','02']);n=ap.parse_args().attempt
out=Path.home()/'.local/share/mailerblend-recovery/voicebox-d076'
ssh=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve']
code="from pathlib import Path;import json;p=Path('/srv/voicebox/pilot-d076/job"+n+"');print(json.dumps({'events':[json.loads(x) for x in (p/'events.jsonl').read_text().splitlines()],'result':json.loads((p/'result.json').read_text()) if (p/'result.json').exists() else None,'wav_exists':(p/'output.wav').exists()}))"
r=subprocess.run(ssh+['pct exec 627 -- python3 -c '+shlex.quote(code)],capture_output=True,timeout=20);assert r.returncode==0,r.stderr.decode();(out/('worker'+n+'.json')).write_bytes(r.stdout);d=json.loads(r.stdout)
if d['wav_exists']:
 audio=out/('eduardo-trading-fp32-'+n+'.wav');assert not audio.exists()
 with audio.open('xb') as f:
  os.chmod(audio,0o600);r=subprocess.run(ssh+['pct exec 627 -- cat /srv/voicebox/pilot-d076/job'+n+'/output.wav'],stdout=f,stderr=subprocess.PIPE,timeout=20)
 assert r.returncode==0;assert hashlib.sha256(audio.read_bytes()).hexdigest()==d['result']['audio']['sha256']
 print('Private WAV copied and hash verified:',str(audio))
print('Collected',n,'wav',d['wav_exists'])

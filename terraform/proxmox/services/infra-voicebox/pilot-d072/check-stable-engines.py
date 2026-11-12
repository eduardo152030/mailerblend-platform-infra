#!/usr/bin/env python3
"""Run only existing preset engines, sequentially and offline, with a hard deadline."""
import subprocess,json,socket
from pathlib import Path
assert socket.gethostname()=='infra-voicebox'
image='local/voicebox:8af7efe62fab-personal-d069'
for engine in ['kokoro','piper']:
 name='voicebox-d072-stable-'+engine
 cmd=['docker','run','--rm','--name',name,'--network','none','--no-healthcheck','--cpus','2','--memory','1400m','--memory-swap','1400m','--entrypoint','python','-e','PYTHONPATH=/app','-e','HF_HOME=/home/voicebox/.cache/huggingface','-e','HF_HUB_OFFLINE=1','-e','OMP_NUM_THREADS=2','-e','MKL_NUM_THREADS=2','-e','NUMBA_CACHE_DIR=/tmp/numba','-v','/srv/voicebox/data:/app/data:ro','-v','/srv/voicebox/huggingface:/home/voicebox/.cache/huggingface:ro','-v','/opt/voicebox/diagnostics-d072-stable/check-engines.py:/check.py:ro','-v','/srv/voicebox/diagnostics-d072-stable:/diagnostic-output',image,'/check.py',engine]
 try:r=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
 except subprocess.TimeoutExpired:
  subprocess.run(['docker','stop','--timeout','5',name],check=True);raise
 Path('/srv/voicebox/diagnostics-d072-stable/'+engine+'-run.log').write_text(r.stdout+r.stderr)
 assert r.returncode==0,engine+' failed; inspect private log'
 print(Path('/srv/voicebox/diagnostics-d072-stable/'+engine+'.json').read_text(),flush=True)

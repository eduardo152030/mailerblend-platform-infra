"""PVE read-only progress, without voice reference or transcript disclosure."""
from pathlib import Path
import subprocess,json
cg=Path('/sys/fs/cgroup/lxc/627')
code="from pathlib import Path;import json;p=Path('/srv/voicebox/pilot-d076/job02/progress.json');print(p.read_text() if p.exists() else '{}')"
r={'progress':json.loads(subprocess.check_output(['pct','exec','627','--','python3','-c',code],text=True)),'ct_memory_gib':int((cg/'memory.current').read_text())/2**30,'ct_swap_mib':int((cg/'memory.swap.current').read_text())/2**20,'ct_pressure':(cg/'memory.pressure').read_text(),'state':json.loads(subprocess.check_output(['pct','exec','627','--','docker','inspect','-f','{{json .State}}','qwen-d076-fp32-long-02'],text=True))}
r['state']={k:v for k,v in r['state'].items() if k in ['Running','Pid','OOMKilled','ExitCode']};print(json.dumps(r))

"""PVE read-only snapshot of the single D080 job. No model loading or mutations."""
from pathlib import Path
import json,subprocess,datetime
pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();root=Path('/proc',pid,'root');job=root/'srv/voicebox/qwen-worker/jobs/7f348e9777214f4e827dcf7e1458c045';cg=Path('/sys/fs/cgroup/lxc/627')
st=dict((k,int(v)) for k,v in (x.split() for x in (cg/'memory.stat').read_text().splitlines()));events=[]
if (job/'events.jsonl').exists():events=[json.loads(x) for x in (job/'events.jsonl').read_text().splitlines()]
result={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':json.loads((job/'state.json').read_text()),'ct_current':int((cg/'memory.current').read_text()),'anon':st['anon'],'file':st['file'],'kernel':st['kernel'],'swap':int((cg/'memory.swap.current').read_text()),'psi':(cg/'memory.pressure').read_text(),'events':events,'checkpoint_committed':(job/'checkpoint/COMMITTED.json').is_file()}
print(json.dumps(result))

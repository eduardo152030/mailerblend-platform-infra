"""PVE read-only preservation snapshot for D074."""
from pathlib import Path
import hashlib,json,subprocess,datetime
configs={p.stem:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('/etc/pve/lxc').glob('*.conf')}
events={p.name:{x.split()[0]:int(x.split()[1]) for x in (p/'memory.events').read_text().splitlines()} for p in Path('/sys/fs/cgroup/lxc').iterdir() if p.name.isdigit() and (p/'memory.events').is_file()}
ids=subprocess.check_output(['pct','exec','618','--','docker','ps','-aq'],text=True).split();rows=json.loads(subprocess.check_output(['pct','exec','618','--','docker','inspect',*ids],text=True))
siblings=[{'id':x['Id'],'name':x['Name'],'image':x['Image'],'started_at':x['State']['StartedAt'],'status':x['State']['Status'],'restarts':x['RestartCount']} for x in rows]
print(json.dumps({'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'config_hashes':configs,'events':events,'global_oom_kill':int(dict(x.split() for x in Path('/proc/vmstat').read_text().splitlines())['oom_kill']),'ct618_containers':siblings,'ct627_df':subprocess.check_output(['pct','exec','627','--','df','-B1','/'],text=True)}))

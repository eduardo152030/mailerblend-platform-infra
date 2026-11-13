#!/usr/bin/env python3
"""PVE: observa memoria de630/631 mientras ejecuta un comando autorizado."""
import pathlib,json,subprocess,time,datetime,sys
assert len(sys.argv)>3
path=pathlib.Path(sys.argv[1]);p=subprocess.Popen(sys.argv[2:]);samples=[]
while True:
 ct={}
 for id in ['630','631']:
  cg=pathlib.Path('/sys/fs/cgroup/lxc')/id
  stat={x.split()[0]:int(x.split()[1]) for x in (cg/'memory.stat').read_text().splitlines()};current=int((cg/'memory.current').read_text())
  ct[id]={'current':current,'working_set':max(0,current-stat.get('inactive_file',0)),'max':int((cg/'memory.max').read_text()),'anon':stat.get('anon'),'swap':int((cg/'memory.swap.current').read_text()),'events':(cg/'memory.events').read_text()}
 samples.append({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ct':ct})
 path.write_text(json.dumps(samples,indent=2)+'\n')
 rc=p.poll()
 if rc is not None:break
 time.sleep(1)
print('Memoria631 working_set pico GiB',round(max(s['ct']['631']['working_set'] for s in samples)/1024**3,3),flush=True)
raise SystemExit(rc)

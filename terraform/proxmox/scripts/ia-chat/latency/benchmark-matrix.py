#!/usr/bin/env python3
"""PVE: matriz secuencial630, r3, PP4h/TG3h; guarda21GiB y residente/RSS<90%.
Solo detiene/arranca llama-server630. Nunca modifica otros CT ni swap global.
"""
import pathlib,subprocess,json,time,datetime,signal,os
ROOT=pathlib.Path('/root/ia-local/latency');OUT=ROOT/'bench';OUT.mkdir(parents=True,exist_ok=True)
MODELS={'gemma-4-26b':'/models/gemma-4-26b-a4b/gemma-4-26B-A4B-it-qat-UD-Q4_K_XL.gguf','qwen3.6-35b':'/models/qwen3.6-35b-a3b/Qwen3.6-35B-A3B-UD-IQ4_XS.gguf'}
def run(*a):return subprocess.check_output(a,text=True).strip()
def cgroup_pids(root):
 pids=set()
 for directory,_,files in os.walk(root,onerror=lambda error:None):
  if 'cgroup.procs' not in files:continue
  try:pids.update((pathlib.Path(directory)/'cgroup.procs').read_text().split())
  except OSError:pass
 return pids
def memory():
 root=pathlib.Path('/sys/fs/cgroup/lxc/630');stat=dict(l.split() for l in (root/'memory.stat').read_text().splitlines());current=int((root/'memory.current').read_text());resident=min(current,sum(int(stat.get(k,0)) for k in ['anon','file_mapped','kernel']));pids=cgroup_pids(root)
 rss=0
 for pid in pids:
  try:
   if pathlib.Path('/proc/'+pid+'/comm').read_text().strip()=='llama-bench':rss+=next(int(l.split()[1])*1024 for l in pathlib.Path('/proc/'+pid+'/status').read_text().splitlines() if l.startswith('VmRSS:'))
  except (OSError,StopIteration):pass
 return {'rss':rss,'resident':resident,'current':current,'limit':int((root/'memory.max').read_text()),'host_available':int(next(l.split()[1] for l in pathlib.Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
run('pct','exec','630','--','systemctl','stop','llama-server')
try:
 for alias,model in MODELS.items():
  for b in [512,2048]:
   for ub in [128,256,512]:
    for kind,t,prompt,gen in [('pp',4,'512,2048','0'),('tg',3,'0','128')]:
     stem=f'{alias}-b{b}-ub{ub}-{kind}';dest=OUT/(stem+'.json');proof=OUT/(stem+'-memory.json')
     if dest.exists() and proof.exists():assert json.loads(proof.read_text())['pass'];print('SKIP verified '+stem,flush=True);continue
     guard=memory();assert guard['host_available']>=21*1024**3,'HALT host MemAvailable<21GiB'
     args=['pct','exec','630','--','/opt/llama.cpp/build/bin/llama-bench','-m',model,'-p',prompt,'-n',gen,'-t',str(t),'-r','3','-b',str(b),'-ub',str(ub),'--repack','0','-lm','mmap','-o','json']
     for suffix in ['.partial','.log']:
      old=OUT/(stem+suffix)
      if old.exists():old.rename(OUT/(stem+'-previous-'+str(time.time_ns())+suffix))
     print('START '+stem+' '+guard['utc'],flush=True);stdout=(OUT/(stem+'.partial')).open('w');stderr=(OUT/(stem+'.log')).open('w');proc=subprocess.Popen(args,stdout=stdout,stderr=stderr);samples=[];halt=False
     while proc.poll() is None:
      m=memory();samples.append(m)
      if max(m['rss'],m['resident'])>=.9*m['limit']:
       subprocess.run(['pct','exec','630','--','pkill','-INT','-x','llama-bench'],capture_output=True);halt=True;break
      time.sleep(.5)
     rc=proc.wait();stdout.close();stderr.close();data=json.loads((OUT/(stem+'.partial')).read_text()) if rc==0 else None
     record={'pass':rc==0 and not halt,'guard':guard,'returncode':rc,'samples':samples,'repack':False};proof.write_text(json.dumps(record,indent=2)+'\n');assert record['pass'],'HALT benchmark rc/pressure '+stem
     assert len(data)==(2 if kind=='pp' else 1);dest.write_text(json.dumps(data,indent=2)+'\n')
     print('PASS '+stem+' '+str([(r['n_prompt'],r['n_gen'],round(r['avg_ts'],4)) for r in data]),flush=True)
finally:
 subprocess.run(['pct','exec','630','--','pkill','-INT','-x','llama-bench'],capture_output=True)
 for _ in range(60):
  if subprocess.run(['pct','exec','630','--','pgrep','-x','llama-bench'],capture_output=True).returncode!=0:break
  time.sleep(1)
 else:raise SystemExit('HALT: benchmark remains alive; do not start router')
 run('pct','exec','630','--','systemctl','start','llama-server')
print('MATRIX PASS',flush=True)

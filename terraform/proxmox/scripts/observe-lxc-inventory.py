#!/usr/bin/env python3
"""Read-only PVE/Docker/Nginx discovery. Never collect environment, full logs or nginx text."""
import argparse, importlib.util, json, subprocess, urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
INNER=r'''
import subprocess,json,pathlib
ids=subprocess.check_output(['docker','ps','-aq'],text=True).split()
containers=json.loads(subprocess.check_output(['docker','inspect']+ids,text=True)) if ids else []
print(json.dumps({'boot_id':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
'os_release':dict(l.split('=',1) for l in pathlib.Path('/etc/os-release').read_text().splitlines() if '=' in l).get('PRETTY_NAME','').strip(chr(34)),
'containers':[{'name':c['Name'].lstrip('/'),'id':c['Id'],'image':c['Config']['Image'],'image_id':c['Image'],
'started_at':c['State']['StartedAt'],'status':c['State']['Status'],'health':c['State'].get('Health',{}).get('Status','not configured'),
'restarts':c['RestartCount'],'ports':c['HostConfig'].get('PortBindings',{}),
'compose_files':c['Config'].get('Labels',{}).get('com.docker.compose.project.config_files',''),
'compose_service':c['Config'].get('Labels',{}).get('com.docker.compose.service',''),
'healthcheck_type':'native Node' if '/app/health_checker_bin.js' in str(c['Config'].get('Healthcheck',{})) else ('configured (command withheld)' if c['Config'].get('Healthcheck') else 'not configured')}
for c in containers]}))
'''
REMOTE=r'''
import subprocess,json,datetime,socket,re,urllib.parse
rows=[]
for ct in IDS:
 cfg=dict(l.split(': ',1) for l in subprocess.check_output(['pct','config',str(ct)],text=True).splitlines() if ': ' in l)
 r=subprocess.run(['pct','exec',str(ct),'--','python3','-'],input=INNER,text=True,capture_output=True,timeout=45)
 assert r.returncode==0,'CT read failed: '+str(ct)
 selected={k:v for k,v in cfg.items() if k in ['hostname','cores','memory','swap','rootfs','ostype','description','net0','tags']}
 selected['description']=urllib.parse.unquote(selected.get('description','')).strip()
 rows.append({'ct':ct,'node':socket.gethostname(),'config':selected,'status':subprocess.check_output(['pct','status',str(ct)],text=True).strip(),'runtime':json.loads(r.stdout)})
r=subprocess.run(['pct','exec','109','--','nginx','-T'],capture_output=True,text=True)
assert r.returncode==0,'Nginx read failed'
s=r.stdout;routes=[]
for match in re.finditer(r'\bserver\s*\{',s):
 start=match.end();depth=1;i=start
 while i<len(s) and depth:
  depth+=(s[i]=='{')-(s[i]=='}');i+=1
 b=s[start:i-1]
 names=[v for line in re.findall(r'\bserver_name\s+([^;]+);',b) for v in line.split() if re.fullmatch(r'[a-zA-Z0-9.*_-]+',v)]
 upstreams=[]
 for value in re.findall(r'\bproxy_pass\s+([^;]+);',b):
  m=re.match(r'(https?)://([a-zA-Z0-9._:-]+)(?:/|$)',value.strip())
  if m:upstreams.append(m.group(1)+'://'+m.group(2))
 if names and upstreams:routes.append({'server_names':names,'proxy_upstreams':sorted(set(upstreams))})
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
groups=[{'name':m.group(1),'servers':re.findall(r'\bserver\s+([a-zA-Z0-9.:-]+)',m.group(2))} for m in re.finditer(r'\bupstream\s+([a-zA-Z0-9_-]+)\s*\{([^}]+)\}',s)]
print(json.dumps({'observed':{'observed_at_utc':now,'mode':'read-only','lxcs':rows},'routing':{'observed_at_utc':now,'source':'CT109 nginx -T (filtered server_name/proxy_pass only)','routes':routes,'upstream_groups':groups}}))
'''
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--routes-output',type=Path,required=True);args=ap.parse_args()
 spec=importlib.util.spec_from_file_location('generator',ROOT/'scripts/generate-lxc-inventory.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
 spec=importlib.util.spec_from_file_location('access',ROOT/'scripts/rollout-approved-exporters.py');access=importlib.util.module_from_spec(spec);spec.loader.exec_module(access)
 code='IDS='+repr(sorted(g.EXPECTED))+'\nINNER='+repr(INNER)+'\n'+REMOTE
 r=subprocess.run(access.SSH+['python3','-'],input=code,text=True,capture_output=True,timeout=600)
 assert r.returncode==0,'Read-only discovery failed; output withheld'
 d=json.loads(r.stdout);g.assert_public(d)
 for path,key in [(args.output,'observed'),(args.routes_output,'routing')]:
  path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(d[key],ensure_ascii=False,indent=2)+'\n')
 print('PASS: 17 read-only LXC snapshots and filtered CT109 routes written')
if __name__=='__main__':main()

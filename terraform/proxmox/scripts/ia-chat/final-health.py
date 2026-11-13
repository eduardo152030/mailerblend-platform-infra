#!/usr/bin/env python3
"""PVE: estado final filtrado, sin entornos/secretos ni datos de otrosCT."""
import pathlib,subprocess,json,hashlib,datetime,os
root=pathlib.Path('/root/ia-local')
def run(*a):return subprocess.run(a,text=True,capture_output=True,check=True).stdout.strip()
original=json.loads((root/'protected-before.json').read_text());assert all(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()==sha for p,sha in original.items())
mem={l.split(':')[0]:int(l.split()[1])*1024 for l in pathlib.Path('/proc/meminfo').read_text().splitlines() if l.startswith(('MemTotal:','MemAvailable:','SwapTotal:','SwapFree:'))}
cts={}
for id in ['630','631']:
 p=pathlib.Path('/sys/fs/cgroup/lxc')/id;s={l.split()[0]:int(l.split()[1]) for l in (p/'memory.stat').read_text().splitlines()};current=int((p/'memory.current').read_text())
 cts[id]={'config':run('pct','config',id),'ip':json.loads(run('pct','exec',id,'--','ip','-j','-4','addr','show','dev','eth0')),'timezone':run('pct','exec',id,'--','cat','/etc/timezone'),'current':current,'working_set':current-s.get('inactive_file',0),'resident_tasks':min(current,s.get('anon',0)+s.get('file_mapped',0)+s.get('kernel',0)),'anon':s.get('anon',0),'swap':int((p/'memory.swap.current').read_text()),'memory_events':(p/'memory.events').read_text()}
containers={name:run('pct','exec','631','--','docker','inspect','--format','{{.Id}}|{{.Image}}|{{.State.StartedAt}}|{{.State.Status}}|{{.RestartCount}}|{{.HostConfig.Runtime}}',name) for name in ['ia-chat-open-webui-1','ia-chat-searxng-1']}
images={name:run('pct','exec','631','--','docker','image','inspect','--format','{{json .RepoDigests}}|{{.Id}}',state.split('|')[1]) for name,state in containers.items()}
code='import sqlite3,json,pathlib; d=sqlite3.connect(\'/opt/ia-chat/data/webui.db\'); print(json.dumps({\'users\':d.execute(\'select count(*) from user\').fetchone()[0],\'knowledge\':d.execute(\'select count(*) from knowledge\').fetchone()[0],\'integrity\':d.execute(\'pragma quick_check\').fetchone()[0],\'models\':d.execute("select id,name from model where id in (\'gemma-4-26b\',\'qwen3.6-35b\')").fetchall(),\'temporary_credentials_absent\':not pathlib.Path(\'/root/ia-validation-auth.json\').exists()}))'
db=json.loads(run('pct','exec','631','--','python3','-c',code))
assert db['integrity']=='ok' and db['temporary_credentials_absent']
# Knowledge owned by real users is preserved; remove only the fixture checked by its cleanup receipt.
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protected_configs':len(original),'protected_unchanged':True,'host_memory':mem,'storage':run('pvesm','status'),'cts':cts,'containers':containers,'images':images,'db':db,'secret_modes':{'630':run('pct','exec','630','--','stat','-c','%a %n','/etc/llama/api.key'),'631':run('pct','exec','631','--','stat','-c','%a %n','/opt/ia-chat/secrets.env','/opt/ia-chat/searxng/settings.yml')},'llama_active':run('pct','exec','630','--','systemctl','is-active','llama-server'),'docker_versions':run('pct','exec','631','--','dpkg-query','-W','docker-ce','docker-ce-cli','containerd.io','docker-compose-plugin'),'models_mount':run('pct','exec','630','--','findmnt','-no','OPTIONS','/models')}
pathlib.Path(os.environ.get('IA_FINAL_HEALTH_PATH',str(root/'final-health.json'))).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'protected_unchanged':True,'users':db['users'],'knowledge':db['knowledge'],'llama_active':result['llama_active'],'rootfs_models_ro':True}))

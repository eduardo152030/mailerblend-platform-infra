"""CT627: exact Docker Engine disk metadata and backup inventory, read-only."""
import json,http.client,socket,subprocess,os
from pathlib import Path
class UnixConnection(http.client.HTTPConnection):
 def connect(self):
  self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(60);self.sock.connect('/var/run/docker.sock')
c=UnixConnection('localhost');c.request('GET','/system/df');r=c.getresponse();assert r.status==200;r=json.loads(r.read())
# Image/container command fields can contain user data; expose only identifiers, sizes, tags, status.
images=[{k:x.get(k) for k in ['Id','RepoTags','Size','SharedSize','Containers']} for x in r.get('Images',[])]
cache=[{k:x.get(k) for k in ['ID','Parent','Parents','Type','Description','InUse','Shared','Size','CreatedAt','LastUsedAt','UsageCount']} for x in r.get('BuildCache',[])]
backups=[]
for p in Path('/opt/voicebox/backups').iterdir():
 if p.is_file():backups.append({'name':p.name,'kind':'file','bytes':p.stat().st_size,'allocated':p.stat().st_blocks*512})
 else:
  n=int(subprocess.check_output(['du','-sx','-B1',str(p)],text=True).split()[0]);backups.append({'name':p.name,'kind':'directory','allocated':n,'top_files':[{'name':q.name,'bytes':q.stat().st_size} for q in p.iterdir() if q.is_file()]})
print(json.dumps({'docker_layers_size':r.get('LayersSize'),'images':images,'build_cache':cache,'volumes':{'count':len(r.get('Volumes') or []),'bytes':sum((x.get('UsageData') or {}).get('Size',0) for x in r.get('Volumes') or [])},'backups':backups}))

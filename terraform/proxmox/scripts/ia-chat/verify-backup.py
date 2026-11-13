#!/usr/bin/env python3
"""PVE: comprueba archivo631 autorizado sin extraer ni exponer su contenido."""
import pathlib,hashlib,subprocess,json,datetime,sys
p=pathlib.Path(sys.argv[1]);assert p.name.startswith('vzdump-lxc-631-') and p.suffixes[-2:]==['.tar','.zst']
sha=hashlib.sha256()
with p.open('rb') as f:
 for b in iter(lambda:f.read(8*1024*1024),b''):sha.update(b)
subprocess.run(['zstd','-q','-t',str(p)],check=True)
z=subprocess.Popen(['zstd','-q','-dc',str(p)],stdout=subprocess.PIPE)
t=subprocess.Popen(['tar','-tf','-'],stdin=z.stdout,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);z.stdout.close()
count=0;critical={key:False for key in ['opt/ia-chat/data/webui.db','opt/ia-chat/docker-compose.yml','opt/ia-chat/secrets.env','opt/ia-chat/searxng/settings.yml','opt/ia-chat/custom.css','etc/vzdump/pct.conf']}
for line in t.stdout:
 count+=1
 for k in critical:
  if line.strip().removeprefix('./')==k:critical[k]=True
err=t.stderr.read();rc=t.wait();zrc=z.wait();assert rc==0 and zrc==0,(rc,zrc,err[:100]);assert all(critical.values()),critical
print(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'path':str(p),'bytes':p.stat().st_size,'sha256':sha.hexdigest(),'zstd_test':'PASS','tar_list':'PASS','members':count,'critical_members':critical,'functional_restore':'NOT_PERFORMED'},indent=2))

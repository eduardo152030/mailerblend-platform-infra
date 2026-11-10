#!/usr/bin/env python3
"""D057 read-only app checks -> existing Node textfile directory. No app changes."""
import argparse,json,subprocess,time,urllib.request,urllib.error
from pathlib import Path

def docker(args,timeout=10,body=None):
 r=subprocess.run(['docker']+args,input=body,capture_output=True,timeout=timeout)
 if r.returncode:raise RuntimeError('Docker check transport failed')
 return r.stdout

def postgres(container):
 r=subprocess.run(['docker','inspect',container],capture_output=True,timeout=5)
 if r.returncode:return 0
 c=json.loads(r.stdout)[0]
 if not c['State']['Running']:return 0
 # Credentials are never used. Select only nonsecret login/database names for pg_isready.
 meta={}
 for item in c['Config'].get('Env',[]):
  k,sep,v=item.partition('=')
  if k in ['POSTGRES_USER','POSTGRES_DB']:meta[k]=v
 user=meta.get('POSTGRES_USER','postgres');db=meta.get('POSTGRES_DB',user)
 r=subprocess.run(['docker','exec','--user','postgres',container,'pg_isready','-q','-h','127.0.0.1','-p','5432','-U',user,'-d',db,'-t','3'],capture_output=True,timeout=8)
 if r.returncode==0:return 1
 if r.returncode in [1,2]:return 0
 return -1

def odoo():
 try:
  with urllib.request.urlopen('http://127.0.0.1:8069/web/health',timeout=3) as r:
   if r.status!=200 or 'application/json' not in r.headers.get('Content-Type',''):return 0
   result=json.loads(r.read(4096))
   if result.get('status') not in ['pass','ok']:return 0
  with urllib.request.urlopen('http://127.0.0.1:8069/web/login',timeout=3) as r:
   text=r.read(131072).lower()
   return int(r.status==200 and b'odoo' in text and b'<form' in text and b'login' in text)
 except (urllib.error.URLError,ValueError):return 0

def collect(spec):
 rows=[]
 for component in spec['checks']:
  start=time.time()
  try:value=odoo() if component['kind']=='odoo_http' else postgres(component['container'])
  except Exception:value=-1
  rows.append({'component':component['name'],'value':value,'timestamp':time.time(),'duration':time.time()-start})
 return rows

def render(spec,rows):
 lines=['# HELP lxc_app_check_success Functional read-only check: 1 success, 0 failure, -1 unknown.','# TYPE lxc_app_check_success gauge','# HELP lxc_app_check_timestamp_seconds Last completed check timestamp.','# TYPE lxc_app_check_timestamp_seconds gauge']
 for row in rows:
  labels=','.join(k+'='+json.dumps(v) for k,v in {'service':spec['service'],'ct_id':str(spec['ct_id']),'component':row['component'],'health_source':'functional_readonly'}.items())
  lines.extend([f'lxc_app_check_success{{{labels}}} {row["value"]}',f'lxc_app_check_timestamp_seconds{{{labels}}} {row["timestamp"]:.6f}'])
 return '\n'.join(lines)+'\n'

def main():
 p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--dry-run',action='store_true');a=p.parse_args();spec=json.loads(Path(a.config).read_text());rows=collect(spec)
 if a.dry_run:print(json.dumps(rows));return
 body=render(spec,rows).encode()
 # Existing nobody-owned collector directory; atomic write of only our file, no CPU inputs touched.
 cmd='cat > /tmp/lxc-metrics/.d057-application.prom.tmp && mv /tmp/lxc-metrics/.d057-application.prom.tmp /tmp/lxc-metrics/d057-application.prom'
 docker(['exec','-i','--user','65534:65534','node_exporter','sh','-c',cmd],body=body)
if __name__=='__main__':main()

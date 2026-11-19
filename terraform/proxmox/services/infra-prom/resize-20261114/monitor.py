#!/usr/bin/env python3
"""Evidencia filtrada de Prometheus/AM, sin modificaciones ni credenciales."""
import datetime,json,pathlib,subprocess,urllib.parse
ROOT=pathlib.Path(__file__).resolve().parents[3]
code=r'''
import json,urllib.request,urllib.parse
base='http://192.168.1.110:9090'
def get(url):
 with urllib.request.urlopen(url,timeout=20) as r:return json.load(r)
queries={'free_percent':'100 * node_filesystem_avail_bytes{instance="192.168.1.110:9100",mountpoint="/",fstype!="rootfs"} / node_filesystem_size_bytes{instance="192.168.1.110:9100",mountpoint="/",fstype!="rootfs"}','size_bytes':'node_filesystem_size_bytes{instance="192.168.1.110:9100",mountpoint="/",fstype!="rootfs"}','up':'up{instance=~"192.168.1.110:.*"}'}
out={k:get(base+'/api/v1/query?'+urllib.parse.urlencode({'query':v}))['data']['result'] for k,v in queries.items()}
out['alerts']=[{'labels':x['labels'],'state':x['state'],'activeAt':x['activeAt']} for x in get(base+'/api/v1/alerts')['data']['alerts'] if x['labels'].get('instance','').startswith('192.168.1.110:') or x['labels'].get('ct')=='610']
out['alertmanager']=[{'labels':x['labels'],'status':x['status'],'endsAt':x['endsAt']} for x in get('http://192.168.1.110:9093/api/v2/alerts') if x['labels'].get('instance','').startswith('192.168.1.110:') or x['labels'].get('ct')=='610']
print(json.dumps(out))
'''
import sys
label=sys.argv[1];assert label.replace('-','').isalnum()
r=subprocess.run(['ssh','-o','UserKnownHostsFile='+str(pathlib.Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve','python3 -'],input=code.encode(),capture_output=True,check=True,timeout=100)
out=json.loads(r.stdout);out['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(ROOT/'docs/roadmap/evidence/ct610-disk-20261114'/f'monitor-{label}.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))

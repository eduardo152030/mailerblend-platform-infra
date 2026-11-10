#!/usr/bin/env python3
"""Exercise real Alertmanager inhibition locally; no external receiver or notification."""
import json,os,socket,subprocess,tempfile,time,urllib.request
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]
binary=os.environ['ALERTMANAGER_BIN']
source=yaml.safe_load((ROOT/'services/infra-prom/config/alertmanager/alertmanager.yml').read_text())
source['receivers']=[{'name':'telegram'}];source['templates']=[]
with tempfile.TemporaryDirectory(prefix='phase5-am-') as folder:
 p=Path(folder);(p/'config.yml').write_text(yaml.safe_dump(source))
 with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
 proc=subprocess.Popen([binary,'--config.file='+str(p/'config.yml'),'--storage.path='+str(p/'data'),'--web.listen-address=127.0.0.1:'+str(port),'--cluster.listen-address='],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 base='http://127.0.0.1:'+str(port)
 def req(path,body=None):
  r=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(r,timeout=2) as v:return v.read()
 try:
  for _ in range(50):
   try:req('/-/ready');break
   except OSError:time.sleep(.1)
  rows=[]
  def add(alert,severity,service,instance,**labels):
   x={'alertname':alert,'severity':severity,'service':service,'instance':instance}|labels;rows.append({'labels':x})
  for resource,crit,warn in [('memory','HostLowMemory','HostMemoryPressure'),('disk','HostDiskAlmostFull','HostDiskFilling'),('tls','SSLCertExpiringVerySoon','SSLCertExpiringSoon')]:
   add(crit,'critical','s','node',resource=resource);add(warn,'warning','s','node',resource=resource)
   add(warn,'warning','independent','node',resource=resource)
  add('SgtmHealthFailed','critical','sgtm','cadvisor',name='serving')
  add('DockerContainerUnhealthy','warning','sgtm','cadvisor',name='serving')
  add('DockerContainerUnhealthy','warning','sgtm','cadvisor',name='preview')
  add('HostOutOfService','critical','host','node')
  add('LxcMemoryMetricsMissing','warning','host','node')
  add('PublicUrlDown','critical','host','https://example.test')
  add('ExporterDown','critical','cad','cadvisor',job='cadvisor')
  add('LxcDockerMetricsMissing','warning','cad','node')
  add('LxcDockerMetricsMissing','warning','other-cad','node')
  add('ExporterDown','critical','blackbox_exporter','blackbox',job='blackbox_exporter')
  add('BlackboxScrapeFailed','critical','probe','https://example.test')
  add('PublicUrlDown','critical','probe','https://example.test')
  req('/api/v2/alerts',rows)
  for _ in range(30):
   data=json.loads(req('/api/v2/alerts')); index={(x['labels']['alertname'],x['labels']['service'],x['labels'].get('name','')):x['status'] for x in data}
   if index[('HostMemoryPressure','s','')]['inhibitedBy']:break
   time.sleep(.1)
  for warn in ['HostMemoryPressure','HostDiskFilling','SSLCertExpiringSoon']:
   assert index[(warn,'s','')]['inhibitedBy'];assert not index[(warn,'independent','')]['inhibitedBy']
  assert index[('DockerContainerUnhealthy','sgtm','serving')]['inhibitedBy']
  assert not index[('DockerContainerUnhealthy','sgtm','preview')]['inhibitedBy']
  assert index[('LxcMemoryMetricsMissing','host','')]['inhibitedBy']
  assert not index[('PublicUrlDown','host','')]['inhibitedBy']
  assert not index[('SgtmHealthFailed','sgtm','serving')]['inhibitedBy']
  assert index[('LxcDockerMetricsMissing','cad','')]['inhibitedBy']
  assert not index[('LxcDockerMetricsMissing','other-cad','')]['inhibitedBy']
  assert index[('BlackboxScrapeFailed','probe','')]['inhibitedBy']
  assert not index[('PublicUrlDown','probe','')]['inhibitedBy']
  print('Real isolated Alertmanager: 15 inhibition/independence assertions PASS; no receiver integration')
 finally:
  proc.terminate();proc.wait(timeout=10)

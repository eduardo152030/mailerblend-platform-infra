#!/usr/bin/env python3
"""Read-only fingerprints for excluded CRM/EVA and their existing Prometheus targets."""
import argparse,hashlib,json,os,subprocess,urllib.request
from pathlib import Path
SSH=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'pve']
def snapshot():
 probe="import subprocess,json,hashlib;ids=subprocess.check_output(['docker','ps','-aq'],text=True).split();cs=json.loads(subprocess.check_output(['docker','inspect']+ids));print(json.dumps([{'name':c['Name'],'id':c['Id'],'image':c['Image'],'started_at':c['State']['StartedAt'],'running':c['State']['Running'],'fingerprint':hashlib.sha256(json.dumps([c['Config'],c['HostConfig'],sorted(c['Mounts'],key=lambda m:(m.get('Destination',''),m.get('Source','')))],sort_keys=True).encode()).hexdigest()} for c in cs]))"
 code='import subprocess,json\nout={}\nfor ct in [618,622]:\n conf=subprocess.check_output(["pct","config",str(ct)],text=True)\n r=subprocess.run(["pct","exec",str(ct),"--","python3","-c",'+repr(probe)+'],capture_output=True,text=True,timeout=30);assert r.returncode==0\n out[str(ct)]={"config_sha256":__import__("hashlib").sha256(conf.encode()).hexdigest(),"containers":sorted(json.loads(r.stdout),key=lambda c:c["name"])}\nprint(json.dumps(out))'
 r=subprocess.run(SSH+['python3','-'],input=code,capture_output=True,text=True,timeout=90);assert r.returncode==0,'Excluded services read-only snapshot failed';d=json.loads(r.stdout)
 with urllib.request.urlopen('http://192.168.1.110:9090/api/v1/targets',timeout=15) as response:targets=json.load(response)['data']['activeTargets']
 d['prometheus_targets']=sorted([{'labels':t['labels'],'scrape_url':t['scrapeUrl'],'health':t['health']} for t in targets if t['labels'].get('service') in ['infra-composable-crm','infra-eva-assistant-bot']],key=lambda t:(t['labels']['service'],t['labels']['job'],t['scrape_url']))
 assert len([t for t in d['prometheus_targets'] if t['labels']['job'] in ['node_exporter','cadvisor']])==4
 return d
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--baseline',type=Path,required=True);a=p.parse_args();os.umask(0o077);current=snapshot()
 if a.baseline.exists():assert json.loads(a.baseline.read_text())==current,'Excluded service drift: stop before R7';print('Excluded CRM/EVA resources, containers and target coverage unchanged')
 else:
  fd=os.open(a.baseline,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'w') as f:json.dump(current,f,indent=2)
  print('Excluded services private baseline recorded, no remote writes')

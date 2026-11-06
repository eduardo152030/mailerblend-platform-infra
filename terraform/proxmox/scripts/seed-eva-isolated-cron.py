#!/usr/bin/env python3
"""Restore installed runtime packages from the preserved cron ONLY in a network-isolated rehearsal."""
import json
import subprocess
import sys

if sys.argv[1:]!=['--execute']:sys.exit('Usage: seed-eva-isolated-cron.py --execute')
assert not json.loads(subprocess.check_output(['ip','-j','route','show','default'],text=True)),'Must have no external route'
links=json.loads(subprocess.check_output(['ip','-j','addr'],text=True))
assert any(n['ifname']=='lo' and any(a['local']=='192.168.1.122' for a in n.get('addr_info',[])) for n in links)
assert any(n['ifname']=='eth0' and n['operstate']=='DOWN' for n in links),'Clone external network must be down'
old='eva-cron-digest-pre-storage-recovery';new='eva-cron-digest'
a,b=json.loads(subprocess.check_output(['docker','inspect',old,new],text=True))
assert a['Image']==b['Image'] and not a['State']['Running'] and not b['State']['Running']
assert b['Config']['Labels']['com.docker.compose.project']=='eva-storage-recovery'
assert all(m['Destination'] in ['/etc/localtime','/etc/timezone'] for m in a['Mounts']+b['Mounts'])
# Same base image; only restore package/runtime directories, never application data.
for path in ['/lib','/usr','/etc/apk']:
    reader=subprocess.Popen(['docker','cp',old+':'+path+'/.','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    writer=subprocess.run(['docker','cp','-',new+':'+path],stdin=reader.stdout,capture_output=True)
    reader.stdout.close();error=reader.stderr.read()
    assert reader.wait()==0 and writer.returncode==0,'Offline package restore failed'
subprocess.run(['docker','update','--restart=unless-stopped',new],check=True,stdout=subprocess.DEVNULL)
subprocess.run(['docker','start',new],check=True,stdout=subprocess.DEVNULL)
print('Seeded clone-only cron with preserved installed packages; image unchanged and egress still blocked.')

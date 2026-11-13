#!/usr/bin/env python3
"""Reconciliación RAM631 autorizada: lee YAML canónico y cambia solo memory en vivo."""
import json,subprocess,shlex,yaml
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];d=yaml.safe_load((ROOT/'inventory/services/infra-webui.yml').read_text());assert d['service']['vmid']==631 and d['resources']['memory']==4096
code='''import json,subprocess,pathlib
p='/nodes/pve/lxc/631/config'
def get():return json.loads(subprocess.check_output(['pvesh','get',p,'--output-format','json']))
a=get();assert a['hostname']=='infra-webui' and a['memory'] in [3072,4096];changed=a['memory']!=4096
before=json.loads(subprocess.check_output(['pct','exec','631','--','docker','inspect','--format','{{json .State}}','ia-chat-open-webui-1']))
if changed:subprocess.run(['pvesh','set',p,'--memory','4096','--digest',a['digest']],check=True,stdout=subprocess.DEVNULL)
b=get();assert {k:v for k,v in a.items() if k not in ['memory','digest']}=={k:v for k,v in b.items() if k not in ['memory','digest']}
after=json.loads(subprocess.check_output(['pct','exec','631','--','docker','inspect','--format','{{json .State}}','ia-chat-open-webui-1']))
assert before['StartedAt']==after['StartedAt'];assert b['memory']==4096
cg=pathlib.Path('/sys/fs/cgroup/lxc/631');assert int((cg/'memory.max').read_text())==4096*1024**2
print(json.dumps({'memory_mib':4096,'changed':changed,'webui_restarted':False,'events':(cg/'memory.events').read_text()}))'''
ssh=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve'];r=subprocess.run(ssh+[shlex.join(['python3','-c',code])],capture_output=True);assert r.returncode==0,'RAM reconciliation failed; output withheld';print(r.stdout.decode())
(ROOT/'docs/roadmap/evidence/ia-chat-latency-2026-11-13/memory-resize.json').write_bytes(r.stdout)

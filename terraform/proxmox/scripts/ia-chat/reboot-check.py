#!/usr/bin/env python3
"""PVE: reboot solo630/631, espera servicios, validaIPs/alias/auth e historial."""
import subprocess,pathlib,json,time,datetime,urllib.request
root=pathlib.Path('/root/ia-local');out={'utc_start':datetime.datetime.now(datetime.timezone.utc).isoformat()}
def run(*args):return subprocess.run(args,text=True,capture_output=True,check=True).stdout.strip()
def ip(id):
 data=json.loads(run('pct','exec',id,'--','ip','-j','-4','addr','show','dev','eth0'));return [a['local'] for a in data[0]['addr_info'] if a['scope']=='global']
before={id:{'ip':ip(id),'boot_id':run('pct','exec',id,'--','cat','/proc/sys/kernel/random/boot_id')} for id in ['630','631']}
# Descargar modelo previo; el router no carga pesos grandes durante el arranque.
run('python3','/root/ia-local/validate-api.py','unload')
for id in ['630','631']:
 run('pct','reboot',id)
 for _ in range(90):
  try:
   afterboot=run('pct','exec',id,'--','cat','/proc/sys/kernel/random/boot_id')
   if afterboot!=before[id]['boot_id']:break
  except subprocess.CalledProcessError:pass
  time.sleep(2)
 else:raise SystemExit('Reboot no demostrado '+id)
 assert ip(id)==before[id]['ip'],('IP cambió',id,ip(id))
 if id=='630':
  for _ in range(30):
   try:
    assert run('pct','exec',id,'--','systemctl','is-active','llama-server')=='active';break
   except Exception:time.sleep(2)
  else:raise SystemExit('llama-server no activo')
 else:run('pct','exec',id,'--','python3','/root/wait-webui.py')
 out[id]={'before':before[id],'after':{'ip':ip(id),'boot_id':afterboot},'same_ip':True,'boot_changed':True}
run('python3','/root/ia-local/validate-api.py','api')
out['api_after_reboot']='PASS'
out['history_after_reboot']=run('pct','exec','631','--','python3','/root/webui-check.py','history-after-reboot')
with urllib.request.urlopen('http://192.168.1.66:3000',timeout=30) as r:out['ui_http']=r.status
out['utc_end']=datetime.datetime.now(datetime.timezone.utc).isoformat();(root/'reboot-verified.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

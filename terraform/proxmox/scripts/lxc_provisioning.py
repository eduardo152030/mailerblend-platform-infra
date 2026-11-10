"""Shared declaration/Notes/monitoring rendering for new inventory entries. No network/apply."""
import copy,hashlib,ipaddress,json,re,shutil
from pathlib import Path
import yaml
PENDING='PENDING VERIFICATION'
NODE_ARCHIVE='node_exporter-1.10.2.linux-amd64.tar.gz'
NODE_SHA256='c46e5b6f53948477ff3a19d97c58307394a29fe64a01905646f026ddc32cb65b'
def validate(data):
 s=data['service'];p=data['provisioning'];m=data['monitoring'];r=data['resources'];n=data['network']
 assert re.fullmatch(r'[a-z][a-z0-9-]{1,61}',s['name']),'Invalid service/hostname'
 assert isinstance(s['vmid'],int) and 100<=s['vmid']<=999999999,'Invalid CT ID'
 ip=ipaddress.ip_interface(s['ip']);assert ip.version==4 and ip.ip not in [ip.network.network_address,ip.network.broadcast_address]
 assert ipaddress.ip_address(n['gateway']) in ip.network and ipaddress.ip_address(n['gateway'])!=ip.ip,'Gateway outside subnet'
 assert isinstance(n['dns'],list) and n['dns']
 for address in n['dns']:ipaddress.ip_address(address)
 for field,minimum in [('cpu',1),('memory',128),('disk_gb',2)]:assert isinstance(r[field],int) and r[field]>=minimum
 assert isinstance(m['docker'],bool) and m['node_exporter'] is True
 assert data['os']['template_vmid']>=100 and data['os']['name'].strip()
 for field in ['environment','purpose','owner','backup']:assert isinstance(p[field],str) and p[field].strip()
 for field in ['applications','dependencies','domains','known_issues']:assert isinstance(p[field],list)
 assert isinstance(data['tags'],list) and data['tags']
 assert re.fullmatch(r'[a-zA-Z0-9_-]+',n['bridge']) and re.fullmatch(r'[a-zA-Z0-9_-]+',data['storage']['name'])
 assert not any(k.lower() in {'password','token','secret','private_key','api_key'} for obj in [s,p,m,n] for k in obj),'Secrets are not inventory inputs'
 for app in p['applications']:
  assert app['name'].strip() and app['runtime'] in ['systemd','docker'] and isinstance(app['ports'],list)
  assert m['docker'] or app['runtime']!='docker','Docker app on non-Docker CT'
 for probe in m.get('blackbox',[]):
  from urllib.parse import urlsplit
  url=urlsplit(probe['url']);assert url.scheme in ['http','https'] and url.hostname and not url.username and not url.password
  assert re.fullmatch(r'[a-zA-Z0-9_-]+',probe['module']) and probe['contract'].strip()
 return data

def pending_notes(data,key):
 validate(data);s=data['service'];p=data['provisioning'];m=data['monitoring'];r=data['resources'];n=data['network'];ct=s['vmid']
 apps='; '.join(a['name']+' ('+a['runtime']+'): '+', '.join(a['ports']) for a in p['applications']) or 'No applications declared; actual absence '+PENDING
 sections=[
  '**Purpose**\n'+p['purpose']+'\nDeployment: '+PENDING+' — declared only, no live observation.',
  '**Environment**\n'+p['environment']+'; owner: '+p['owner'],
  f'**Network**\nCT {ct}; {s["ip"]}; gateway {n["gateway"]}; DNS {", ".join(n["dns"])}; bridge {n["bridge"]}. Domains: '+(', '.join(p['domains']) or PENDING),
  '**Applications**\n'+apps+'\nAll application health: '+PENDING,
  '**Dependencies**\n'+('; '.join(p['dependencies']) or 'None declared; '+PENDING),
  '**Monitoring**\nNode Exporter 1.10.2 native systemd; CPU cgroup v2 textfile (native CPU collector disabled), RAM LXCFS/root disk. '+('cAdvisor 0.60.6 planned; exact socket/namespace approval required.' if m['docker'] else 'Docker/cAdvisor not required by declaration; no Docker agent installed.')+'\nUptime: existing PVE exporter; dashboards join published inventory. Endpoints: '+('; '.join(x['url']+' ['+x['contract']+']' for x in m.get('blackbox',[])) or PENDING)+'\nAll deployed monitoring/functional status: '+PENDING,
  f'**Infrastructure as Code**\ninventory/services/{key}.yml; Terraform resource svc["{key}"]; {r["cpu"]} CPU / {r["memory"]} MiB / {r["disk_gb"]} GiB; template {data["os"]["template_vmid"]} ({data["os"]["name"]}); storage {data["storage"]["name"]}.',
  f'**Documentation**\ndocs/inventory/{ct}-LXC-INVENTORY.md; docs/runbooks/NEW-LXC-PROVISIONING.md',
  '**Known Issues**\n'+'; '.join(p['known_issues'] or [PENDING])+'\nBackup/recovery: '+p['backup']]
 observed=p.get('verification')
 if observed:
  assert observed['result']=='PASS' and observed['ct_id']==ct and observed['service']==s['name'] and observed['state']=='RUNNING'
  assert observed['allocated_cores']==r['cpu'] and observed['memory_mib']==r['memory']
  sections[0]='**Purpose**\n'+p['purpose']+'\nDeployment: RUNNING observed '+observed['observed_at_utc']+'; stability/acceptance '+PENDING+'.'
  sections.append('**Observed (read-only gate)**\nCPU source: '+observed['cpu_source']+'; uptime '+str(observed['uptime_seconds'])+'s; allocation verified against PVE. Point-in-time observation, not business UAT or continuous acceptance.')
 return {'title':f'CT {ct} — {s["name"]}','sections':sections}

def inventory_document(data,key):
 notes=pending_notes(data,key)
 return '# '+notes['title']+'\n\nEstado: **'+PENDING+'**. Declaración preparada, no despliegue ni aceptación.\n\n'+ '\n\n'.join(notes['sections'])+'''\n\n## Arquitectura y operaciones

Aplicaciones y dependencias corresponden a declaraciones anteriores, no a procesos
observados. Validar plantilla/SO/LXCFS/cgroup, puertos, acceso y contrato funcional
antes de integrar monitorización. No aplicar el ejemplo ni usar deploy-all.
Operación: docs/runbooks/NEW-LXC-PROVISIONING.md. Sin reinicios automáticos de apps.
Rollback de alta: retirar primero discovery del CT nuevo, detener solo sus nuevos
exporters y conservar CT/volúmenes/datos para diagnóstico; no destroy automático.
Restauración/RPO/RTO/retención: PENDING VERIFICATION; no se afirma backup realizado.
Limitaciones: ejecución real, permisos/namespaces, origen de métricas y cadena de
alertas requieren primer ensayo autorizado y evidencia fechada.\n'''

def render_monitoring(data,out,root):
 validate(data);out=Path(out);out.mkdir(parents=True,exist_ok=True);s=data['service'];m=data['monitoring'];ct=s['vmid'];name=s['name'];ip=s['ip'].split('/')[0];cores=data['resources']['cpu']
 # Reuse the already accepted CPU producer; adapt only explicit identity/capacity/paths.
 body=(root/'services/common/pilot-624/node-cgroup.sh').read_text().replace('infra-journal-web',name).replace('"624"',json.dumps(str(ct))).replace('\\"624\\"','\\"'+str(ct)+'\\"').replace(' = 1 ]',f' = {cores} ]').replace('cores%s 1\\n',f'cores%s {cores}\\n').replace('${PILOT_HOST_ROOT:-/host}','${PILOT_HOST_ROOT:-/}').replace('${PILOT_METRIC_DIR:-/tmp/lxc-metrics}','${PILOT_METRIC_DIR:-/var/lib/node_exporter/textfile}')
 (out/'node-cgroup.sh').write_text(body)
 service='''[Unit]
Description=Node Exporter for this LXC (native CPU disabled)
After=network-online.target lxc-cpu.service
[Service]
User=nobody
Group=nogroup
ExecStart=/opt/lxc-monitoring/node_exporter --web.listen-address=IP:9100 --no-collector.cpu --collector.textfile.directory=/var/lib/node_exporter/textfile
Restart=on-failure
[Install]
WantedBy=multi-user.target
'''.replace('IP',ip)
 (out/'node-exporter.service').write_text(service)
 (out/'lxc-cpu.service').write_text('[Unit]\nDescription=LXC cgroup CPU textfile\n[Service]\nType=oneshot\nUser=nobody\nGroup=nogroup\nExecStart=/bin/sh /opt/lxc-monitoring/node-cgroup.sh --once\n')
 (out/'lxc-cpu.timer').write_text('[Unit]\nDescription=Refresh LXC CPU every5s\n[Timer]\nOnBootSec=5s\nOnUnitActiveSec=5s\nAccuracySec=1s\n[Install]\nWantedBy=timers.target\n')
 if m['docker']:
  compose=yaml.safe_load((root/'services/common/cadvisor/docker-compose.phase4.yml').read_text());cad=compose['services']['cadvisor'];cad['ports']=[f'{ip}:8085:8080'];cad['pull_policy']='missing';cad['command']+=['--allow_dynamic_housekeeping=false','--max_housekeeping_interval=30s','--jitter_factor=0','--initial_splay_factor=0']
  cad['volumes'].append('/run/containerd/containerd.sock:/run/containerd/containerd.sock:ro')
  (out/'cadvisor.yml').write_text(yaml.safe_dump(compose,sort_keys=False))
 targets={'node-exporter.json':[{'targets':[ip+':9100'],'labels':{'job':'node_exporter','service':name,'vmid':str(ct),'source':'inventory'}}],
          'cadvisor.json':([{'targets':[ip+':8085'],'labels':{'job':'cadvisor','service':name,'vmid':str(ct),'source':'inventory'}}] if m['docker'] else []),
          'blackbox.json':[{'targets':[p['url']],'labels':{'service':name,'vmid':str(ct),'module':p['module'],'probe_id':name+'-'+str(i),'probe_type':'internal','source':'inventory'}} for i,p in enumerate(m.get('blackbox',[]))]}
 modules={}
 for probe in m.get('blackbox',[]):
  if probe.get('body_regex'):
   re.compile(probe['body_regex'])
   modules[probe['module']]={'prober':'http','timeout':'5s','http':{'method':'GET','valid_status_codes':[200],'follow_redirects':False,'fail_if_body_not_matches_regexp':[probe['body_regex']]}}
 (out/'blackbox-modules.yml').write_text(yaml.safe_dump({'modules':modules},sort_keys=False))
 for fn,rows in targets.items():(out/fn).write_text(json.dumps(rows,indent=2)+'\n')
 # Expected inventory is a candidate until runtime receipt; never call a source verified merely from YAML.
 records={'groups':[{'name':'provisioned_'+str(ct),'rules':[{'record':'lxc:cpu_inventory:expected','expr':'vector(1)','labels':{'job':'node_exporter','instance':ip+':9100','service':name,'ct_id':str(ct)}},{'record':'lxc:cadvisor:required','expr':'vector('+str(int(m['docker']))+')','labels':{'service':name,'ct_id':str(ct)}}]}]}
 (out/'expected-inventory.yml').write_text(yaml.safe_dump(records,sort_keys=False))
 (out/'activation.json').write_text(json.dumps({'status':'PREPARED_NOT_DEPLOYED','node_cpu_contract_label':'BLOCKED until verify-new-lxc.py passes','cpu_rules':'existing lxc-cpu.yml, no physical fallback','cadvisor_required':m['docker'],'required_prerequisites':['fresh PVE identity/allocation/uptime','SSH known_hosts verified','LXCFS and cgroup metrics verified','Docker namespace/socket approval if required','valid functional probe modules','backup and rollback for monitoring transaction'],'publish':'merge additive targets into existing jobs and expected-inventory rule, then validated controlled reload; never replace all catalogs','blackbox_modules_required':sorted({p['module'] for p in m.get('blackbox',[])})},indent=2)+'\n')
 config={'ct_id':ct,'hostname':name,'ip':ip,'cpu':cores,'memory_mib':data['resources']['memory'],'docker':m['docker'],'node_archive':NODE_ARCHIVE,'node_sha256':NODE_SHA256}
 (out/'install-config.json').write_text(json.dumps(config,indent=2)+'\n')
 shutil.copy2(root/'templates/provisioning/install-monitoring.py',out/'install-monitoring.py')

#!/usr/bin/env python3
"""D060: deterministic Grafana LXC details, from existing scoped Prometheus metrics."""
import copy,json,runpy,re
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
f=runpy.run_path(str(ROOT/'scripts/generate-fleet-dashboard.py'))
DS=f['DS'];I=f['I'];identify=f['identify'];onlyct=f['onlyct'];probe_alias=f['probe_alias']
P=[]
def target(expr,ref='A',instant=True,legend='{{name}}'):
 return {'refId':ref,'expr':expr,'datasource':DS,'instant':instant,'range':not instant,'format':'table' if instant else 'time_series','legendFormat':legend,'editorMode':'code'}
def panel(title,kind,x,y,w,h,description=''):
 p={'id':len(P)+1,'title':title,'type':kind,'gridPos':{'x':x,'y':y,'w':w,'h':h},'datasource':DS,'description':description,'fieldConfig':{'defaults':{'noValue':'UNKNOWN','color':{'mode':'thresholds'},'thresholds':{'mode':'absolute','steps':[{'color':'green','value':None}]}},'overrides':[]},'options':{}}
 P.append(p);return p
fleet=json.loads((ROOT/'services/infra-grafana/config/provisioning/fleet-assets/proxmox-lxc-fleet.json').read_text())
health=copy.deepcopy(next(p for p in fleet['panels'] if p['title'].startswith('LXC health')))
health.update({'id':1,'title':'LXC · información y salud','gridPos':{'x':0,'y':0,'w':24,'h':7}});P.append(health)
# Both variables are scoped: a single CT selects exactly its service via the recorded inventory.
def scope(expr):
 return f'(({expr}) * on(service) group_left(ct_id) (0*{I}+1))'
def scalar(title,q,x,unit='short',description=''):
 p=panel(title,'stat',x,7,6,4,description);p['targets']=[target(q)];p['targets'][0]['format']='time_series';p['fieldConfig']['defaults']['unit']=unit;p['options']={'reduceOptions':{'calcs':['lastNotNull'],'fields':'','values':False},'textMode':'auto','colorMode':'value','graphMode':'none'};return p
scalar('CPU asignada',onlyct(scope('max by(service)(lxc_cpu_capacity_cores{job="node_exporter",resource_scope="lxc"})')),0,'short','Capacidad del cgroup LXC aceptada en F4; no CPUs del host.')
scalar('RAM asignada',onlyct(scope('max by(service)(node_memory_MemTotal_bytes{job="node_exporter"})')),6,'bytes','MemTotal virtualizado por LXCFS; no RAM física del host.')
scalar('Disco raíz · capacidad',onlyct(scope('max by(service)(node_filesystem_size_bytes{job="node_exporter",mountpoint="/",fstype!~"tmpfs|overlay|squashfs|aufs|ramfs"})')),12,'bytes','Capacidad real del filesystem raíz. No es la cuota declarada en Terraform ni maxdisk de PVE.')
p=scalar('Identidad e IP del LXC','label_replace('+scope('up{job="node_exporter"}')+',"ip","$1","instance","([^:]+):[0-9]+")',18,description='IP de gestión desde el target Node existente; nombre desde inventario publicado por IaC.')
p['options']['textMode']='name';p['targets'][0]['legendFormat']='CT {{ct_id}} · {{service}} · {{ip}}'
for title,key,x in [('CPU · histórico LXC','cpu',0),('RAM · histórico LXC','ram',8),('Disco · histórico raíz','disk',16)]:
 p=panel(title,'timeseries',x,11,8,7);p['targets']=[target(f[key],instant=False,legend='CT {{ct_id}}')];p['fieldConfig']['defaults'].update({'unit':'percent','min':0,'max':100,'color':{'mode':'palette-classic'},'custom':{'drawStyle':'line','lineWidth':2,'fillOpacity':8,'showPoints':'never','spanNulls':False}});p['options']={'legend':{'displayMode':'list','placement':'bottom'},'tooltip':{'mode':'multi'}}
p=panel('Red del LXC · recepción / transmisión','timeseries',0,18,12,7,'Interfaces Node del LXC, excluye loopback; bits/s, no tráfico del host ni de otros CT.')
for ref,direction in [('A','receive'),('B','transmit')]:
 p.setdefault('targets',[]).append(target(scope(f'8*sum by(service,device)(rate(node_network_{direction}_bytes_total{{job="node_exporter",device!="lo"}}[5m]))'),ref,False,direction+' {{device}}'))
p['fieldConfig']['defaults'].update({'unit':'bps','min':0,'color':{'mode':'palette-classic'}})
# Scope on service AND preserve cgroup ID. A Docker ID may occur in another LXC.
cs='job="cadvisor",name!=""'
alive=f'((container_last_seen{{{cs}}} >= time()-45) and (container_last_seen{{{cs}}} <= time()+2) and on(service) (min by(service)(up{{job="cadvisor"}}) == 1))'
join='instance,service,name,id'
def current(q):return scope(f'({q}) and on({join}) {alive}')
p=panel('Docker · contenedores activos del LXC','table',0,25,24,8,'Solo cgroups vistos ≤45s y cAdvisor UP del CT seleccionado. Estado=observado activo, no Docker State exacto. Reinicios no disponibles: no existe contador fiable; cambios de start_time no se etiquetan como reinicios. Healthcheck=-1 es sin check, no saludable.')
cols=[('A',current(f'0*{alive}+1'),'Observado activo'),('B',current(f'container_health_state{{{cs}}}'),'Healthcheck'),('C',current(f'100*sum by(instance,service,name,id)(rate(container_cpu_usage_seconds_total{{{cs}}}[5m]))'),'CPU (% de un core)'),('D',current(f'container_memory_working_set_bytes{{{cs}}}'),'RAM working set'),('E',current(f'time()-container_start_time_seconds{{{cs}}}'),'Tiempo desde arranque')]
p['targets']=[target(q,ref) for ref,q,_ in cols]
# Join by full scoped identity, never by bare name/id shared across LXCs.
for t in p['targets']:t['expr']=f'label_join({t["expr"]},"container_key","|","service","instance","id","name")'
names={'name':'Contenedor','container_label_com_docker_compose_service':'Compose service',**{'Value #'+ref:label for ref,_,label in cols}}
p['transformations']=[{'id':'joinByField','options':{'byField':'container_key','mode':'outerTabular'}},{'id':'filterFieldsByName','options':{'include':{'names':list(names)}}},{'id':'organize','options':{'renameByName':names}}]
def override(p,name,props):p['fieldConfig']['overrides'].append({'matcher':{'id':'byName','options':name},'properties':[{'id':k,'value':v} for k,v in props.items()]})
override(p,'Observado activo',{'mappings':f['mapping']({1:('ACTIVO (métrica fresca)','green')})})
override(p,'Healthcheck',{'mappings':f['mapping']({1:('HEALTHY','green'),0:('UNHEALTHY','red'),-1:('SIN HEALTHCHECK','text')}),'custom.cellOptions':{'type':'color-text'}})
for label,unit in [('CPU (% de un core)','percent'),('RAM working set','bytes'),('Tiempo desde arranque','dtdhms')]:override(p,label,{'unit':unit})
p['options']={'showHeader':True,'cellHeight':'sm','sortBy':[{'displayName':'Contenedor','desc':False}]}
# Canonicalize historical aliases BEFORE selection, retaining the actual endpoint label.
def probes(metric):return scope(probe_alias(metric))
p=panel('Aplicación · endpoints y sondas','table',12,18,12,7,'Disponibilidad del contrato de cada endpoint, no UAT. Readiness de Odoo/PG y CRM se presenta en los paneles específicos. Sin filas significa que no hay sonda Blackbox asociada, no que la app sea saludable.')
probe_queries=[('A',probes('probe_success{job="blackbox"}'),'Resultado'),('B',probes('probe_http_status_code{job="blackbox"}'),'HTTP'),('C',probes('probe_duration_seconds{job="blackbox"}'),'Duración (s)'),('D',probes('up{job="blackbox"}'),'Scrape UP')]
for ref,q,_ in probe_queries:p.setdefault('targets',[]).append(target(f'label_join({q},"probe_key","|","service","instance","module","probe_id")',ref))
names={'instance':'Endpoint','module':'Contrato',**{'Value #'+ref:label for ref,_,label in probe_queries}}
p['transformations']=[{'id':'joinByField','options':{'byField':'probe_key','mode':'outerTabular'}},{'id':'filterFieldsByName','options':{'include':{'names':list(names)}}},{'id':'organize','options':{'renameByName':names}}];p['options']={'showHeader':True,'cellHeight':'sm'}
for label in ['Resultado','Scrape UP']:override(p,label,{'mappings':f['mapping']({1:('UP','green'),0:('FALLO','red')}),'custom.cellOptions':{'type':'color-text'}})
override(p,'Duración (s)',{'unit':'s'})
p=panel('Aplicación · disponibilidad observada','timeseries',0,33,12,7,'Media de probe_success en ventanas de5min. Es disponibilidad de muestras recogidas; huecos/ausencia no garantizan disponibilidad continua.')
p['targets']=[target(probes('100*avg_over_time(probe_success{job="blackbox"}[5m])'),instant=False,legend='{{instance}}')];p['fieldConfig']['defaults'].update({'unit':'percent','min':0,'max':100,'color':{'mode':'palette-classic'}})
p=panel('Aplicación · latencia de la sonda','timeseries',12,33,12,7,'Duración total de la sonda HTTP/TCP según el módulo; no latencia de todas las operaciones de negocio.')
p['targets']=[target(probes('probe_duration_seconds{job="blackbox"}'),instant=False,legend='{{instance}}')];p['fieldConfig']['defaults'].update({'unit':'s','min':0,'color':{'mode':'palette-classic'}})
p=panel('Readiness · componentes esenciales','table',0,40,12,7,'Odoo/PostgreSQL:checks periódicos de lectura, frescura45s. CRM:healthchecks nativos por identidad/Compose y cgroup fresco. La ausencia de checks es ausencia de cobertura específica, no éxito.')
func=scope('lxc_app_check_success{job="node_exporter",health_source="functional_readonly"} and on(service,ct_id,component) (time()-lxc_app_check_timestamp_seconds{job="node_exporter"} <= 45)')
crm=current('container_health_state{job="cadvisor",service="infra-composable-crm",name=~"budibase-app|crm-api"}')
combined=f'(label_replace({func},"component","$1","component","(.+)")) or label_replace({crm},"component","$1","name","(.+)")'
p['targets']=[target(combined)];p['transformations']=[{'id':'filterFieldsByName','options':{'include':{'names':['component','Value']}}},{'id':'organize','options':{'renameByName':{'component':'Componente','Value':'Readiness'}}}];p['options']={'showHeader':True};override(p,'Readiness',{'mappings':f['mapping']({1:('HEALTHY (readiness)','green'),0:('CRITICAL','red'),-1:('UNKNOWN','gray')}),'custom.cellOptions':{'type':'color-text'}})
p=panel('Monitoring · targets y frescura','table',12,40,12,7,'Edad desde el scrape del target, no desde el arranque. FreshnessCPU y readiness se comprueban además mediante timestamps propios.')
monitor_base=scope('up{job=~"node_exporter|cadvisor"}')
monitor_probe=probes('up{job="blackbox"}')
pve_target=f'((0*{I}+1) * on() group_left(job,instance) up{{job="pve_uptime"}})'
mon=f'({monitor_base} or {monitor_probe} or {pve_target})'
node_age=scope('timestamp(up{job=~"node_exporter|cadvisor"})')
probe_age=probes('timestamp(up{job="blackbox"})')
pve_age=f'(time()-((0*{I}+1) * on() group_left(job,instance) timestamp(up{{job="pve_uptime"}})))'
node_source_age=scope('time()-lxc_cpu_collector_timestamp_seconds{job="node_exporter"}')
cad_source_age=scope('label_replace((time()-max by(service,instance)(container_last_seen{job="cadvisor",name!=""})),"job","cadvisor","instance",".*")')
probe_source_age=probes('time()-timestamp(probe_success{job="blackbox"})')
for ref,q in [('A',mon),('B',f'(time()-{node_age}) or (time()-{probe_age}) or {pve_age}'),('C',f'{node_source_age} or {cad_source_age} or {probe_source_age} or {pve_age}')]:
 p.setdefault('targets',[]).append(target(f'label_join({q},"target_key","|","job","instance","module","service")',ref))
names={'job':'Collector','instance':'Target','Value #A':'Scrape UP','Value #B':'Edad scrape (s)','Value #C':'Edad fuente (s)'}
p['transformations']=[{'id':'joinByField','options':{'byField':'target_key','mode':'outerTabular'}},{'id':'filterFieldsByName','options':{'include':{'names':list(names)}}},{'id':'organize','options':{'renameByName':names}}];p['options']={'showHeader':True};override(p,'Scrape UP',{'mappings':f['mapping']({1:('UP','green'),0:('DOWN','red')}),'custom.cellOptions':{'type':'color-text'}});override(p,'Edad scrape (s)',{'unit':'s'});override(p,'Edad fuente (s)',{'unit':'s'})
# Keep descriptions from the actual IaC rules; ALERTS itself does not export annotations.
rules=[]
for path in sorted((ROOT/'services/infra-prom/config/rules').glob('*.yml')):
 for group in yaml.safe_load(path.read_text()).get('groups',[]):
  rules.extend(r for r in group['rules'] if 'alert' in r)
# Descriptions are documented rule text; evaluation-dependent template values stay explicitly linked to Prometheus.
alert_rows=[]
for r in rules:
 desc=r.get('annotations',{}).get('description',r.get('annotations',{}).get('summary',r['alert']))
 desc=re.sub(r'{{.*?}}','[detalle de evaluación en Prometheus]',desc,flags=re.S)
 raw=f'ALERTS{{alertstate=~"firing|pending",alertname={json.dumps(r["alert"])}}}'
 row=scope(probe_alias(raw))
 row=f'label_replace({row},"description",{json.dumps(desc.replace("$","$$"),ensure_ascii=False)},"alertname",".*")'
 alert_rows.append(row)
p=panel('Alertas activas · CT $lxc','table',0,47,24,6,'Descripción del contrato IaC; valores interpolados/activeAt disponibles en Prometheus. Conserva severidad y estado reales de ALERTS. Sin filas con consulta correcta=sin alertas del CT.')
p['targets']=[target(' or '.join(alert_rows))];p['transformations']=[{'id':'filterFieldsByName','options':{'include':{'names':['alertname','alertstate','severity','service','name','description']}}},{'id':'sortBy','options':{'sort':[{'field':'severity','desc':False}]}}];p['options']={'showHeader':True};p['fieldConfig']['defaults']['noValue']='Sin alertas activas'
p['links']=[{'title':'Estado, descripción y tiempo activo en Prometheus','url':'http://192.168.1.110:9090/alerts','targetBlank':True}]
override(p,'alertname',{'links':[{'title':'Abrir regla en Prometheus','url':'http://192.168.1.110:9090/alerts','targetBlank':True}]})
# Optional documentation discovered from actual files, never links to absent/unpublished inventory pages.
doc_ids=sorted(p.name.split('-')[0] for p in (ROOT/'docs/inventory').glob('[0-9]*-LXC-INVENTORY.md'))
doc_regex='|'.join(doc_ids) or 'no_inventory_exists'
doc=f'label_replace(({I} and on(ct_id) label_replace(up{{job="node_exporter",vmid=~"{doc_regex}"}},"ct_id","$1","vmid","(.+)")),"inventory_path","docs/inventory/$1-LXC-INVENTORY.md","ct_id","(.+)")'
doc=f'({doc}) or on(ct_id) label_replace({I},"inventory_path","Sin ficha individual en repositorio","ct_id",".*")'
p=panel('Documentación · ficha local existente','table',0,53,12,4,'Ruta real del repositorio, no enlace web a archivos sin publicar. Las fichas opcionales se descubren al generar IaC. No se crean enlaces rotos.')
p['targets']=[target(doc)];p['transformations']=[{'id':'filterFieldsByName','options':{'include':{'names':['ct_id','inventory_path']}}}];p['options']={'showHeader':True}
p=panel('Contratos y límites','text',12,53,12,4)
p['options']={'mode':'markdown','content':'**CT seleccionado: $lxc · $service**\n\nSTOPPED solo desde Proxmox. Sin datos = UNKNOWN. DEMO no exime de supervisión. Readiness no es UAT.\n\nDocker muestra únicamente identidades frescas del LXC. CPU Docker usa % de **un core**; CPU LXC usa % de su capacidad. No existe contador fiable de reinicios.\n\nDisco: capacidad del filesystem raíz, no cuota Terraform. Frescura del scrape no sustituye timestamps del collector. Inventarios: rutas locales verificadas, sin enlaces web no publicados.'}
# Project identity labels once before joining numeric columns. Otherwise Grafana
# suffixes repeated name/instance fields (name1/name2...) and clutters the table.
for table in P:
 title=table['title']
 if title.startswith('Docker ·'):key='container_key';labels=['name','container_label_com_docker_compose_service']
 elif title=='Aplicación · endpoints y sondas':key='probe_key';labels=['instance','module']
 elif title=='Monitoring · targets y frescura':key='target_key';labels=['job','instance']
 else:continue
 project=[]
 for query in table['targets']:
  include=[key,'Value','Value #'+query['refId']]+(labels if query['refId']=='A' else [])
  project.append({'id':'filterFieldsByName','filter':{'id':'byRefId','options':query['refId']},'options':{'include':{'names':include}}})
 table['transformations']=project+table['transformations']
for table in P:
 if table['title']=='Readiness · componentes esenciales':table['fieldConfig']['defaults']['noValue']='Sin señal local; consultar endpoints'
variables=copy.deepcopy(fleet['templating']['list'])
variables=[variables[0],{'name':'lxc','label':'CT ID','type':'query','datasource':DS,'definition':'label_values(lxc:cpu_inventory:expected, ct_id)','query':{'query':'label_values(lxc:cpu_inventory:expected, ct_id)','refId':'CTDiscovery'},'refresh':2,'multi':False,'includeAll':False,'sort':3,'current':{}},{'name':'service','label':'Service','type':'query','datasource':DS,'definition':'label_values(lxc:cpu_inventory:expected{ct_id=~"${lxc:regex}"}, service)','query':{'query':'label_values(lxc:cpu_inventory:expected{ct_id=~"${lxc:regex}"}, service)','refId':'ServiceDiscovery'},'refresh':2,'multi':False,'includeAll':False,'current':{},'hide':0}]
d={'id':None,'uid':'proxmox-lxc-details','title':'Proxmox · LXC Details','description':'Diagnóstico de un LXC por CT ID, con métricas reales y ámbitos explícitos. D060.','tags':['proxmox','lxc','iac'],'timezone':'Europe/Madrid','schemaVersion':41,'version':1,'editable':False,'refresh':'30s','style':'dark','time':{'from':'now-6h','to':'now'},'templating':{'list':variables},'annotations':{'list':[]},'panels':P,'links':[{'title':'← Fleet Overview','type':'link','url':'/d/proxmox-lxc-fleet/proxmox-lxc-fleet-overview?var-lxc=${lxc}&var-service=%24__all&from=${__from}&to=${__to}&theme=dark','targetBlank':False}]}
# The shared health table's CT link should return to Fleet, rather than link to itself.
for ov in health['fieldConfig']['overrides']:
 if ov['matcher']['options']=='CT ID':
  for prop in ov['properties']:
   if prop['id']=='links':prop['value']=[{'title':'Volver a Fleet','url':d['links'][0]['url']}]
p=ROOT/'services/infra-grafana/config/provisioning/fleet-assets/proxmox-lxc-details.json';p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n');print(p.relative_to(ROOT))

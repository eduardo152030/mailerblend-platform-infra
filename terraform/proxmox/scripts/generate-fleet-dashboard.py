#!/usr/bin/env python3
"""D052: generate the fleet dashboard; no changes to Prometheus rules."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'services/infra-grafana'
DS={'type':'prometheus','uid':'${DS_PROMETHEUS}'}
SEL='ct_id=~"${lxc:regex}",service=~"${service:regex}"'
# Inventory derived from metrics; recording-rule inventory retains missing configured CTs.
I=f'(max by(ct_id,service)(label_replace(up{{job="node_exporter",vmid=~"${{lxc:regex}}",service=~"${{service:regex}}"}},"ct_id","$1","vmid","(.+)")) or max by(ct_id,service)(lxc:cpu_inventory:expected{{{SEL}}}))'
N='max by(service)(up{job="node_exporter"})'
C='min by(service)(up{job="cadvisor"})'
def identify(q):return f'(({q}) * on(service) group_left(ct_id) (0 * {I} + 1))'
def onlyct(q):return f'max by(ct_id)({q})'
node=onlyct(identify(N));cad=onlyct(identify(C));inv=onlyct(f'0*{I}')
# Prepared D061: default remains Docker-required for accepted legacy CTs.
cad_not_required=onlyct(f'0*({I} and on(service) (lxc:cadvisor:required == 0))')
cad=f'(({cad_not_required}-2) or {cad})'
cpu=onlyct(f'lxc:cpu_usage:percent{{{SEL}}} and on(service) ({N} == 1)')
ram=onlyct(identify(f'(100 * (1 - node_memory_MemAvailable_bytes{{job="node_exporter"}} / (node_memory_MemTotal_bytes{{job="node_exporter"}} > 0))) and on(service) ({N} == 1)'))
disk=onlyct(identify(f'(100 * (1 - node_filesystem_avail_bytes{{job="node_exporter",mountpoint="/",fstype!~"tmpfs|overlay|squashfs|aufs|ramfs"}} / (node_filesystem_size_bytes{{job="node_exporter",mountpoint="/",fstype!~"tmpfs|overlay|squashfs|aufs|ramfs"}} > 0))) and on(service) ({N} == 1)'))
# Explicit semantic aliases, never IP/CT guesses. Preserve original component names elsewhere.
def probe_alias(q):
 for source,dest in [('edge-nucleotecnologico-collect','infra-nucleoedge'),('edge-mailerblend-collect','infra-mailerblend-edge'),('infra-prometheus|infra-alertmanager','infra-prom')]:
  q=f'label_replace({q},"service","{dest}","service","{source}")'
 return q
p='(probe_success{job="blackbox"} and on(instance,module,service) (up{job="blackbox"} == 1))'
# A configured probe missing its value is UNKNOWN, not an inferred success.
p=f'({p} or on(instance,module,service) (0 * up{{job="blackbox"}} - 1))'
app=onlyct(identify(f'(min by(service)({probe_alias(p)} == 0) or min by(service)({probe_alias(p)}))'))
# D054: typed health. Monitoring is N/A as a business application; real service health remains separate.
monitor_services='infra-grafana|infra-blackbox'
monitor_inventory=onlyct(f'0*({I} and on(service) label_replace(up{{job="node_exporter",service=~"{monitor_services}"}},"ct_id","$1","vmid","(.+)"))')
monitor=onlyct(identify('(min by(service)(probe_success{job="blackbox",service="infra-grafana"} and on(instance,module,service) (up{job="blackbox"} == 1))) or label_replace(min(up{job="blackbox_exporter",instance="192.168.1.116:9115"}),"service","infra-blackbox","__name__",".*")'))
monitor=f'({monitor} or ({monitor_inventory}-1) or ({inv}-2))'
# Identity must match the Compose service; freshness must refer to the same Docker cgroup ID.
h='(container_health_state{job="cadvisor",service="infra-composable-crm",name="budibase-app",container_label_com_docker_compose_service="budibase-app"} or container_health_state{job="cadvisor",service="infra-composable-crm",name="crm-api",container_label_com_docker_compose_service="crm-api"})'
h=f'({h} and on(instance,service,name,id) ((time()-container_last_seen{{job="cadvisor"}} >= 0) and (time()-container_last_seen{{job="cadvisor"}} <= 45)) and (time()-timestamp({h}) <= 45))'
h=f'({h} and on(service,name) (count by(service,name)({h}) == 1))'
ready=f'(min by(service)({h}) and on(service) (count by(service)({h}) == 2) and on(service) (count by(service)(app:container:expected{{service="infra-composable-crm",name=~"budibase-app|crm-api"}}) == 2) and on(service) ({C} == 1))'
ready=onlyct(identify(f'((0*({ready} == 1)+2) or (0*({ready} == 0)))'))
crm_inventory=onlyct(f'0*({I} and on(service) up{{job="node_exporter",service="infra-composable-crm"}})')
worker_inventory=onlyct(f'0*({I} and on(service) up{{job="node_exporter",service="infra-excraper"}})')
worker_coverage=onlyct(identify('count by(service)(up{job="blackbox",service="infra-excraper",probe_id=~"excraper-linkedin-health|excraper-signals-health"}) == 2'))
worker_app=f'(({app} and on(ct_id) {worker_coverage}) or ({worker_inventory}-1))'
app=f'((({monitor_inventory}-2) or {ready} or ({crm_inventory}-1) or {worker_app} or {app}) or ({inv}-1))'
# D056: central read-only Proxmox API source, dynamically matched to the monitored CT inventory.
boot_contract=(ROOT/'services/infra-pve-uptime/uptime.promql').read_text().strip()
uptime=f'((({boot_contract}) and on(ct_id) ({I})) or ({inv}-1))'
unhealthy=onlyct(identify('count by(service)(container_health_state{job="cadvisor",name!="",name!~"cadvisor|node_exporter"} == 0)'))
firing=probe_alias('ALERTS{alertstate="firing"}')
alerts=onlyct(identify(f'count by(service)({firing})'))
alerts=f'({alerts} or {inv})'
critical_firing=probe_alias('ALERTS{alertstate="firing",severity="critical"}')
critical_alerts=onlyct(identify(f'count by(service)({critical_firing})'))
active=probe_alias('ALERTS{alertstate=~"firing|pending"}')
warning_alerts=onlyct(identify(f'count by(service)({active})'))
# D057: PVE state is authoritative; never infer STOPPED from missing exporters.
pve_raw='pve_up{job="pve_uptime",ct_id!=""}'
pve_state=onlyct(f'({pve_raw} and (time()-timestamp({pve_raw}) <= 45) and on(job,instance) (up{{job="pve_uptime"}} == 1) and on(ct_id) (count by(ct_id)({pve_raw}) == 1))')
pve_state=f'(({pve_state} and on(ct_id) {I}) or ({inv}-1))'
def scoped_inventory(regex):
 return onlyct(f'0*({I} and on(service) (up{{job="node_exporter",service=~"{regex}"}} or lxc:cpu_inventory:expected{{service=~"{regex}"}}))')
# CT613 is verified infra-only; DEMO is metadata, not a monitoring exemption.
no_application=scoped_inventory('infra-hola')
functional='lxc_app_check_success{job="node_exporter",health_source="functional_readonly"}'
functional=f'({functional} and on(service,ct_id,component) ((time()-lxc_app_check_timestamp_seconds{{job="node_exporter"}} >= 0) and (time()-lxc_app_check_timestamp_seconds{{job="node_exporter"}} <= 45)) and (time()-timestamp({functional}) <= 45) and on(service) ({N} == 1))'
functional=f'({functional} and on(service,ct_id,component) (count by(service,ct_id,component)({functional}) == 1))'
# All expected components are essential; collector uncertainty never becomes success.
functional_known=f'({functional} >= 0)'
functional_complete=f'((min by(service,ct_id)({functional_known}) and on(service,ct_id) (count by(service,ct_id)({functional_known}) == 2) and on(service) up{{job="node_exporter",service="infra-gestoria"}}) or (min by(service,ct_id)({functional_known}) and on(service,ct_id) (count by(service,ct_id)({functional_known}) == 1) and on(service) up{{job="node_exporter",service="infra-journal-db"}}))'
functional_ready=onlyct(f'((0*({functional_complete} == 1)+2) or (0*(min by(service,ct_id)({functional_known}) == 0)))')
functional_inventory=scoped_inventory('infra-gestoria|infra-journal-db')
app=f'((0*({pve_state} == 0)-3) or ({no_application}-2) or {functional_ready} or ({functional_inventory}-1) or {app})'
# Monitoring is a coverage/freshness assessment for every CT, separate from app success.
own_monitor=monitor
node_fresh=onlyct(identify('min by(service)(up{job="node_exporter"} and (time()-timestamp(up{job="node_exporter"}) <= 45))'))
cad_fresh=onlyct(identify('min by(service)(up{job="cadvisor"} and (time()-timestamp(up{job="cadvisor"}) <= 45))'))
node_status=f'({node_fresh} or ({inv}-1))'
cad_status=f'({cad_fresh} or ({inv}-1))'
cad_data=onlyct(identify('max by(service)((time()-container_last_seen{job="cadvisor",name!=""} >= 0) and (time()-container_last_seen{job="cadvisor",name!=""} <= 45))'))
resource_present=f'({inv} and {cpu} and {ram} and {disk})'
app_known=f'(({app} >= 0) or ({app} == -2))'
cad_coverage=f'((({cad_status} == 1) and {cad_data}) or {cad_not_required})'
monitor_good=f'(({node_status} == 1) and {cad_coverage} and {resource_present} and ({pve_state} >= 0) and ({uptime} >= 0) and {app_known} and ({own_monitor} != -1))'
monitor_bad=f'(({node_status} == 0) or ({own_monitor} == 0) or (({node_status} == -1) and ({cad_status} == 0)))'
monitor_partial=f'(({node_status} == 1) or ({cad_status} == 1))'
monitor=f'((0*{monitor_bad}) or (0*{monitor_good}+1) or (0*{monitor_partial}+2) or ({inv}-1))'
infra_critical=f'(({ram} > 90) or ({disk} > 95))'
infra_warning=f'(({cpu} > 90) or ({ram} > 80) or ({disk} > 85))'
infra_good=f'({resource_present} and ({pve_state} == 1) and ({node_status} == 1))'
infrastructure=f'((0*({pve_state} == 0)+4) or (0*{infra_critical}+3) or (0*{infra_warning}+2) or (0*{infra_good}) or ({inv}+1))'
critical=f'(({infrastructure} == 3) or ({app} == 0) or ({monitor} == 0) or ({critical_alerts} > 0))'
warning=f'(({infrastructure} == 2) or ({monitor} == 2) or ({unhealthy} > 0) or ({warning_alerts} > 0))'
known=f'(({infrastructure} == 0) and {app_known} and ({monitor} == 1) and ({pve_state} == 1))'
overall=f'((0*({pve_state} == 0)+4) or (0*{critical}+3) or (0*{warning}+2) or (0*{known}) or ({inv}+1))'
identity=f'0*{I}'
queries={'A':identity,'B':node,'C':cad,'D':app,'E':cpu,'F':ram,'G':disk,'H':alerts,'I':overall,'J':uptime,'K':monitor,'L':pve_state,'M':infrastructure}
# D060: constrain every derived branch (including functional checks) to selected inventory.
queries={k:f'({q}) and on(ct_id) {inv}' for k,q in queries.items()}
P=[]
def target(expr,ref='A',table=False):return {'refId':ref,'expr':expr,'datasource':DS,'instant':table,'range':not table,'format':'table' if table else 'time_series','legendFormat':'CT {{ct_id}} · {{service}}','editorMode':'code'}
def panel(title,kind,x,y,w,h):
 p={'id':len(P)+1,'title':title,'type':kind,'gridPos':{'x':x,'y':y,'w':w,'h':h},'datasource':DS,'fieldConfig':{'defaults':{'noValue':'UNKNOWN','mappings':[{'type':'special','options':{'match':'null','result':{'text':'UNKNOWN','color':'gray'}}}],'color':{'mode':'thresholds'},'thresholds':{'mode':'absolute','steps':[{'color':'green','value':None},{'color':'yellow','value':80},{'color':'red','value':90}]}},'overrides':[]},'options':{}}
 P.append(p);return p
for title,job,x,w in [('LXC monitorizados','node_exporter',0,5),('Node Exporter','node_exporter',5,5),('cAdvisor','cadvisor',10,5),('Blackbox · sondas','blackbox',15,5)]:
 p=panel(title,'stat',x,0,w,5)
 if title=='LXC monitorizados':
  exprs=[('Descubiertos','count(count by(vmid)(up{job="node_exporter",vmid!=""}))'),('En inventario CPU','count(count by(ct_id)(lxc:cpu_inventory:expected))')]
  p['description']='LXC descubiertos en targets Node frente a inventario CPU esperado. No son un inventario PVE vivo.'
 else:
  exprs=[('Disponibilidad',f'100*sum(up{{job="{job}"}})/count(up{{job="{job}"}})'),('UP',f'sum(up{{job="{job}"}})'),('Configurados',f'count(up{{job="{job}"}})')]
  p['description']='UP significa scrape correcto. En Blackbox no equivale a probe_success; ver disponibilidad de aplicación.'
 p['targets']=[dict(target(q,chr(65+i),True),legendFormat=name) for i,(name,q) in enumerate(exprs)]
 p['options']={'reduceOptions':{'calcs':['lastNotNull'],'fields':'','values':False},'textMode':'value_and_name','colorMode':'value','graphMode':'none','orientation':'horizontal'}
 for i,(name,q) in enumerate(exprs):
  p['fieldConfig']['overrides'].append({'matcher':{'id':'byFrameRefID','options':chr(65+i)},'properties':[{'id':'displayName','value':name},{'id':'unit','value':'percent' if name=='Disponibilidad' else 'short'},{'id':'color','value':{'mode':'thresholds'} if name=='Disponibilidad' else {'mode':'fixed','fixedColor':'text'}}]})
 p['fieldConfig']['defaults']['thresholds']['steps']=[{'color':'red','value':None},{'color':'yellow','value':1},{'color':'green','value':100}]
p=panel('Alertas FIRING','stat',20,0,4,5);p['targets']=[target('sum(ALERTS{alertstate="firing"}) or (0 * sum(up{job="prometheus"} == 1))',table=True)];p['options']={'reduceOptions':{'calcs':['lastNotNull']},'colorMode':'background_solid','graphMode':'none'};p['fieldConfig']['defaults']['thresholds']['steps']=[{'color':'green','value':None},{'color':'yellow','value':1},{'color':'red','value':5}]
p=panel('LXC health · priorización por estado','table',0,5,24,16);p['targets']=[target(q,r,True) for r,q in queries.items()]
names={'ct_id':'CT ID','service':'Service Name','Value #M':'Infrastructure Health','Value #D':'Application Health','Value #K':'Monitoring Health','Value #I':'Overall Status','Value #J':'Uptime','Value #L':'LXC State','Value #B':'Node Exporter','Value #C':'cAdvisor','Value #E':'CPU Usage (%)','Value #F':'RAM Usage (%)','Value #G':'Disk Usage (%)','Value #H':'Active Alerts'}
p['transformations']=[{'id':'joinByField','options':{'byField':'ct_id','mode':'outerTabular'}},{'id':'filterFieldsByName','options':{'include':{'names':list(names)}}},{'id':'organize','options':{'renameByName':names,'indexByName':{k:i for i,k in enumerate(names)}}},{'id':'sortBy','options':{'sort':[{'field':'Overall Status','desc':True}]}}]
p['options']={'showHeader':True,'cellHeight':'sm','footer':{'show':False},'sortBy':[{'displayName':'Overall Status','desc':True}]}
p['description']='D057: STOPPED solo desde PVE. Infrastructure y Monitoring Health para todos; CT613 DEMO infra-only verificado, sin exención de cobertura. Una fila por CT. Application Health: sondas HTTP reales o readiness interna CRM (no disponibilidad pública). Grafana/Blackbox: NOT APPLICABLE como negocio, Monitoring Health separado. Uptime real desde API Proxmox por CT ID; UNKNOWN si detenido/sin fuente fresca/duplicado. Nunca Docker ni boot del host. Umbrales F5 intactos.'
def override(p,field,properties):p['fieldConfig']['overrides'].append({'matcher':{'id':'byName','options':field},'properties':[{'id':k,'value':v} for k,v in properties.items()]})
def mapping(values):return [{'type':'value','options':{str(k):{'text':v[0],'color':v[1]} for k,v in values.items()}},{'type':'special','options':{'match':'null','result':{'text':'UNKNOWN','color':'gray'}}}]
for f in ['Node Exporter','cAdvisor']:
 override(p,f,{'mappings':mapping({0:('DOWN','red'),1:('Healthy' if f=='Application Health' else 'UP','green'),-1:('UNKNOWN','gray'),-2:('NOT APPLICABLE','text')}),'custom.cellOptions':{'type':'color-text'}})
override(p,'Application Health',{'mappings':mapping({0:('CRITICAL','red'),1:('HEALTHY','green'),2:('HEALTHY (readiness)','green'),-1:('UNKNOWN','gray'),-2:('NOT APPLICABLE','text'),-3:('STOPPED','red')}),'custom.cellOptions':{'type':'color-text'}})
override(p,'Monitoring Health',{'mappings':mapping({0:('CRITICAL','red'),1:('HEALTHY','green'),-1:('UNKNOWN','gray'),2:('DEGRADED','yellow')}),'custom.cellOptions':{'type':'color-text'}})
override(p,'Infrastructure Health',{'mappings':mapping({0:('HEALTHY','green'),1:('UNKNOWN','gray'),2:('WARNING','yellow'),3:('CRITICAL','red'),4:('STOPPED','red')}),'custom.cellOptions':{'type':'color-text'}})
override(p,'LXC State',{'mappings':mapping({0:('STOPPED','red'),1:('RUNNING','green'),-1:('UNKNOWN','gray')})})
override(p,'Uptime',{'unit':'dtdhms','decimals':0,'mappings':mapping({-1:('UNKNOWN','gray')}),'custom.width':135})
override(p,'Overall Status',{'mappings':mapping({0:('HEALTHY','green'),1:('UNKNOWN','gray'),2:('WARNING','yellow'),3:('CRITICAL','red'),4:('STOPPED','red')}),'custom.cellOptions':{'type':'color-background'}})
for f,warning,critical_v in [('CPU Usage (%)',90,101),('RAM Usage (%)',80,90),('Disk Usage (%)',85,95)]:
 override(p,f,{'unit':'percent','min':0,'max':100,'decimals':1,'custom.cellOptions':{'type':'gauge','mode':'basic'},'thresholds':{'mode':'absolute','steps':[{'color':'green','value':None},{'color':'yellow','value':warning},{'color':'red','value':critical_v}]}})
override(p,'CT ID',{'links':[{'title':'Abrir LXC Details','url':'/d/proxmox-lxc-details/proxmox-lxc-details?var-lxc=${__value.raw}&from=${__from}&to=${__to}&theme=dark'}],'custom.width':95})
for field,width in [('Service Name',210),('Infrastructure Health',145),('Application Health',185),('Monitoring Health',140),('Overall Status',120),('Uptime',150),('LXC State',100),('Node Exporter',100),('cAdvisor',90)]:override(p,field,{'custom.width':width})
for i,(title,q,warn,crit) in enumerate([('CPU Usage by LXC',cpu,90,101),('Memory Usage by LXC',ram,80,90),('Disk Usage by LXC',disk,85,95)]):
 p=panel(title,'timeseries',i*8,21,8,9);p['targets']=[target(f'({q}) * on(ct_id) group_left(service) (0*{I}+1)')];p['fieldConfig']['defaults'].update({'unit':'percent','min':0,'max':100,'decimals':1,'color':{'mode':'palette-classic'},'custom':{'drawStyle':'line','lineWidth':2,'fillOpacity':8,'showPoints':'never','spanNulls':False,'thresholdsStyle':{'mode':'dashed'}},'thresholds':{'mode':'absolute','steps':[{'color':'green','value':None},{'color':'yellow','value':warn},{'color':'red','value':crit}]}});p['options']={'legend':{'displayMode':'table','placement':'bottom','calcs':['lastNotNull','max']},'tooltip':{'mode':'multi','sort':'desc'}}
p=panel('Active alerts · FIRING / PENDING','table',0,30,24,6);p['fieldConfig']['defaults']['noValue']='Sin alertas activas';p['fieldConfig']['defaults']['mappings']=[]
# ALERTS exports labels, not annotations or activeAt. Expose available data and link to the actual API-backed Prometheus UI.
full_inventory=I.replace('${lxc:regex}','.*').replace('${service:regex}','.*')
def scoped_alerts(severity=''):
 raw=probe_alias('ALERTS{alertstate=~"firing|pending"'+severity+'}')
 return f'({identify(raw)} or ({raw} unless on(service) {full_inventory}))'
critical_rows=scoped_alerts(',severity="critical"')
warning_rows=scoped_alerts(',severity="warning"')
rank=f'(0*{critical_rows}+3) or (0*{warning_rows}+2) or (0*{scoped_alerts()}+1)'
p['targets']=[target(rank,table=True)];p['transformations']=[{'id':'filterFieldsByName','options':{'include':{'names':['alertname','alertstate','severity','service','ct_id','instance','name','Value']}}},{'id':'organize','options':{'renameByName':{'Value':'Prioridad'}}},{'id':'sortBy','options':{'sort':[{'field':'Prioridad','desc':True}]}}];p['description']='Sin filas = sin alertas activas (si datasource disponible). ALERTS no expone descripción ni activeAt; consultar Prometheus mediante el enlace. Incluye alertas globales sin service para no ocultarlas al filtrar. No hay historial RESOLVED inventado.';p['links']=[{'title':'Descripción, tiempo activo y reglas en Prometheus','url':'http://192.168.1.110:9090/alerts','targetBlank':True}];p['options']={'showHeader':True,'cellHeight':'sm'}
p=panel('Cobertura y navegación','text',0,36,24,8);p['id']+=1;p['options']={'mode':'markdown','content':'### Fleet observability\nActualización **30 s** · Infraestructura y monitorización supervisadas en todos los CT · CPU cgroup LXC · RAM LXCFS · disco raíz.\n\n**UNKNOWN** conserva la ausencia de datos. Application Health combina sondas verificadas y readiness CRM explícita. Readiness no acredita disponibilidad pública. Grafana/Blackbox y CT613 sin app: NOT APPLICABLE solo en Application Health. Monitoring Health nunca N/A; STOPPED procede de Proxmox. CT613 DEMO es metadato, no mantenimiento ni exención. Uptime desde API Proxmox por CT ID, con estado running y frescura. No depende de Docker ni del boot del host.\n\nSeleccione un **CT ID** para abrir **LXC Details**, conservando el rango temporal. Desde Details puede volver a Fleet.\n\nAlertas: descripción y tiempo activo en [Prometheus](http://192.168.1.110:9090/alerts). Sin historial RESOLVED.\n\nGrafana es dinámico; el alta de targets Prometheus requiere el proceso IaC documentado.'}
variables=[{'name':'DS_PROMETHEUS','type':'datasource','query':'prometheus','regex':'/^Prometheus$/','hide':2,'refresh':1,'current':{'text':'Prometheus','value':'PBFA97CFB590B2093'}},]
for name,label,q in [('service','Service','label_values(up{job="node_exporter"}, service)'),('lxc','LXC','label_values(up{job="node_exporter",service=~"${service:regex}"}, vmid)')]:
 variables.append({'name':name,'label':label,'type':'query','datasource':DS,'definition':q,'query':{'query':q,'refId':'StandardVariableQuery'},'refresh':2,'multi':True,'includeAll':True,'allValue':'.*','sort':3 if name=='lxc' else 1,'current':{'text':'All','value':'$__all'}})
d={'id':None,'uid':'proxmox-lxc-fleet','title':'Proxmox · LXC Fleet Overview','description':'Estado de salud, disponibilidad y recursos de la infraestructura LXC.','tags':['proxmox','lxc','fleet','iac','D052'],'timezone':'Europe/Madrid','schemaVersion':41,'version':1,'editable':False,'style':'dark','refresh':'30s','time':{'from':'now-6h','to':'now'},'timepicker':{'refresh_intervals':['30s','1m','5m']},'templating':{'list':variables},'annotations':{'list':[]},'panels':P,'links':[]}
for panel_item in P:
 if panel_item['title']=='CPU Usage by LXC':
  panel_item['fieldConfig']['defaults']['thresholds']['steps']=[{'color':'green','value':None},{'color':'yellow','value':90}]
 if panel_item['title'].startswith('LXC health'):
  for ov in panel_item['fieldConfig']['overrides']:
   if ov['matcher']['options']=='CPU Usage (%)':
    for prop in ov['properties']:
     if prop['id']=='thresholds':prop['value']['steps']=[{'color':'green','value':None},{'color':'yellow','value':90}]
out=BASE/'config/provisioning/fleet-assets/proxmox-lxc-fleet.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
print(out.relative_to(ROOT))

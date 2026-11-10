"""D060 regression: filtering, cloned Docker IDs, missing data and future CTs."""
import json,subprocess,tempfile,unittest
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]
class Details(unittest.TestCase):
 def test_isolation_and_new_ct(self):
  model=json.loads((ROOT/'services/infra-grafana/config/provisioning/fleet-assets/proxmox-lxc-details.json').read_text())
  fleet=json.loads((ROOT/'services/infra-grafana/config/provisioning/fleet-assets/proxmox-lxc-fleet.json').read_text())
  health=next(p for p in model['panels'] if p['title'].startswith('LXC ·'))
  def expr(p,ref='A',ct='9999',service='future'):
   return next(t['expr'] for t in p['targets'] if t['refId']==ref).replace('${lxc:regex}',ct).replace('${service:regex}',service)
  base={'lxc:cpu_inventory:expected{ct_id="9999",service="future",instance="192.0.2.1:9100"}':'1+0x4','up{job="node_exporter",service="future",vmid="9999",instance="192.0.2.1:9100"}':'1+0x4','up{job="cadvisor",service="future",instance="192.0.2.1:8085"}':'1+0x4','lxc_cpu_capacity_cores{job="node_exporter",resource_scope="lxc",service="future"}':'2+0x4'}
  cases=[]
  def case(name,data,q,rows):cases.append({'name':name,'interval':'30s','input_series':[{'series':k,'values':v} for k,v in data.items()],'promql_expr_test':[{'expr':q,'eval_time':'2m','exp_samples':rows}]})
  cpu=next(p for p in model['panels'] if p['title']=='CPU asignada')
  case('future-CT-no-dashboard-edit',base,expr(cpu),[{'labels':'{ct_id="9999"}','value':2}])
  # A global Odoo/PG source must not leak into a selected unrelated CT.
  crossed={**base,'up{job="node_exporter",service="infra-gestoria",vmid="623"}':'1+0x4'}
  for comp in ['odoo','postgres']:
   crossed[f'lxc_app_check_success{{job="node_exporter",service="infra-gestoria",ct_id="623",component="{comp}",health_source="functional_readonly"}}']='1+0x4'
   crossed[f'lxc_app_check_timestamp_seconds{{job="node_exporter",service="infra-gestoria",ct_id="623",component="{comp}"}}']='0+30x4'
  case('readiness-never-leaks-between-CTs',crossed,expr(health,'D'),[{'labels':'{ct_id="9999"}','value':-1}])
  dock=next(p for p in model['panels'] if p['title'].startswith('Docker ·'))
  docker=dict(base)
  for service,instance in [('future','192.0.2.1:8085'),('other','192.0.2.2:8085')]:
   label=f'job="cadvisor",service="{service}",instance="{instance}",name="cloned",id="same-id"'
   docker['container_last_seen{'+label+'}']='0+30x4';docker['container_health_state{'+label+'}']='1+0x4'
  samples=[{'labels':'{job="cadvisor",service="future",instance="192.0.2.1:8085",name="cloned",id="same-id",ct_id="9999",container_key="future|192.0.2.1:8085|same-id|cloned"}','value':1}]
  case('Docker-cloned-ID-only-selected-LXC',docker,expr(dock,'B'),samples)
  stale={k:('0+0x4' if k.startswith('container_last_seen') else v) for k,v in docker.items()}
  case('stale-containers-not-active',stale,expr(dock,'B'),[])
  tool=Path.home()/'.local/share/mailerblend-recovery/phase5/d050/promtool'
  with tempfile.TemporaryDirectory() as td:
   path=Path(td)/'tests.yml';path.write_text(yaml.safe_dump({'rule_files':[],'evaluation_interval':'30s','tests':cases}))
   r=subprocess.run([str(tool),'test','rules',str(path)],capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stdout+r.stderr)
if __name__=='__main__':unittest.main()

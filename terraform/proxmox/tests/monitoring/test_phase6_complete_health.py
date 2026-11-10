"""Exercise fleet failure semantics with the real PromQL evaluator."""
import json, subprocess, tempfile, unittest
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]
class CompleteHealth(unittest.TestCase):
 def test_failure_semantics(self):
  model=json.loads((ROOT/'services/infra-grafana/config/provisioning/fleet-assets/proxmox-lxc-fleet.json').read_text())
  panel=next(p for p in model['panels'] if p['title'].startswith('LXC health'))
  expr={t['refId']:t['expr'].replace('${lxc:regex}','.*').replace('${service:regex}','.*') for t in panel['targets']}
  cases=[]
  base={'up{job="node_exporter",service="infra-hola",vmid="613"}':'1+0x4'}
  def case(name,data,ref,value):
   cases.append({'name':name,'interval':'30s','input_series':[{'series':k,'values':v} for k,v in data.items()],'promql_expr_test':[{'expr':expr[ref],'eval_time':'2m','exp_samples':[{'labels':'{ct_id="613"}','value':value}]}]})
  case('no-business-app-verified',base,'D',-2)
  case('missing-resource-coverage-degraded',base,'K',2)
  case('missing-pve-never-stopped',base,'L',-1)
  case('missing-pve-overall-warning',base,'I',2)
  stopped={**base,'pve_up{job="pve_uptime",instance="pve",ct_id="613"}':'0+0x4','up{job="pve_uptime",instance="pve"}':'1+0x4'}
  for ref,value in [('L',0),('D',-3),('M',4),('I',4)]:case('pve-stopped-'+ref,stopped,ref,value)
  down={k:'0+0x4' for k in base};case('node-down-critical',down,'K',0);case('critical-propagates',down,'I',3)
  unknown={'lxc:cpu_inventory:expected{service="infra-hola",ct_id="613"}':'1+0x4'}
  case('absent-exporters-unknown',unknown,'K',-1);case('absent-is-not-healthy',unknown,'I',1)
  pg={'up{job="node_exporter",service="infra-journal-db",vmid="613"}':'1+0x4','lxc_app_check_success{job="node_exporter",service="infra-journal-db",ct_id="613",component="postgres",health_source="functional_readonly"}':'1+0x4','lxc_app_check_timestamp_seconds{job="node_exporter",service="infra-journal-db",ct_id="613",component="postgres"}':'0+30x4'}
  case('pg-readiness',pg,'D',2)
  case('pg-failure',{k:('0+0x4' if k.startswith('lxc_app_check_success') else v) for k,v in pg.items()},'D',0)
  case('pg-stale',{k:('0+0x4' if k.startswith('lxc_app_check_timestamp') else v) for k,v in pg.items()},'D',-1)
  case('pg-unknown',{k:('-1+0x4' if k.startswith('lxc_app_check_success') else v) for k,v in pg.items()},'D',-1)
  tool=Path.home()/'.local/share/mailerblend-recovery/phase5/d050/promtool'
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'tests.yml';p.write_text(yaml.safe_dump({'rule_files':[],'evaluation_interval':'30s','tests':cases}))
   r=subprocess.run([str(tool),'test','rules',str(p)],capture_output=True,text=True)
   self.assertEqual(r.returncode,0,r.stdout+r.stderr)
if __name__=='__main__':unittest.main()

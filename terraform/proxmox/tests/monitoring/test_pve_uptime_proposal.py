"""D056 local-only PromQL contract, without Proxmox writes or credentials."""
import json,subprocess,tempfile,unittest
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]
class Uptime(unittest.TestCase):
 def test_reading_contract(self):
  expr=(ROOT/'services/infra-pve-uptime/uptime.promql').read_text()
  base={'pve_uptime_seconds{job="pve_uptime",instance="exporter",id="lxc/9999",ct_id="9999"}':'500 530 5 35 65','pve_up{job="pve_uptime",instance="exporter",id="lxc/9999",ct_id="9999"}':'1+0x4','up{job="pve_uptime",instance="exporter"}':'1+0x4'}
  tests=[]
  def case(name,ss,time,want):tests.append({'name':name,'interval':'30s','input_series':[{'series':k,'values':v} for k,v in ss.items()],'promql_expr_test':[{'expr':expr,'eval_time':time,'exp_samples':[] if want is None else [{'labels':'{ct_id="9999"}','value':want}]}]})
  case('before-lxc-restart',base,'30s',530);case('after-lxc-restart',base,'1m',5)
  case('source-down',{k:('0+0x4' if k.startswith('up{') else v) for k,v in base.items()},'1m',None)
  case('ct-stopped',{k:('0+0x4' if k.startswith('pve_up{') else v) for k,v in base.items()},'1m',None)
  case('old-sample',{k:('500 _ _ _ _' if k.startswith('pve_uptime') else v) for k,v in base.items()},'2m',None)
  dup=dict(base);dup.update({k.replace('instance="exporter"','instance="duplicate"'):v for k,v in base.items()});case('duplicate-ct',dup,'1m',None)
  case('no-source-host-boot-only',{'node_boot_time_seconds{ct_id="9999"}':'0+0x4'},'1m',None)
  case('missing-state',{k:v for k,v in base.items() if not k.startswith('pve_up{')},'1m',None)
  model=json.loads((ROOT/'services/infra-grafana/config/provisioning/fleet-assets/proxmox-lxc-fleet.json').read_text());table=next(p for p in model['panels'] if p['title'].startswith('LXC health'));generated=next(t['expr'] for t in table['targets'] if t['refId']=='J').replace('${lxc:regex}','.*').replace('${service:regex}','.*')
  dynamic=dict(base);dynamic['up{job="node_exporter",service="brand-new",vmid="9999"}']='1+0x4'
  tests.append({'name':'future-lxc-joined-without-dashboard-edit','interval':'30s','input_series':[{'series':k,'values':v} for k,v in dynamic.items()],'promql_expr_test':[{'expr':generated,'eval_time':'1m','exp_samples':[{'labels':'{ct_id="9999"}','value':5}]}]})
  pt=Path.home()/'.local/share/mailerblend-recovery/phase5/d050/promtool'
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'tests.yml';p.write_text(yaml.safe_dump({'rule_files':[],'evaluation_interval':'30s','tests':tests}));r=subprocess.run([str(pt),'test','rules',str(p)],capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stdout+r.stderr)
   p=Path(td)/'prom.yml';job=yaml.safe_load((ROOT/'services/infra-prom/proposals/pve-uptime/scrape.yml').read_text());p.write_text(yaml.safe_dump({'scrape_configs':[job]}));r=subprocess.run([str(pt),'check','config',str(p)],capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stdout+r.stderr)
if __name__=='__main__':unittest.main()

"""D054: readiness identity/freshness, monitoring semantics and host-boot rejection."""
import json,subprocess,tempfile,unittest
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]
class StageA(unittest.TestCase):
 def test_contracts(self):
  d=json.loads((ROOT/'services/infra-grafana/config/provisioning/fleet-assets/proxmox-lxc-fleet.json').read_text());table=next(p for p in d['panels'] if p['title'].startswith('LXC health'));exprs={t['refId']:t['expr'].replace('${lxc:regex}','.*').replace('${service:regex}','.*') for t in table['targets']}
  base={'up{job="node_exporter",service="infra-composable-crm",vmid="618"}':'1+0x4','up{job="cadvisor",service="infra-composable-crm"}':'1+0x4'}
  for name in ['budibase-app','crm-api']:
   labels=f'job="cadvisor",instance="test",service="infra-composable-crm",name="{name}",id="{name}-id",container_label_com_docker_compose_service="{name}"'
   base['container_health_state{'+labels+'}']='1+0x4';base['container_last_seen{'+labels+'}']='0+30x4';base[f'app:container:expected{{service="infra-composable-crm",name="{name}"}}']='1+0x4'
  cases=[]
  def case(name,ss,ref,want,ct='618'):
   cases.append({'name':name,'interval':'30s','input_series':[{'series':k,'values':v} for k,v in ss.items()],'promql_expr_test':[{'expr':exprs[ref],'eval_time':'2m','exp_samples':[{'labels':f'{{ct_id="{ct}"}}','value':want}]}]})
  case('crm-readiness',base,'D',2)
  case('crm-missing-component',{k:v for k,v in base.items() if not (k.startswith('container_health') and 'name="crm-api"' in k)},'D',-1)
  case('crm-stale',{k:('0+0x4' if k.startswith('container_last_seen') else v) for k,v in base.items()},'D',-1)
  case('crm-wrong-compose-identity',{k.replace('container_label_com_docker_compose_service="crm-api"','container_label_com_docker_compose_service="wrong"'):v for k,v in base.items()},'D',-1)
  case('crm-unhealthy',{k:('0+0x4' if k.startswith('container_health') and 'name="crm-api"' in k else v) for k,v in base.items()},'D',0)
  case('crm-cadvisor-down',{k:('0+0x4' if k.startswith('up{job="cadvisor"') else v) for k,v in base.items()},'D',-1)
  duplicate=dict(base);duplicate.update({k.replace('id="crm-api-id"','id="duplicate"'):v for k,v in base.items() if k.startswith('container_') and 'name="crm-api"' in k});case('crm-duplicate',duplicate,'D',-1)
  mon={'up{job="node_exporter",service="infra-blackbox",vmid="616"}':'1+0x4','up{job="blackbox_exporter",instance="192.168.1.116:9115"}':'1+0x4'}
  case('monitor-not-business',mon,'D',-2,'616');case('own-endpoint-up-without-fleet-coverage-is-degraded',mon,'K',2,'616')
  boot={'up{job="node_exporter",service="new",vmid="999"}':'1+0x4','node_boot_time_seconds{job="node_exporter",service="new"}':'0+0x4'}
  case('host-boot-rejected',boot,'J',-1,'999')
  trusted={k.replace('service="new"}', 'service="new",boot_scope="lxc_verified"}'):v for k,v in boot.items()}
  case('tagged-node-boot-still-rejected',trusted,'J',-1,'999')
  workers={'up{job="node_exporter",service="infra-excraper",vmid="620"}':'1+0x4'}
  for probe in ['excraper-linkedin-health','excraper-signals-health']:
   labels=f'job="blackbox",service="infra-excraper",probe_id="{probe}",instance="{probe}",module="health"'
   workers['up{'+labels+'}']='1+0x4';workers['probe_success{'+labels+'}']='1+0x4'
  case('two-workers-healthy',workers,'D',1,'620')
  case('missing-worker',{k:v for k,v in workers.items() if 'excraper-signals-health' not in k},'D',-1,'620')
  case('failed-worker',{k:('0+0x4' if k.startswith('probe_success') and 'excraper-signals-health' in k else v) for k,v in workers.items()},'D',0,'620')
  pt=Path.home()/'.local/share/mailerblend-recovery/phase5/d050/promtool'
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'tests.yml';p.write_text(yaml.safe_dump({'rule_files':[],'evaluation_interval':'30s','tests':cases}));r=subprocess.run([str(pt),'test','rules',str(p)],capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stdout+r.stderr)
if __name__=='__main__':unittest.main()

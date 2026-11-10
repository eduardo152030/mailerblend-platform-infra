"""Synthetic PromQL fault cases using the actual dashboard expressions, no production writes."""
import json,os,subprocess,tempfile,unittest
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]
class FleetContract(unittest.TestCase):
 def test_states(self):
  dashboard=json.loads((ROOT/'services/infra-grafana/config/provisioning/fleet-assets/proxmox-lxc-fleet.json').read_text())
  expr=next(p for p in dashboard['panels'] if p['title'].startswith('LXC health'))['targets'][8]['expr']
  expr=expr.replace('${lxc:regex}','.*').replace('${service:regex}','.*')
  series={
   'up{job="pve_uptime",instance="pve"}':'1',
   'pve_up{job="pve_uptime",instance="pve",ct_id="999",id="lxc/999"}':'1',
   'pve_uptime_seconds{job="pve_uptime",instance="pve",ct_id="999",id="lxc/999"}':'500',
   'container_last_seen{job="cadvisor",service="new-service",name="app"}':'60',

   'up{job="node_exporter",service="new-service",vmid="999"}':'1',
   'up{job="cadvisor",service="new-service"}':'1',
   'lxc:cpu_usage:percent{service="new-service",ct_id="999"}':'25',
   'node_memory_MemAvailable_bytes{job="node_exporter",service="new-service"}':'50',
   'node_memory_MemTotal_bytes{job="node_exporter",service="new-service"}':'100',
   'node_filesystem_avail_bytes{job="node_exporter",service="new-service",mountpoint="/",fstype="ext4"}':'50',
   'node_filesystem_size_bytes{job="node_exporter",service="new-service",mountpoint="/",fstype="ext4"}':'100',
   'up{job="blackbox",service="new-service",instance="http://test",module="http_2xx"}':'1',
   'probe_success{job="blackbox",service="new-service",instance="http://test",module="http_2xx"}':'1',
  }
  def changed(prefix,value):return {k:(value if k.startswith(prefix) else v) for k,v in series.items()}
  cases=[('healthy-new-ct',series,0),('missing-cpu-degrades-coverage',{k:v for k,v in series.items() if not k.startswith('lxc:cpu_usage')},2),('missing-app-degrades-coverage',{k:v for k,v in series.items() if 'blackbox' not in k},2),('node-down',changed('up{job="node_exporter"','0'),3),('app-down',changed('probe_success','0'),3),('ram-warning',changed('node_memory_MemAvailable','15'),2),('ram-critical',changed('node_memory_MemAvailable','5'),3),('no-probe-result-degrades-coverage',{k:v for k,v in series.items() if not k.startswith('probe_success')},2),('failure-and-unknown',dict(changed('probe_success','0'),**{'up{job="blackbox",service="new-service",instance="http://missing",module="http_2xx"}':'1'}),3)]
  cases.extend([('docker-unhealthy',dict(series,**{'container_health_state{job="cadvisor",service="new-service",name="app"}':'0'}),2),('critical-alert',dict(series,**{'ALERTS{service="new-service",alertstate="firing",severity="critical",alertname="Synthetic"}':'1'}),3),('alias-alert',dict({k.replace('new-service','infra-nucleoedge'):v for k,v in series.items()},**{'ALERTS{service="edge-nucleotecnologico-collect",alertstate="firing",severity="critical",alertname="Synthetic"}':'1'}),3)])
  tests=[]
  for name,ss,want in cases:
   tests.append({'name':name,'interval':'30s','input_series':[{'series':k,'values':v+'+0x2'} for k,v in ss.items()],'promql_expr_test':[{'expr':expr,'eval_time':'1m','exp_samples':[{'labels':'{ct_id="999"}','value':want}]}]})
  with tempfile.TemporaryDirectory() as td:
   path=Path(td)/'tests.yml';path.write_text(yaml.safe_dump({'rule_files':[],'evaluation_interval':'30s','tests':tests}))
   pt=os.environ.get('PROMTOOL',str(Path.home()/'.local/share/mailerblend-recovery/phase5/d050/promtool'))
   r=subprocess.run([pt,'test','rules',str(path)],capture_output=True,text=True)
   self.assertEqual(r.returncode,0,r.stdout+r.stderr)
if __name__=='__main__':unittest.main()

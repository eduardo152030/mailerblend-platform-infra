import copy,importlib.util,json,subprocess,sys,tempfile,unittest
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from lxc_provisioning import validate,pending_notes,inventory_document,render_monitoring
class Provisioning(unittest.TestCase):
 def setUp(self):self.data=yaml.safe_load((ROOT/'examples/new-lxc/service.yml').read_text())
 def test_required_inputs(self):
  for key in ['service','resources','network','os','provisioning','monitoring']:
   data=copy.deepcopy(self.data);del data[key]
   with self.assertRaises((KeyError,AssertionError)):validate(data)
 def test_invalid_gateway(self):
  self.data['network']['gateway']='203.0.113.1'
  with self.assertRaises(AssertionError):validate(self.data)
 def test_no_credentials_or_wrong_runtime(self):
  self.data['provisioning']['token']='must-not-be-accepted'
  with self.assertRaises(AssertionError):validate(self.data)
  del self.data['provisioning']['token'];self.data['provisioning']['applications'][0]['runtime']='docker'
  with self.assertRaises(AssertionError):validate(self.data)
 def test_undeployed_notes(self):
  text='\n'.join(pending_notes(self.data,'example-native')['sections']);self.assertIn('PENDING VERIFICATION',text)
  for name in ['Purpose','Environment','Network','Applications','Dependencies','Monitoring','Infrastructure as Code','Documentation','Known Issues']:self.assertIn('**'+name+'**',text)
  doc=inventory_document(self.data,'example-native');self.assertIn('no despliegue',doc);self.assertIn('Rollback',doc)
 def test_native_and_docker_artifacts(self):
  for docker in [False,True]:
   self.data['monitoring']['docker']=docker
   with tempfile.TemporaryDirectory() as tmp:
    path=Path(tmp);render_monitoring(self.data,path,ROOT)
    self.assertEqual((path/'cadvisor.yml').exists(),docker)
    script=(path/'node-cgroup.sh').read_text();self.assertIn('ct_id=\\"9991\\"',script);self.assertNotIn('ct_id=\\"624\\"',script)
    self.assertIn('--no-collector.cpu',(path/'node-exporter.service').read_text())
    nodes=json.loads((path/'node-exporter.json').read_text());self.assertNotIn('cpu_contract',nodes[0]['labels'])
    self.assertIn('PREPARED_NOT_DEPLOYED',(path/'activation.json').read_text())
    subprocess.run(['sh','-n',str(path/'node-cgroup.sh')],check=True)
 def test_native_promql_semantics(self):
  dashboard=json.loads((ROOT/'services/infra-grafana/config/provisioning/fleet-assets/proxmox-lxc-fleet.json').read_text());table=next(x for x in dashboard['panels'] if x['title'].startswith('LXC health'));expr={x['refId']:x['expr'].replace('${lxc:regex}','.*').replace('${service:regex}','.*') for x in table['targets']}
  series={'up{job="node_exporter",service="native",vmid="9991"}':'1+0x4','lxc:cadvisor:required{service="native",ct_id="9991"}':'0+0x4'}
  tests=[{'name':'native-no-docker-no-fake-cadvisor','interval':'30s','input_series':[{'series':k,'values':v} for k,v in series.items()],'promql_expr_test':[{'expr':expr['C'],'eval_time':'2m','exp_samples':[{'labels':'{ct_id="9991"}','value':-2}]}]}]
  rule=yaml.safe_load((ROOT/'services/infra-prom/config/rules/infra-containers.yml').read_text());query=next(x['expr'] for g in rule['groups'] for x in g['rules'] if x.get('alert')=='LxcDockerMetricsMissing')
  tests[0]['input_series'].append({'series':'lxc:cpu_inventory:expected{service="native",ct_id="9991"}','values':'1+0x4'})
  full=copy.deepcopy(tests[0]);full['name']='native-full-coverage-no-cadvisor-still-healthy'
  metrics={'lxc:cpu_usage:percent{service="native",ct_id="9991"}':'25+0x4','node_memory_MemAvailable_bytes{job="node_exporter",service="native"}':'50+0x4','node_memory_MemTotal_bytes{job="node_exporter",service="native"}':'100+0x4','node_filesystem_avail_bytes{job="node_exporter",service="native",mountpoint="/",fstype="ext4"}':'50+0x4','node_filesystem_size_bytes{job="node_exporter",service="native",mountpoint="/",fstype="ext4"}':'100+0x4','up{job="pve_uptime",instance="pve"}':'1+0x4','pve_up{job="pve_uptime",instance="pve",ct_id="9991",id="lxc/9991"}':'1+0x4','pve_uptime_seconds{job="pve_uptime",instance="pve",ct_id="9991",id="lxc/9991"}':'500+30x4','up{job="blackbox",service="native",instance="http://example",module="health"}':'1+0x4','probe_success{job="blackbox",service="native",instance="http://example",module="health"}':'1+0x4'}
  full['input_series'] += [{'series':k,'values':v} for k,v in metrics.items()]
  full['promql_expr_test']=[{'expr':expr[k],'eval_time':'2m','exp_samples':[{'labels':'{ct_id="9991"}','value':v}]} for k,v in [('K',1),('I',0)]];tests.append(full)
  tests[0]['promql_expr_test'].append({'expr':query,'eval_time':'2m','exp_samples':[]})
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'tests.yml';path.write_text(yaml.safe_dump({'rule_files':[],'evaluation_interval':'30s','tests':tests}));tool=Path.home()/'.local/share/mailerblend-recovery/phase5/d050/promtool';r=subprocess.run([str(tool),'test','rules',str(path)],capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stdout+r.stderr)
if __name__=='__main__':unittest.main()

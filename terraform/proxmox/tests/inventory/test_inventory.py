import copy,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def load(filename):
 s=importlib.util.spec_from_file_location(filename,ROOT/'scripts'/filename);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
g=load('generate-lxc-inventory.py');p=load('validate-lxc-notes-plan.py')
class InventoryTests(unittest.TestCase):
 def test_exact_17_and_generated_artifacts(self):
  notes,md=g.build();self.assertEqual(len(notes),17);self.assertIn('CT 61211',md)
  self.assertEqual(notes,json.loads((ROOT/'inventory/generated/lxc-notes.json').read_text()))
 def test_ct614_notes_equal_the_service_source(self):
  notes,_=g.build();v=notes['infra-nucleoedge']
  text='# '+v['title']+'\n\n'+'\n\n'.join(v['sections'])+'\n'
  self.assertEqual(text,(ROOT/'services/infra-nucleoedge/NOTES.md').read_text())
 def test_service_scope_rejects_other_resource_notes(self):
  self.assertFalse(p.review(self.plan(),{'infra-nucleoedge':'new'})['apply_permitted'])
 def test_ct614_individual_inventory_is_primary(self):
  _,markdown=g.build()
  section=markdown.split('## CT 614 — infra-nucleoedge',1)[1].split('\n## ',1)[0]
  self.assertIn('614-LXC-INVENTORY.md',section)
  self.assertNotIn('## Applications',section)
 def test_ct615_notes_equal_source(self):
  notes,_=g.build();v=notes['infra-mailerblend-edge']
  self.assertEqual('# '+v['title']+'\n\n'+'\n\n'.join(v['sections'])+'\n',(ROOT/'services/infra-mailerblend-edge/NOTES.md').read_text())
 def test_ct615_individual_inventory_is_primary(self):
  _,markdown=g.build();section=markdown.split('## CT 615 — infra-mailerblend-edge',1)[1].split('\n## ',1)[0]
  self.assertIn('615-LXC-INVENTORY.md',section);self.assertNotIn('## Applications',section)
 def test_yaml_duplicate_is_rejected(self):
  with self.assertRaises(ValueError):g.yaml.load('a: 1\na: 2',Loader=g.UniqueLoader)
 def test_domain_requires_upstream_match(self):
  r={'routes':[{'server_names':['svc01.example'],'proxy_upstreams':['http://192.168.1.118:8080']}]}
  self.assertEqual(g.domains_for('192.168.1.112',r),[])
  self.assertEqual(g.domains_for('192.168.1.118',r),['svc01.example'])
 def test_upstream_groups_resolved_exactly(self):
  r={'routes':[{'server_names':['edge.example'],'proxy_upstreams':['http://sgtm_serving']}],'upstream_groups':[{'name':'sgtm_serving','servers':['192.168.1.115:18091']}]}
  self.assertEqual(g.domains_for('192.168.1.115',r),['edge.example']);self.assertEqual(g.domains_for('192.168.1.11',r),[])
 def test_secret_assignments_are_rejected(self):
  for value in [{'password':'example'},{'CONTAINER_CONFIG':'opaque'},'https://user:pass@host/']:
   with self.assertRaises(AssertionError):g.assert_public(value)
 def plan(self):
  return {'resource_changes':[{'address':'proxmox_virtual_environment_container.svc["x"]','type':'proxmox_virtual_environment_container','name':'svc','index':'x','change':{'actions':['update'],'before':{'description':'old','cpu':[{'cores':2}]},'after':{'description':'new','cpu':[{'cores':2}]},'after_unknown':{}}}]}
 def test_only_expected_notes_may_apply(self):self.assertTrue(p.review(self.plan(),{'x':'new'})['apply_permitted'])
 def test_resource_changes_block_apply(self):
  x=self.plan();x['resource_changes'][0]['change']['after']['cpu']=[{'cores':3}]
  self.assertFalse(p.review(x,{'x':'new'})['apply_permitted'])
 def test_recreation_and_unknowns_block_apply(self):
  for actions in [['create'],['delete'],['delete','create']]:
   x=self.plan();x['resource_changes'][0]['change']['actions']=actions;self.assertFalse(p.review(x,{'x':'new'})['apply_permitted'])
  x=self.plan();x['resource_changes'][0]['change']['after_unknown']={'memory':True};self.assertFalse(p.review(x,{'x':'new'})['apply_permitted'])
 def test_unexpected_description_and_resource_block_apply(self):
  self.assertFalse(p.review(self.plan(),{'x':'different'})['apply_permitted'])
  x=self.plan();x['resource_changes'][0]['type']='other';self.assertFalse(p.review(x,{'x':'new'})['apply_permitted'])
if __name__=='__main__':unittest.main()

import ast,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Latency(unittest.TestCase):
 def test_ttft_counts_first_visible_stream_delta_not_final(self):
  tree=ast.parse((ROOT/'scripts/ia-chat/latency/ui-probe.py').read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='first_token_time');scope={};exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'ui-probe.py','exec'),scope)
  events=[{'elapsed_s':.1,'event':{'type':'response:completion','data':{'choices':[{'delta':{'role':'assistant','content':None}}]}}},{'elapsed_s':.8,'event':{'type':'response:completion','data':{'type':'response.output_text.delta','delta':'Hola'}}},{'elapsed_s':3,'event':{'type':'chat:completion','data':{'content':'Hola','done':True}}}]
  self.assertEqual(scope['first_token_time'](events),.8)
  self.assertIsNone(scope['first_token_time'](events[:1]))
 def test_gemma_template_keeps_generation_prefix_in_history(self):
  import jinja2
  source=(ROOT/'services/infra-llm/config/gemma-cache.jinja').read_text();env=jinja2.Environment(extensions=['jinja2.ext.loopcontrols']);env.globals['raise_exception']=lambda s:(_ for _ in ()).throw(ValueError(s));template=env.from_string(source)
  messages=[{'role':'system','content':'Respuesta corta.'},{'role':'user','content':'Hola'}]
  first=template.render(messages=messages,add_generation_prompt=True,enable_thinking=False,bos_token='',tools=None)
  second=template.render(messages=messages+[{'role':'assistant','content':'Hola.'},{'role':'user','content':'Sigue'}],add_generation_prompt=True,enable_thinking=False,bos_token='',tools=None)
  self.assertTrue(second.startswith(first+'Hola.<turn|>\n'))
  self.assertEqual(first.count('<|channel>thought'),1)

 def test_qwen_preserve_thinking_retains_empty_prefix_without_first_turn_change(self):
  import jinja2
  source=(ROOT/'services/ia-local/upstream/qwen-chat-template.jinja').read_text();template=jinja2.Environment().from_string(source)
  messages=[{'role':'system','content':'Respuesta corta.'},{'role':'user','content':'Hola'}]
  plain=template.render(messages=messages,add_generation_prompt=True,enable_thinking=False)
  first=template.render(messages=messages,add_generation_prompt=True,enable_thinking=False,preserve_thinking=True)
  self.assertEqual(first,plain)
  second=template.render(messages=messages+[{'role':'assistant','content':'Hola.'},{'role':'user','content':'Sigue'}],add_generation_prompt=True,enable_thinking=False,preserve_thinking=True)
  self.assertTrue(second.startswith(first+'Hola.<|im_end|>\n'))

 def test_observer_tolerates_removed_oneshot_cgroup(self):
  import tempfile,pathlib,os
  from unittest.mock import patch
  tree=ast.parse((ROOT/'scripts/ia-chat/latency/benchmark-matrix.py').read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='cgroup_pids');scope={'os':os,'pathlib':pathlib};exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'benchmark-matrix.py','exec'),scope)
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp);(root/'cgroup.procs').write_text('123\n456\n')
   def walk(path,onerror):
    onerror(FileNotFoundError('lxc-cpu.service disappeared'))
    yield str(root),[],['cgroup.procs']
    yield str(root/'vanished'),[],['cgroup.procs']
   with patch.object(os,'walk',side_effect=walk):self.assertEqual(scope['cgroup_pids'](root),{'123','456'})

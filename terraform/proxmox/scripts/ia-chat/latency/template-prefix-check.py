#!/usr/bin/env python3
"""PVE: verifica prefijo del template Gemma sin generar texto ni usar datos personales."""
import sys,importlib.util,json,pathlib
sys.argv=['validate-api.py','library'];sp=importlib.util.spec_from_file_location('a','/root/ia-local/validate-api.py');a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
messages=[{'role':'system','content':'Responde en español salvo que se te pida otro idioma. Sé directo y conciso.'},{'role':'user','content':'Hola, ¿qué tal?'}];answer='¡Hola! Todo bien, ¿y tú? ¿En qué puedo ayudarte?'
def render(ms,thinking=False):
 code,d=a.call('/apply-template',{'model':'gemma-4-26b','messages':ms,'chat_template_kwargs':{'enable_thinking':thinking}});assert code==200;return d['prompt']
one=render(messages);expected='<|turn>system\nResponde en español salvo que se te pida otro idioma. Sé directo y conciso.<turn|>\n<|turn>user\nHola, ¿qué tal?<turn|>\n<|turn>model\n<|channel>thought\n<channel|>'
assert one==expected,'First-turn template changed'
two=render(messages+[{'role':'assistant','content':answer},{'role':'user','content':'¿Y cómo puedes ayudarme?'}]);assert two.startswith(one+answer+'<turn|>\n'),'History does not retain generated prefix'
on=render(messages,True);assert not on.endswith('<|channel>thought\n<channel|>'),'Thinking-on changed to off'
d={'result':'PASS','first_turn_identical_to_upstream':True,'history_prefix_exact':True,'thinking_control_preserved':True};path=pathlib.Path('/root/ia-local/latency/template-prefix-check.json');path.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))

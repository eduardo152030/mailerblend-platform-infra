#!/usr/bin/env python3
"""Verify alert input selectors against the live Prometheus AST and series.
Empty alert results are expected; missing input metrics are not silently accepted.
"""
import importlib.util,json
from pathlib import Path
import yaml
s=importlib.util.spec_from_file_location('p5',Path(__file__).with_name('phase5-alerting.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
selectors={};checks=[]
def walk(node):
 if isinstance(node,dict):
  if node.get('type') in ['vectorSelector','matrixSelector']:
   matchers=node['matchers'];selector='{'+','.join(x['name']+x['type']+json.dumps(x['value']) for x in matchers)+'}'
   selectors[selector]=None
  for v in node.values():walk(v)
 elif isinstance(node,list):
  for v in node:walk(v)
for path in (m.ROOT/'services/infra-prom/config/rules').glob('*.yml'):
 for g in yaml.safe_load(path.read_text())['groups']:
  for r in g['rules']:
   if 'alert' in r:
    ast=m.api('/api/v1/parse_query?'+m.urllib.parse.urlencode({'query':r['expr']}));walk(ast);checks.append(r['alert'])
for selector in selectors:selectors[selector]=len(m.query(selector))
# New expected inventory will be created locally and validated with fixtures.
allowed=['{__name__="app:container:expected"}']
missing=[s for s,n in selectors.items() if n==0 and s not in allowed]
result={'alert_rules_checked':len(checks),'input_selector_counts':selectors,'candidate_only_inputs':allowed,'unexpected_missing':missing}
m.save(m.PRIVATE/'series-audit.json',result);print(json.dumps(result,ensure_ascii=False));assert not missing

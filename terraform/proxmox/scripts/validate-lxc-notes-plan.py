#!/usr/bin/env python3
"""Fail closed unless a saved full Terraform plan changes only the 17 LXC descriptions.
Input JSON is private (may contain credentials). Output contains names/field names only.
"""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def descriptions():
 d=json.loads((ROOT/'inventory/generated/lxc-notes.json').read_text())
 return {k:'# '+v['title']+'\n\n'+'\n\n'.join(v['sections'])+'\n' for k,v in d.items()}
def review(plan,expected):
 issues=[];changes=[]
 for r in plan.get('resource_changes',[]):
  c=r['change'];actions=c['actions']
  if actions==['no-op']:continue
  if r.get('mode')=='data' and actions==['read']:continue
  before,after=c.get('before') or {},c.get('after') or {}
  fields=sorted(k for k in set(before)|set(after) if before.get(k)!=after.get(k))
  key=r.get('index');entry={'address':r['address'],'actions':actions,'fields':fields};changes.append(entry)
  if r.get('type')!='proxmox_virtual_environment_container' or r.get('name')!='svc' or key not in expected:
   issues.append({'address':r['address'],'reason':'Outside authorized LXC notes scope'});continue
  if actions!=['update'] or fields!=['description'] or c.get('replace_paths'):
   issues.append({'address':r['address'],'reason':'Change is not description-only','fields':fields});continue
  if after['description']!=expected[key]:issues.append({'address':r['address'],'reason':'Description differs from generated inventory'})
  if any(v for k,v in c.get('after_unknown',{}).items()):issues.append({'address':r['address'],'reason':'Unknown planned attributes'})
 return {'result':'BLOCKED' if issues else 'PASS','changes':changes,'issues':issues,'apply_permitted':not issues}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('plan_json',type=Path);ap.add_argument('--report',type=Path,required=True);ap.add_argument('--service',help='Restrict authorization to one inventory service');a=ap.parse_args()
 expected=descriptions()
 if a.service:
  assert a.service in expected, 'Unknown service'
  expected={a.service:expected[a.service]}
 result=review(json.loads(a.plan_json.read_text()),expected);a.report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(1 if result['issues'] else 0)
if __name__=='__main__':main()

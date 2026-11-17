#!/usr/bin/env python3
"""Reconciliar exclusivamente disco610 con inventario YAML, mediante SSH estricto."""
import argparse,json,pathlib,shlex,subprocess,yaml
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--label',required=True);a=p.parse_args();assert a.label.replace('-','').isalnum()
d=yaml.safe_load((ROOT/'inventory/services/infra-prom.yml').read_text());assert d['service']['vmid']==610
args=['python3','-','--target',str(d['resources']['disk_gb'])]+(['--execute'] if a.execute else [])
r=subprocess.run(['ssh','-o','UserKnownHostsFile='+str(pathlib.Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve',shlex.join(args)],input=(HERE/'remote.py').read_bytes(),capture_output=True,timeout=3000)
if r.returncode:
 print('STOP: reconciliación fallida; salida sensible omitida. Código:',r.returncode)
 print(r.stderr.decode()[-1600:]);raise SystemExit(1)
result=json.loads(r.stdout);(ROOT/'docs/roadmap/evidence/ct610-disk-20261114'/f'{a.label}.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

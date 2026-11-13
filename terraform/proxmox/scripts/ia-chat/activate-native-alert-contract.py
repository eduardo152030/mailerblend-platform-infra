#!/usr/bin/env python3
"""Activa solo la excepción declarativa sinDocker; mantiene alertas de CT legacy."""
import importlib.util,json,yaml,hashlib,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];s=importlib.util.spec_from_file_location('stage',ROOT/'scripts/phase6-stage-a.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
p=Path.home()/'.local/share/mailerblend-recovery/ia-chat/native-alert';p.mkdir(parents=True,exist_ok=True,mode=0o700)
file='/opt/infra-prom/config/rules/infra-containers.yml';body=t.remote(610,['cat',file]);runtime=yaml.safe_load(body);desired=yaml.safe_load((ROOT/'services/infra-prom/config/rules/infra-containers.yml').read_text())
old=next(r for g in runtime['groups'] for r in g['rules'] if r.get('alert')=='LxcDockerMetricsMissing');new=next(r for g in desired['groups'] for r in g['rules'] if r.get('alert')=='LxcDockerMetricsMissing')
assert new['expr']=='(lxc:cpu_inventory:expected unless on(service) container_last_seen{job="cadvisor",name!=""}) unless on(service) (lxc:cadvisor:required == 0)'
was=old['expr'];old['expr']=new['expr'];candidate=yaml.safe_dump(runtime,sort_keys=False).encode();changed=was!=new['expr']
if changed:
 backup=p/'infra-containers.before.yml'
 if backup.exists():assert backup.read_bytes()==body,'Runtime drift'
 else:backup.write_bytes(body);backup.chmod(0o600)
 t.remote(610,['mkdir','-p','/opt/infra-prom/config/.runtime/ia-chat']);t.remote(610,['tee','/opt/infra-prom/config/.runtime/ia-chat/infra-containers.before.yml'],body)
 target='/opt/infra-prom/config/.runtime/ia-chat/infra-containers.candidate.yml';t.remote(610,['tee',target],candidate)
 local=p/'infra-containers.candidate.yml';local.write_bytes(candidate)
 subprocess.run([str(Path.home()/'.local/share/mailerblend-recovery/phase5/d050/promtool'),'check','rules',str(local)],check=True)
 try:t.remote(610,['tee',file],candidate);t.reload(610)
 except Exception:t.remote(610,['tee',file],body);t.reload(610);raise
out={'changed':changed,'restarts':0,'reloads':int(changed),'only_alert':'LxcDockerMetricsMissing','old_expr':was,'new_expr':new['expr'],'legacy_default_docker_required':True};(ROOT/'docs/roadmap/evidence/ia-chat-2026-11-13/native-alert-contract.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))

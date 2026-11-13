#!/usr/bin/env python3
"""Ejecutar enPVE; secretos solo630/631, nunca stdout ni argumentos."""
import subprocess,json
code="""import pathlib,secrets,os
p=pathlib.Path('/etc/llama');p.mkdir(mode=0o700,exist_ok=True)
k=p/'api.key'
if not k.exists():k.write_text(secrets.token_urlsafe(48)+'\\n')
k.chmod(0o600)
print(k.read_text().strip())
"""
key=subprocess.run(['pct','exec','630','--','python3','-c',code],text=True,capture_output=True,check=True).stdout.strip()
code2="""import pathlib,secrets,sys
p=pathlib.Path('/opt/ia-chat/secrets.env')
if not p.exists():p.write_text('OPENAI_API_KEY='+sys.stdin.read().strip()+'\\nWEBUI_SECRET_KEY='+secrets.token_urlsafe(64)+'\\n')
p.chmod(0o600)
t=pathlib.Path('/root/searxng-settings.template').read_text();d=pathlib.Path('/opt/ia-chat/searxng/settings.yml')
if not d.exists():d.write_text(t.replace('REPLACE_WITH_LOCAL_SECRET',secrets.token_hex(32)))
d.chmod(0o600)
"""
subprocess.run(['pct','exec','631','--','python3','-c',code2],input=key,text=True,check=True)
print('Secretos preparados: CT630 /etc/llama/api.key; CT631 /opt/ia-chat/secrets.env y /opt/ia-chat/searxng/settings.yml; modos600')

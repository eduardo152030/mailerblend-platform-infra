#!/usr/bin/env python3
"""D083: regla temporal basada en CPU real; ejecutar en CT610: on/off/cleanup.

Recorre exporter -> Prometheus -> regla -> Alertmanager -> Telegram.
No acredita recepción humana. No genera carga ni POST directo a Alertmanager.
"""
import argparse
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('action', choices=['on', 'off', 'cleanup'])
args = parser.parse_args()
path = Path('/opt/infra-prom/config/rules/d083-recovery-test.yml')
previous = path.read_bytes() if path.exists() else None
if path.exists():
    existing = json.loads(path.read_text())
    assert existing['groups'][0]['name'] == 'd083_recovery_verification'
if args.action == 'cleanup':
    if path.exists():
        import urllib.request, urllib.parse
        query = urllib.parse.urlencode({'query': 'ALERTS{alertname="MonitoringRecoveryVerification",alertstate="firing"}'})
        result = json.load(urllib.request.urlopen('http://127.0.0.1:9090/api/v1/query?' + query))
        assert not result['data']['result'], 'Resolver antes de retirar la regla'
        path.unlink()
else:
    body = {'groups': [{'name': 'd083_recovery_verification', 'rules': [{
        'alert': 'MonitoringRecoveryVerification',
        'expr': 'lxc:cpu_usage:percent{ct_id="610"} ' + ('>= 0' if args.action == 'on' else '< 0'),
        'for': '30s',
        'labels': {'severity': 'info', 'service': 'infra-prom', 'recovery_test': 'd083'},
        'annotations': {'summary': 'PRUEBA de recuperación tras reinicio; sin incidencia real',
                        'description': 'Verificación CPU LXC → Prometheus → reglas → Alertmanager → Telegram.',
                        'ct_id': '610', 'value': '{{ printf "%.2f" $value }}%',
                        'dashboard_url': 'http://192.168.1.111:3010/d/proxmox-lxc-fleet'}
    }]}]}
    path.write_text(json.dumps(body, ensure_ascii=False, indent=2) + '\n')
result = subprocess.run(['docker', 'exec', 'prometheus', 'promtool', 'check', 'config',
                         '/etc/prometheus/prometheus.yml'], capture_output=True)
if result.returncode:
    if previous is not None:
        path.write_bytes(previous)
    elif path.exists():
        path.unlink()
    raise RuntimeError('Configuración inválida; regla anterior restaurada, sin recarga')
subprocess.run(['docker', 'kill', '--signal=HUP', 'prometheus'], check=True, capture_output=True)
print('PASS regla temporal ' + args.action + '; promtool válido, SIGHUP sin reinicio')

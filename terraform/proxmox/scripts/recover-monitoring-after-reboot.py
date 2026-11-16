#!/usr/bin/env python3
"""D083: recuperar solo Prometheus/Alertmanager existentes, sin recrear ni pull.

Ejecutar en CT610 (python3). Conserva Compose previo en /root y comprueba su
restaurabilidad. Rollback de política: restaurar el Compose del backup y aplicar
docker update --restart=unless-stopped prometheus alertmanager; no parar servicios.
No modifica targets, reglas, secretos, imágenes ni volúmenes.
"""
import hashlib
import argparse
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blackbox', action='store_true', help='Solo Blackbox en CT616')
    args = parser.parse_args()
    base = Path('/opt/infra-blackbox' if args.blackbox else '/opt/infra-prom')
    compose = base / 'docker-compose.yml'
    names = ['infra-blackbox'] if args.blackbox else ['prometheus', 'alertmanager']
    before = json.loads(run('docker', 'inspect', *names))
    for c in before:
        assert c['Config']['Labels']['com.docker.compose.project.working_dir'] == str(base)
        assert args.blackbox or any(m['Type'] == 'volume' for m in c['Mounts'])
    original = compose.read_bytes()
    backup = Path('/root/monitoring-recovery-d083')
    backup.mkdir(mode=0o700, exist_ok=True)
    saved = backup / 'docker-compose.before.yml'
    if not saved.exists():
        saved.write_bytes(original)
        saved.chmod(0o600)
        assert saved.read_bytes() == original
        (backup / 'baseline.json').write_text(json.dumps([
            {'name': c['Name'], 'id': c['Id'], 'image': c['Image'],
             'running': c['State']['Running'], 'state': c['State'],
             'policy': c['HostConfig']['RestartPolicy'], 'mounts': c['Mounts']}
            for c in before], indent=2))
    text = original.decode()
    # El fichero desplegado puede diferir del candidato Git: preservar todo salvo
    # las dos políticas de reinicio. No desplegar versiones locales de imágenes.
    assert text.count('restart: unless-stopped') + text.count('restart: always') == len(names)
    candidate = text.replace('restart: unless-stopped', 'restart: always').encode()
    if candidate != original:
        compose.write_bytes(candidate)
        p = subprocess.run(['docker', 'compose', '-f', str(compose), 'config', '--quiet'],
                           capture_output=True)
        if p.returncode:
            compose.write_bytes(original)
            raise RuntimeError('Compose inválido; original restaurado, salida privada omitida')
    for c in before:
        name = c['Name'].lstrip('/')
        if c['HostConfig']['RestartPolicy']['Name'] != 'always':
            run('docker', 'update', '--restart=always', name)
        if not c['State']['Running']:
            run('docker', 'start', name)
    after = json.loads(run('docker', 'inspect', *names))
    for a, b in zip(before, after):
        assert a['Id'] == b['Id'] and a['Image'] == b['Image']
        mounts = lambda c: sorted(c['Mounts'], key=lambda m: m['Destination'])
        assert mounts(a) == mounts(b) and b['State']['Running']
        if a['State']['Running']:
            assert a['State']['StartedAt'] == b['State']['StartedAt']
    print(json.dumps({'observed_at_utc': datetime.now(timezone.utc).isoformat(),
        'compose_sha256': hashlib.sha256(candidate).hexdigest(),
        'backup_verified': True, 'same_containers_images_mounts': True,
        'services': [{'name': c['Name'], 'started': c['State']['StartedAt'],
                      'restart': c['HostConfig']['RestartPolicy']['Name']}
                     for c in after]}))


if __name__ == '__main__':
    main()

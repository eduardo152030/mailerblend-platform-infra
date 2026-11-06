#!/usr/bin/env python3
"""Fail closed before recreating a legacy Budibase stack with duplicated single images."""
from pathlib import Path
import sys
import yaml

DEFAULT = Path(__file__).resolve().parents[1] / 'services/infra-composable-crm/compose/budibase/docker-compose.yml'


def validate(config):
    services = config.get('services', {})
    errors = []
    for name, service in services.items():
        image = service.get('image', '').split('@', 1)[0].split(':', 1)[0]
        if image != 'budibase/budibase':
            continue
        if name == 'budibase-worker':
            errors.append('budibase-worker uses the all-in-one image: a second complete stack is not a dedicated worker.')
        mounts = service.get('volumes', [])
        has_data = any((isinstance(m, str) and m.split(':')[1:2] == ['/data']) or
                       (isinstance(m, dict) and m.get('target') == '/data') for m in mounts)
        if not has_data:
            errors.append(f'{name}: explicitly preserve the existing /data volume before any recreation.')
    if errors:
        raise ValueError('Deployment blocked: ' + ' '.join(errors) +
                         ' Back up both existing data volumes and approve a compatible topology migration first.')


if __name__ == '__main__':
    try:
        validate(yaml.safe_load(Path(sys.argv[1] if len(sys.argv) > 1 else DEFAULT).read_text()))
    except yaml.YAMLError:
        print('Invalid Budibase YAML configuration; content omitted.', file=sys.stderr)
        sys.exit(1)
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    print('Budibase topology preflight passed.')

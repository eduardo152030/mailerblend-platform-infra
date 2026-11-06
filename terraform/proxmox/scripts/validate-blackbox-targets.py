#!/usr/bin/env python3
"""Validate the repository-owned Blackbox catalog without probing any endpoints."""
import json
import ipaddress
from pathlib import Path
from urllib.parse import urlsplit

CATALOG = Path(__file__).resolve().parents[1] / 'services/infra-prom/config/targets/blackbox.json'


def validate(groups):
    ids, requests = set(), set()
    for group in groups:
        labels = group['labels']
        required = {'job', 'service', 'module', 'probe_type', 'probe_id', 'alert_target', 'scope', 'source'}
        if not required <= labels.keys() or any(not labels[k] for k in required):
            raise ValueError('Missing required probe identity labels')
        if labels['job'] != 'blackbox':
            raise ValueError('Unexpected job')
        if labels['probe_id'] in ids:
            raise ValueError('Duplicate probe_id')
        ids.add(labels['probe_id'])
        if len(group['targets']) != 1:
            raise ValueError('Each catalog entry must contain one explicit request')
        if labels['module'] == 'tcp_connect':
            address, port = group['targets'][0].rsplit(':', 1)
            ipaddress.IPv4Address(address)
            if not 1 <= int(port) <= 65535 or labels['probe_type'] != 'tcp':
                raise ValueError('Invalid TCP probe')
            if labels['alert_target'] != 'tcp://' + group['targets'][0]:
                raise ValueError('TCP alert endpoint does not match')
            key = ('tcp_connect', address, int(port))
            if key in requests:
                raise ValueError('Duplicate TCP request')
            requests.add(key)
            continue
        if labels['module'] not in ('http_2xx', 'http_2xx_strict', 'http_collect_200'):
            raise ValueError('Unsupported HTTP probe module')
        url = urlsplit(group['targets'][0])
        if url.scheme not in ('http', 'https') or not url.hostname or url.username or url.fragment:
            raise ValueError('Invalid probe URL')
        if 'PLACEHOLDER' in group['targets'][0]:
            raise ValueError('Placeholder endpoint')
        key = (labels['module'], url.scheme.lower(), url.netloc.lower(), url.path or '/', url.query)
        if key in requests:
            raise ValueError('Duplicate request with the same module')
        requests.add(key)
        endpoint = f'{url.scheme}://{url.netloc}{url.path or "/"}'
        if labels['alert_target'] != endpoint:
            raise ValueError('Logical alert endpoint does not match the request')
        if url.scheme == 'https' and labels.get('tls_target') != f'https://{url.netloc}':
            raise ValueError('Missing or incorrect TLS identity')
    return len(ids)


if __name__ == '__main__':
    groups = json.loads(CATALOG.read_text())
    journal = CATALOG.with_name('blackbox-journal.json')
    if journal.exists(): groups += json.loads(journal.read_text())
    count = validate(groups)
    print(f'Blackbox catalog valid: {count} requests; no duplicate request/module pairs.')

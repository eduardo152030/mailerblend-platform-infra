#!/usr/bin/env python3
"""Generate inventory catalogs locally; preserves the accepted Blackbox base catalog."""
import argparse
import ipaddress
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_services(inventory_dir=None):
    services = []
    seen = {"name": set(), "ip": set(), "vmid": set()}
    for path in sorted(Path(inventory_dir or ROOT / 'inventory/services').glob('*.yml')):
        svc = (yaml.safe_load(path.read_text()) or {}).get('service', {})
        if not all(k in svc for k in ['name', 'ip', 'vmid']):
            raise ValueError(f'Missing service identity in {path.name}')
        address = ipaddress.ip_interface(svc['ip']).ip
        if address.version != 4:
            raise ValueError('IPv4 service addresses required by current deployment')
        row = {'name': svc['name'], 'ip': str(address), 'vmid': str(svc['vmid'])}
        for key, value in row.items():
            if value in seen[key]:
                raise ValueError(f'Duplicate service {key}: {value}')
            seen[key].add(value)
        services.append(row)
    if not services:
        raise ValueError('Empty inventory')
    return services


def validated_cpu_cts(state=None,root=ROOT):
    if state is None:state=yaml.safe_load((root/'services/common/exporter-migration.yml').read_text())
    assert state['schema']==1
    ids=set()
    for ident,filename in state['cpu_contract_verified'].items():
        ct=int(ident);r=json.loads((root/filename).read_text())
        assert r['ct']==ct and (r.get('result')=='PASS' or r.get('pilot_technical_result')=='PASS'), 'Unverified exporter evidence'
        assert r.get('cpu_source')=='cgroup_v2_textfile' or (ct==624 and str(r.get('cpu_source')).startswith('cgroup_v2') and r.get('native_cpu_time_series_disabled') is True), 'Unknown CPU source'
        ids.add(ct)
    assert {int(x) for x in state['exporters_validated']}<=ids
    assert set(state['prometheus_integrated'])<=ids
    assert set(state['telegram_chain_verified'])<=set(state['prometheus_integrated'])
    return ids


def groups_for(services, port, job, only_services=None):
    scope = 'application' if job == 'grafana' else 'lxc'
    cpu_cts=validated_cpu_cts() if job=='node_exporter' else set()
    return [{'targets': [f"{s['ip']}:{port}"], 'labels': {
        'job': job, 'source': 'inventory', 'service': s['name'],
        'vmid': s['vmid'], 'collector_scope': scope,
        **({'cpu_contract': 'lxc_cgroup_v1'} if job == 'node_exporter' and int(s['vmid']) in cpu_cts else {}),
    }} for s in services if only_services is None or s['name'] in only_services]


def journal_groups(services):
    contracts = yaml.safe_load((ROOT / 'services/infra-prom/config/journal-probes.yml').read_text())
    by_name = {s['name']: s for s in services}
    rows = []
    for name, contract in sorted(contracts.items()):
        if name not in by_name:
            raise ValueError('Missing Journal service: ' + name)
        svc = by_name[name]
        address = f"{svc['ip']}:{contract['port']}"
        target = address if contract['module'] == 'tcp_connect' else 'http://' + address + contract['path']
        endpoint = 'tcp://' + address if contract['module'] == 'tcp_connect' else target
        rows.append({'targets': [target], 'labels': {
            'job': 'blackbox', 'service': name, 'vmid': svc['vmid'],
            'module': contract['module'], 'probe_type': contract['probe_type'],
            'scope': 'internal', 'source': 'inventory',
            'probe_id': name + '-availability', 'alert_target': endpoint,
        }})
    return rows


def generate(inventory_dir, output_dir):
    # Validate every identity before writing any catalog.
    services = load_services(inventory_dir)
    outputs = {
        'node-exporter.json': groups_for(services, 9100, 'node_exporter'),
        'cadvisor.json': groups_for(services, 8085, 'cadvisor'),
        'grafana.json': groups_for(services, 3010, 'grafana', ['infra-grafana']),
        'blackbox-journal.json': journal_groups(services),
    }
    if len(outputs['grafana.json']) != 1:
        raise ValueError('Exactly one infra-grafana service is required')
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in outputs.items():
        (output_dir / name).write_text(json.dumps(rows, indent=2) + '\n')
    return {name: len(rows) for name, rows in outputs.items()}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inventory-dir', type=Path, default=ROOT / 'inventory/services')
    p.add_argument('--output-dir', type=Path, default=ROOT / 'services/infra-prom/config/targets')
    args = p.parse_args()
    try:
        print(json.dumps(generate(args.inventory_dir, args.output_dir)))
    except (ValueError, OSError, yaml.YAMLError) as exc:
        p.exit(1, str(exc) + '\n')

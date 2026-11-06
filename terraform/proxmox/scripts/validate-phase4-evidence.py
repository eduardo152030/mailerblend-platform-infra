#!/usr/bin/env python3
"""Fail closed on measured coverage gaps. Read-only; a passing check is not full phase acceptance."""
import argparse
import json
import math
from pathlib import Path
import urllib.parse
import urllib.request
import yaml

ROOT = Path(__file__).resolve().parents[1]


def assess(runtime, monitoring, expected):
    issues = []
    observed = {s['service']: s for s in runtime['services']}
    if len(observed) != len(runtime['services']) or set(observed) != set(expected):
        issues.append('Runtime inventory differs from the expected service set')
    targets = monitoring['targets']
    for name in expected:
        s = observed.get(name, {})
        rt = s.get('runtime', {})
        limits = s.get('proxmox', {})
        for job in ['node_exporter', 'cadvisor']:
            matches = [t for t in targets if t.get('service') == name and t.get('job') == job]
            if len(matches) != 1 or matches[0].get('health') != 'up':
                issues.append(name + ': expected exactly one healthy ' + job + ' scrape')
        node = rt.get('node_endpoint', {})
        if node.get('http') != 200:
            issues.append(name + ': Node Exporter not measured/available')
        else:
            if node.get('cpu_count') != int(limits.get('cores') or -1):
                issues.append(name + ': Node CPU count differs from LXC allocation')
            if node.get('memory_total') != int(limits.get('memory') or -1) * 1024 * 1024:
                issues.append(name + ': Node RAM differs from LXC allocation')
        if node.get('cpu_source') != 'cgroup_v2_textfile':
            issues.append(name + ': LXC CPU source unverified; procfs capacity does not prove CPU isolation')
        else:
            if node.get('native_cpu_time_series_count') != 0 or node.get('cpu_collector_success') != 1 or node.get('textfile_scrape_error') != 0:
                issues.append(name + ': incorrect/stale CPU collector mode')
            if node.get('cpu_ct_id') != str(s.get('ct')):
                issues.append(name + ': CPU metric belongs to another CT')
            age = node.get('cpu_collector_age_seconds')
            if not isinstance(age, (int, float)) or not math.isfinite(age) or not -2 <= age <= 15:
                issues.append(name + ': LXC CPU collector is stale')
            for field in ['cpu_capacity_cores', 'cpu_usage_seconds', 'cpu_user_seconds', 'cpu_system_seconds']:
                value = node.get(field)
                if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0 or (field == 'cpu_capacity_cores' and value <= 0):
                    issues.append(name + ': missing/invalid ' + field)
            if node.get('cpu_capacity_cores') != int(limits.get('cores') or -1):
                issues.append(name + ': CPU capacity differs from Proxmox allocation')
        cad = rt.get('cadvisor_endpoint', {})
        if cad.get('http') != 200:
            issues.append(name + ': cAdvisor not measured/available')
        active = {c['name'] for c in rt.get('containers', []) if c['running']}
        if not active:
            issues.append(name + ': no active-container baseline')
        for metric, key in [('RAM', 'memory_container_names'), ('CPU', 'cpu_container_names')]:
            if not active <= set(cad.get(key, [])):
                issues.append(name + ': individual Docker ' + metric + ' identities missing')
    grafana = [t for t in targets if t.get('job') == 'grafana' and t.get('service') == 'infra-grafana']
    if len(grafana) != 1 or grafana[0].get('health') != 'up':
        issues.append('Grafana: metrics scrape missing/unhealthy')
    probes = monitoring.get('journal_probe_success', [])
    for service in ['infra-journal-api', 'infra-journal-db', 'infra-journal-web']:
        found = [r for r in probes if r['metric'].get('service') == service]
        if len(found) != 1 or float(found[0]['value'][1]) != 1:
            issues.append(service + ': expected one successful availability probe')
    return issues


def live_monitoring(base):
    def get(path):
        with urllib.request.urlopen(base.rstrip('/') + path, timeout=15) as r:
            return json.load(r)
    targets = get('/api/v1/targets')['data']['activeTargets']
    query = urllib.parse.urlencode({'query': 'probe_success{job="blackbox",service=~"infra-journal-(api|db|web)"}'})
    return {'targets': [{'job': t['labels'].get('job'), 'service': t['labels'].get('service'), 'health': t['health']} for t in targets],
            'journal_probe_success': get('/api/v1/query?' + query)['data']['result']}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runtime-audit', type=Path, required=True)
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument('--monitoring-audit', type=Path)
    source.add_argument('--prometheus-url')
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    try:
        expected = [yaml.safe_load(f.read_text())['service']['name'] for f in sorted((ROOT / 'inventory/services').glob('*.yml'))]
        runtime = json.loads(args.runtime_audit.read_text())
        monitoring = json.loads(args.monitoring_audit.read_text()) if args.monitoring_audit else live_monitoring(args.prometheus_url)
        issues = assess(runtime, monitoring, expected)
        report = {'automated_core_checks_passed': not issues,
                  'full_phase_acceptance_requires_review': True,
                  'runtime_observed_at': runtime.get('observed_at'), 'issues': issues}
        rendered = json.dumps(report, indent=2) + '\n'
        if args.output:
            args.output.write_text(rendered)
        print(rendered, end='')
        raise SystemExit(1 if issues else 0)
    except (OSError, ValueError, KeyError) as exc:
        p.exit(2, 'Incomplete or inaccessible audit evidence: ' + type(exc).__name__ + '\n')

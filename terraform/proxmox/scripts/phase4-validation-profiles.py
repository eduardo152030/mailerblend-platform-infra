#!/usr/bin/env python3
"""D038: local profile selection, acceptance gates and scoped rollout plan. No remote actions."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]


def config():
    return yaml.safe_load((ROOT / 'services/common/phase4-validation-profiles.yml').read_text())


def profile_for(ct, known_cts):
    if isinstance(ct, bool) or ct not in known_cts:
        raise ValueError('Unknown CT: profile assignment requires inventory identity')
    cfg = config()
    name = 'CRITICAL' if ct in cfg['critical_cts'] else 'STANDARD'
    return dict(cfg['profiles'][name] | cfg.get('ct_observation_windows', {}).get(ct, {}), name=name)


def fingerprint(files, dependencies):
    """Caller must include the entire relevant source/config closure and installed dependency versions."""
    if not files or not dependencies:
        raise ValueError('Source closure and dependency versions are required')
    payload = {'files': {str(p): hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sorted(files, key=str)},
               'dependencies': dependencies}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def reusable_proof(proof, current_fingerprint):
    return (isinstance(current_fingerprint, str) and len(current_fingerprint) == 64
            and proof.get('result') == 'PASS' and proof.get('fingerprint') == current_fingerprint
            and proof.get('evidence_verified') is True)


def assess(evidence, profile):
    """Fail closed on missing evidence; inherited unhealthy status alone is not a regression."""
    if profile not in config()['profiles']:
        raise ValueError('Unknown validation profile')
    p = config()['profiles'][profile]
    if 'ct' in evidence:
        known = [yaml.safe_load(f.read_text())['service']['vmid'] for f in (ROOT/'inventory/services').glob('*.yml')]
        p = profile_for(evidence['ct'], known)
        if p['name'] != profile:
            raise ValueError('CT/profile mismatch')
    gates = ['preflight_pass', 'backup_verified', 'node_ready', 'cadvisor_ready',
             'lxc_cpu_ram_correct', 'docker_metrics_correct', 'timestamps_identity_valid',
             'application_baseline_verified', 'application_no_regression',
             'preexisting_alerts_preserved', 'critical_dependencies_verified',
             'prometheus_collecting', 'alertmanager_ready', 'telegram_errors_unchanged',
             'no_new_oom', 'no_unexpected_restarts', 'rollback_available', 'idempotence_verified']
    if profile == 'CRITICAL':
        gates += ['continuity_verified', 'recovery_verified']
    if evidence.get('telegram_test_required') is not False:
        gates += ['batch_telegram_delivery_verified']
    missing = [k for k in gates if evidence.get(k) is not True]
    if profile == 'STANDARD' and not (evidence.get('rollback_rehearsal_pass') is True or
            reusable_proof(evidence.get('rollback_proof', {}), evidence.get('rollback_fingerprint'))):
        missing.append('compatible_rollback_proof')
    # All samples must pass; actual elapsed time and distinct increasing sample times are mandatory.
    times = evidence.get('sample_elapsed_seconds', [])
    if (not isinstance(times, list) or len(times) < p['minimum_samples'] or
            any(isinstance(t, bool) or not isinstance(t, (int, float)) or not math.isfinite(t) or t < 0 for t in times) or
            any(b <= a or b-a > 45 for a,b in zip(times,times[1:])) or
            not times or times[0] > 1 or times[-1] - times[0] < p['observation_seconds']):
        missing.append('observation_window')
    if evidence.get('all_observation_samples_passed') is not True:
        missing.append('all_observation_samples_passed')
    return {'accepted': not missing, 'profile': profile, 'missing': missing,
            'additional_watch_required': False, 'alert_for_runtime_proven': False}


def plan(registry, queue, known_cts):
    cfg = config(); accepted = set(registry['prometheus_integrated'])
    blocked = {r['ct'] for r in queue['items']}
    known = set(known_cts)
    if accepted & blocked or not (accepted | blocked) <= known:
        raise ValueError('Conflicting or unknown production states')
    pending = known - accepted - blocked
    order = cfg['execution_scope']['recommended_critical_order']
    pending_order = sorted(pending, key=lambda ct: (order.index(ct) if ct in order else -1, ct))
    rows = [dict(ct=ct, profile=profile_for(ct, known)['name']) for ct in pending_order]
    eligible = [r['ct'] for r in rows if r['profile'] == 'STANDARD' and
                r['ct'] not in cfg['execution_scope']['excluded_cts'] and
                cfg['execution_scope']['conventional_pending_authorized'] is True]
    return {'decision': cfg['decision'], 'mode': 'local_plan_only', 'accepted': sorted(accepted),
            'blocked': sorted(blocked), 'pending': rows, 'authorized_standard_order': eligible,
            'critical_deployment_authorized': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Preserve previous evidence; use a new output')
    services = [yaml.safe_load(p.read_text())['service']['vmid'] for p in (ROOT/'inventory/services').glob('*.yml')]
    registry = yaml.safe_load((ROOT/'services/common/exporter-migration.yml').read_text())
    queue = yaml.safe_load((ROOT/'services/common/phase4-recovery-queue.yml').read_text())
    result = plan(registry, queue, services)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

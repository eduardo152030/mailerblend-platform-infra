#!/usr/bin/env python3
"""Reusable reviewed-bundle CPU/RAM instrumentation. Local preparation only; no SSH/apply."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def revision_for(directory,names):
    directory=Path(directory)
    return 'framework-'+hashlib.sha256(''.join((directory/n).read_text() for n in sorted(names) if n!='pilot.py').encode()).hexdigest()[:12]


def instrument(directory, ct, revision_salt=""):
    """Reusable instrumentation. Call only with a reviewed, previously rendered bundle."""
    directory=Path(directory)
    manifest=json.loads((directory/'manifest.json').read_text())
    assert isinstance(ct,int) and ct>0 and manifest['ct']==ct,'Bundle/container identity mismatch'
    assert not any((directory/n).exists() for n in ['baseline.json','applied.json','external-backup-verified.json','memory-alignment.py'])
    spec_contract=importlib.util.spec_from_file_location('metric_contract',ROOT/'scripts/exporter_metric_contract.py');metric_contract_module=importlib.util.module_from_spec(spec_contract);spec_contract.loader.exec_module(metric_contract_module)
    library=metric_contract_module.render_alignment_source('memory')
    (directory/'memory-alignment.py').write_text(library)
    sampler=directory/'sample.py';body=sampler.read_text();marker='    print(json.dumps(out,sort_keys=True))';assert body.count(marker)==1
    block="""    memory_ns={'__name__':'memory_alignment'}
    exec(Path(CPU_HISTORY_PATH).with_name('memory-alignment.py').read_text(),memory_ns)
    try:
        memory_ns['require_collector'](Path(CPU_HISTORY_PATH).with_name('memory-history.jsonl'))
        memory_history=memory_ns['history_for_sample'](out,Path(CPU_HISTORY_PATH).with_name('memory-history.jsonl'))
        out['memory_alignment']=memory_ns['aligned_evidence'](out,memory_history)
    except Exception as exc:
        cpu_ns['record_probe_failure'](out,CPU_HISTORY_PATH,exc)
        raise
"""
    sampler.write_text(body.replace(marker,block+marker))
    observer=directory/'observe.py';body=observer.read_text()
    old="                assert abs(row['value']-api['memory_usage'])<=allowance,'cAdvisor/Docker RAM mismatch: '+name"
    assert body.count(old)==1
    # Supersede only the asynchronous comparison with the same gate at its measured timestamp.
    body=body.replace(old,"                assert api['memory_usage']>=0,'Invalid current Docker RAM gauge'")
    direct="        assert abs(api['memory_usage']-direct)<=max(8*1024*1024,direct*.25),'Docker API/cgroup RAM mismatch'"
    assert body.count(direct)==1
    body=body.replace(direct,"        assert direct>=0,'Invalid current cgroup RAM gauge'")
    marker='    validate_alignment(sample,previous)';assert body.count(marker)==1
    body=body.replace(marker,marker+'\n    validate_memory_alignment(sample,previous)')
    # Import in an isolated namespace: CPU alignment functions must not be shadowed by RAM names.
    code=library.split("\nif __name__=='__main__':")[0]
    prefix="_memory_ns={'__name__':'memory_alignment'}\nexec("+repr(code)+",_memory_ns)\nvalidate_memory_alignment=_memory_ns['validate_alignment']\n"
    observer.write_text(prefix+body)
    helper=directory/'pilot.py';body=helper.read_text()
    original=f"PROJECT = 'exporter-pilot-{ct}'";assert body.count(original)==1
    names=set(manifest['file_sha256'])|{'memory-alignment.py'}
    revision=revision_for(directory,names)
    if revision_salt:
        revision="framework-"+hashlib.sha256((revision+str(revision_salt)).encode()).hexdigest()[:12]
    body=body.replace(original,f"PROJECT = 'exporter-pilot-{ct}-{revision}'")
    assert body.count(f"'-phase4-{ct}-held'")==3
    body=body.replace(f"'-phase4-{ct}-held'",f"'-phase4-{ct}-{revision}-held'")
    helper.write_text(body)
    profile_spec=importlib.util.spec_from_file_location('validation_profiles',ROOT/'scripts/phase4-validation-profiles.py');profiles=importlib.util.module_from_spec(profile_spec);profile_spec.loader.exec_module(profiles)
    window=profiles.profile_for(ct,[ct])
    manifest.update(framework_revision=revision,status='PREPARED_NOT_DEPLOYED_D036',approval_required=True,automatic_continuation=False,
        initial_seconds=window['observation_seconds'],initial_minimum_samples=window['minimum_samples'],validation_profile=window['name'],observation_policy='D-040',
        memory_alignment={'schema':1,'history_interval_seconds':.1 if ct==618 else .5,'max_gap_seconds':2,'max_request_seconds':.5,'max_metric_age_seconds':90,'interpolation':False,'compare_both_endpoints':True,'app_allowance':'max(512KiB,20%) unchanged','exporter_allowance':'max(4MiB,30%) unchanged'},
        reentry_required='Fresh CT-specific audit/directory/checkpoint; preserve historical HALTs/candidates; execution policy must explicitly authorize.')
    for n in names:
        if n.endswith('.py'):compile((directory/n).read_text(),n,'exec')
    manifest['file_sha256']={n:hashlib.sha256((directory/n).read_bytes()).hexdigest() for n in sorted(names)}
    (directory/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


def render(out,audit):
    assert audit['ct'] in [618,622,619,623,617,615,614,61211,611,616,610]
    ct=audit['ct'];out=Path(out)
    assert not out.exists() or not any(out.iterdir()),'Require empty preparation directory'
    spec=importlib.util.spec_from_file_location('approved',ROOT/'scripts/prepare-approved-exporters.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
    assert ct in [618,622] or all(c['running'] or c['name'].startswith(('node_exporter','cadvisor')) for c in audit['containers']),'Stopped application requires review'
    reviewed=dict(audit,containers=[c for c in audit['containers'] if c['running']])
    if ct in [618,622]:reviewed['all_application_names']=[c['name'] for c in audit['containers'] if not c['name'].startswith(('node_exporter','cadvisor'))]
    base.render(ct,out,reviewed)
    import yaml
    path=out/'cadvisor.yml';config=yaml.safe_load(path.read_text());command=config['services']['cadvisor']['command']
    for flag in ['--allow_dynamic_housekeeping=false','--max_housekeeping_interval=30s','--jitter_factor=0','--initial_splay_factor=0']:
        if flag not in command:command.append(flag)
    path.write_text(yaml.safe_dump(config,sort_keys=False))
    return instrument(out,ct,revision_salt=audit.get("deployment_revision", ""))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ct',type=int,choices=[61211],required=True);p.add_argument('--audit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    rows=json.loads(a.audit.read_text());audit=next(r for r in rows if r['ct']==a.ct)
    result=render(a.output,audit)
    print(json.dumps({'ct':a.ct,'status':result['status'],'revision':result['framework_revision'],'files':len(result['file_sha256']),'approval_required':True}))

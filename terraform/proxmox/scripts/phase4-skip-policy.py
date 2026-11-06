"""D035: distinguish healthy baseline, inherited issue, contained regression, global uncertainty."""
REQUIRED=('isolated','originals_verified','application_working','prior_coverage_unchanged','global_monitoring_healthy','recovery_complete','data_safe','backups_recoverable','critical_dependencies_verified')
GLOBAL=('backup','common_iac','validator','ssh_identity','global_prometheus','coverage_loss','alertmanager_telegram','unknown_state','rollback','data_risk','critical_dependency')
PREEXISTING=('preexisting_before_mutation','no_active_changes','isolated','originals_verified','prior_coverage_unchanged','legacy_and_alerts_preserved','global_monitoring_healthy','data_safe','critical_dependencies_verified')

def decide(attempt,policy):
    if attempt.get('completed') and 'validation_profile' in attempt:
        import importlib.util
        from pathlib import Path
        spec=importlib.util.spec_from_file_location('validation_profiles',Path(__file__).with_name('phase4-validation-profiles.py'))
        profiles=importlib.util.module_from_spec(spec);spec.loader.exec_module(profiles)
        acceptance=profiles.assess(attempt,attempt['validation_profile'])
        if acceptance['accepted']:
            return {'result':'DONE','case':'A','continue':True,'reason':'Profile gates passed; application baseline preserved'}
        return {'result':'HALT GLOBAL','case':'D','continue':False,'reason':'Incomplete profile acceptance evidence: '+','.join(acceptance['missing'])}
    if attempt.get('completed'):
        keys=['all_acceptance_gates','initial_observation_pass','watch_pass','global_monitoring_healthy','application_healthy_before','application_healthy_after','critical_dependencies_verified']
        if all(attempt.get(k) is True for k in keys):
            return {'result':'DONE','case':'A','continue':True,'reason':'Healthy baseline preserved; all monitoring acceptance gates and full watch passed'}
        return {'result':'HALT GLOBAL','case':'D','continue':False,'reason':'Incomplete acceptance evidence'}
    category=attempt.get('category','unknown_state')
    if category in GLOBAL:
        return {'result':'HALT GLOBAL','case':'D','continue':False,'reason':'Systemic or unclassified failure: '+category}
    if category=='pre_existing_application':
        missing=[k for k in PREEXISTING if attempt.get(k) is not True]
        if missing:return {'result':'HALT GLOBAL','case':'D','continue':False,'reason':'Pre-existing issue proof missing: '+','.join(missing)}
        return {'result':'BLOCKED / PRE-EXISTING ISSUE','case':'B','continue':True,'reason':'Inherited issue; no mutation; legacy/alerts preserved and next CT critically independent'}
    if category not in policy['isolated_categories']:
        return {'result':'HALT GLOBAL','case':'D','continue':False,'reason':'Systemic or unclassified failure: '+category}
    keys=list(REQUIRED)
    if category=='application_regression':keys+=['baseline_health_restored','regression_contained']
    missing=[key for key in keys if attempt.get(key) is not True]
    if missing:return {'result':'HALT GLOBAL','case':'D','continue':False,'reason':'Skip safety evidence missing: '+','.join(missing)}
    return {'result':'BLOCKED / ROLLED BACK','case':'C','continue':True,'reason':'Isolated failure; original health restored and regression contained'}

def sequence(policy,attempt,record):
    results=[]
    assert policy['maximum_attempts_per_ct']==1
    assert len(policy['order'])==len(set(policy['order']))
    assert not set(policy['order']) & set(policy['deferred']+policy['excluded_exporters'])
    for ct in policy['order']:
        try:evidence=attempt(ct)
        except BaseException as exc:evidence={'completed':False,'category':'unknown_state','failure_type':type(exc).__name__}
        decision=decide(evidence,policy)
        row={'ct':ct,'evidence':evidence,**decision};record(row);results.append(row)
        if not decision['continue']:break
    return results

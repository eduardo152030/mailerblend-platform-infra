#!/usr/bin/env python3
"""Build a deterministic, inventory-checked rollout plan; never connects or executes."""
import argparse
import json
from pathlib import Path
import yaml
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
# Ordered gates, not concurrent groups. Approval must be obtained per future batch.
BATCHES=[
 ('R1','Canario sin aplicaciones', ['infra-hola']),
 ('R2','Gestión interna y workers', ['infra-project-gestion','infra-excraper']),
 ('R3','Aplicaciones con almacenamiento', ['infra-pulpo','infra-gestoria']),
 ('R4','Entrada y analítica pública', ['infra-orbit','infra-mailerblend-edge','infra-nucleoedge']),
 ('R5','Plataforma multiusuario con base de datos', ['svc01']),
 ('R6','Último lote de aplicaciones: recuperadas recientemente', ['infra-composable-crm','infra-eva-assistant-bot']),
 ('R7','Plano de observabilidad, Prometheus al final', ['infra-grafana','infra-blackbox','infra-prom']),
]
STEPS=['scope_and_live_preflight','freeze_model_and_exact_images','snapshot_originals_and_load_archive',
       'verify_pve_and_offhost_backups','apply_exporters_only','validate_real_metrics_and_application','integrate_source_verified_ct_into_prometheus_and_rules',
       'exercise_rollback_and_resume_same_ids','second_apply_without_recreation',
       'verify_exporter_backed_rule_alertmanager_telegram_chain','observe_integrated_using_batch_policy_and_continue_watch','archive_evidence_and_config_offhost','accept_ct_before_next']


def build():
    inventory={}
    for path in sorted((ROOT/'inventory/services').glob('*.yml')):
        s=yaml.safe_load(path.read_text())['service']
        assert s['name'] not in inventory
        inventory[s['name']]={'service':s['name'],'ct':int(s['vmid']),'ip':s['ip'].split('/')[0]}
    accepted_names={'infra-journal-web','infra-journal-api','infra-journal-db'}
    ordered=[n for _,_,names in BATCHES for n in names]
    assert len(ordered)==len(set(ordered)) and set(ordered)|accepted_names==set(inventory)
    assert len(inventory)==17 and len({s['ct'] for s in inventory.values()})==17
    ps=importlib.util.spec_from_file_location('window_policy',ROOT/'scripts/rollout-observation-policy.py');pm=importlib.util.module_from_spec(ps);ps.loader.exec_module(pm)
    lock=json.loads((ROOT/'services/common/phase4-images.json').read_text())
    historical=json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-runtime-audit.json').read_text())
    resources={s['service']:s['proxmox'] for s in historical['services']}
    batches=[]
    for ident,reason,names in BATCHES:
        rows=[]
        for name in names:
            r=dict(inventory[name]);r['last_audit_cores']=int(resources[name]['cores']);r['last_audit_memory_mib']=int(resources[name]['memory'])
            r['resources_require_live_revalidation']=True
            r['node_image']=lock['node'][name]['image'];r['cadvisor_image']=lock['cadvisor_candidate']['image']
            assert '@sha256:' in r['node_image'] and '@sha256:' in r['cadvisor_image']
            r['containerd_socket_approval']='PENDING_CT_SPECIFIC_REVIEW'
            r['application_contract']='REQUIRES_CT_SPECIFIC_BASELINE_AND_READ_ONLY_PROBE'
            rows.append(r)
        batches.append({'batch':ident,'reason':reason,'approval':'PENDING','execution':'NOT_AUTHORIZED','ct_order':rows,'steps_per_ct':STEPS,'observation':pm.policy(ident),'technical_result':'PASS' if ident=='R1' else 'NOT_EXECUTED'})
    return {'schema':1,'mode':'PLAN_ONLY_NO_REMOTE_ACTIONS','required_total_lxc':17,'journal_order':[624,626,625],
            'remaining_ct_count':14,'remaining_batches':batches,'concurrency':1,
            'stop_on_failure':True,'force_stop_allowed':False,'apps_or_volumes_may_change':False,
            'incremental_integration':{'bootstrap_cts':[624,626,625],'required_before_next_ct':True,'complete_chain_required_per_ct':True},
            'global_integration':{'after_all_17_validated':True,'independent_validation_required':True,
              'scope':['17 Node','17 cAdvisor','Grafana job','Journal probes','lxc_cpu compatible rules','FIRING/RESOLVED Telegram delivery'],
              'execution_in_current_batch':False}}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path)
    a=p.parse_args();body=json.dumps(build(),indent=2)+'\n'
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(body)
    else:print(body,end='')

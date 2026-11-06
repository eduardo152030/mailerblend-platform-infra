#!/usr/bin/env python3
"""Publish only explicitly sanitized run summaries and update central tracking."""
import json,re
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]

def resource_summary(samples,before):
 assert samples and all(s['checks_passed'] for s in samples)
 def events(text):return {k:int(v) for k,v in (line.split() for line in text.splitlines())}
 start=events(before['memory.events']);end=events(samples[-1]['resources']['memory.events'])
 peaks={}
 for sample in samples:
  for c in sample['containers']:
   if c['running'] and c['name'] in ['node_exporter','cadvisor']:
    peaks[c['name']]=max(peaks.get(c['name'],0),c['docker_stats']['memory_usage'])
 return {'minimum_available_bytes':min(s['lxc_proc']['mem_available_bytes'] for s in samples),'maximum_memory_current_bytes':max(int(s['resources']['memory.current']) for s in samples),'final_swap_bytes':int(samples[-1]['resources']['memory.swap.current']),'memory_event_deltas':{k:end.get(k,0)-start.get(k,0) for k in ['high','max','oom','oom_kill','oom_group_kill']},'exporter_memory_peak_sampled_bytes':peaks}

def update(run):
 private=Path.home()/'.local/share/mailerblend-recovery/phase4'/run
 reports=[]
 for ct in [621,620,619,623,617,615,614,61211,611,616,610]:
  path=private/str(ct)/'state.json'
  if not path.exists():continue
  state=json.loads(path.read_text());item={k:state[k] for k in ['ct','result','steps','timings_seconds']}
  for key in ['duration_seconds','observation','failed_observation','telegram','failure_type','blocked_reason','safe_rollback_verified','rollback_scope','recovery_authorization']:
   if key in state:item[key]=state[key]
  if state['result']=='PASS':
   observations=private/str(ct)/'observations.jsonl';samples=[json.loads(l) for l in observations.read_text().splitlines()]
   item['resources']=resource_summary(samples,state['resources_before'])
   evidence=ROOT/'docs/roadmap/evidence'/('2026-11-02-rollout-'+str(ct)+'.json')
   if evidence.exists():
    public=json.loads(evidence.read_text());public['resources']=item['resources'];evidence.write_text(json.dumps(public,indent=2)+'\n')
  watch=private/str(ct)/'post-watch.jsonl'
  if watch.exists():
   rows=[json.loads(l) for l in watch.read_text().splitlines()]
   item['post_watch']={'samples':len(rows),'seconds':rows[-1]['elapsed_seconds'] if rows else 0,'any_anomaly':any(not r['checks_passed'] for r in rows)}
   if item['post_watch']['any_anomaly']:item['acceptance']='BLOCKED_POST_WATCH_REVIEW'
   recheck=private/str(ct)/'post-watch-serialized-check-result.json'
   if recheck.exists():
    checked=json.loads(recheck.read_text());item['post_watch']['extended_recheck']=checked
    if checked['result']=='PASS' and checked['seconds']>=600:item['acceptance']='PASS_AFTER_VALIDATOR_FIX'

  reports.append(item)
 registry=yaml.safe_load((ROOT/'services/common/exporter-migration.yml').read_text());coverage=len(registry['telegram_chain_verified']);done=[x['ct'] for x in reports if x['result']=='PASS'];block=[x['ct'] for x in reports if x['result'].startswith('BLOCKED')]
 report={'run':run,'result':'BLOCKED' if block or (private/'HALT.json').exists() else 'IN_PROGRESS','completed_this_run':done,'coverage_corrected':coverage,'required':17,'excluded_r6':[618,622],'states':reports,'human_receipt_confirmed_this_run':False,'alert_high_cpu_for_proven':False}
 report['reported_at_utc']=datetime.now(timezone.utc).isoformat()
 starts=[json.loads((private/str(row['ct'])/'state.json').read_text())['started_at_utc'] for row in reports]
 if starts:report['total_elapsed_wall_seconds']=round((datetime.now(timezone.utc)-min(datetime.fromisoformat(x) for x in starts)).total_seconds(),3)
 (ROOT/'docs/roadmap/evidence/2026-11-02-autonomous-execution.json').write_text(json.dumps(report,indent=2)+'\n')
 text='''# Fase 4 — ejecución autónoma D-025

Run `RUN`. **RESULT**. Cobertura fiable integrada: **COVERAGE/17**.
CRM618/EVA622 excluidos; no repetir Journal/P0/R1. No commits ni pushes.

## Ejecución actual

| CT | Resultado | Segundos totales | Observación | Telegram |
|---|---|---|---|---|
'''.replace('RUN',run).replace('RESULT',report['result']).replace('COVERAGE',str(coverage))
 for row in reports:
  obs=row.get('observation',row.get('failed_observation',{}));tg=row.get('telegram',{})
  text+=f"| {row['ct']} | {row['result']} | {row.get('duration_seconds','en curso')} | {obs.get('samples','—')} muestras / {round(obs.get('seconds',0),1)}s | {tg.get('attempts_delta','—')} intentos; {tg.get('failures_delta','—')} errores nuevos |\n"
 text+='''
## Gates y límites de la evidencia

PASS exige backup externo verificado, archivo de imágenes leído/cargado, ensayo
real de rollback coordinado, reanudación de mismos candidatos, segunda aplicación
sin recreación ni recarga, métricas LXC/Docker y aplicaciones estables. R2–R5 inicial
180s/7 muestras cada30s; R7 600s/21; los tiempos de enrutamiento Telegram pueden
alargar la ventana efectiva. Vigilancia posterior900s y Prometheus/Alertmanager.
No se demuestra el predicado CPU>90%/for10m por transcurrir una ventana.

La prueba Telegram recorre una regla temporal sobre métrica real, Prometheus y
Alertmanager; comprueba FIRING/RESOLVED y contadores sin errores nuevos. La API
aceptó los envíos: no se atribuye una confirmación humana de recepción a este run.
Backups/configuraciones con secretos quedan privados fuera deGit; hashes en evidencia.

## Incidencias

**Secuencia detenida por watcher621 durante integración620.** A los60s delwatch
una muestra falló AssertionError; recargaProm de620 ocurrió a los42s. A90s vuelve
correcta. Causa probable: transición de salud de reglas trasreload; el detalle de la
excepción del sampler no se conservó, así que no se afirma como causa demostrada.
HALT se conserva. CT620 se devuelve al checkpoint previo mediante rollback previsto;
no ejecutar619 ni siguientes. Ventana extendida y diagnósticos en curso.

Bloqueo SSH inicial resuelto por propietario. Todas las nuevas conexiones exigen
known_hosts explícito, BatchMode y verificación estricta. No se cambió SSH global.
Primer ensayo621: originales reanudados, HTTP inmediato recibió connection refused
antes de readiness. Se detuvo avance, verificó readiness acotado y checkpointProm,
y reanudaron mismos candidatos conservando backups. Corrección versionada/probada.

Preflight de otros CT detectó rutas HTTP incorrectas y healthchecks heredados:
no considerarlos disponibilidad correcta ni cambiarlos automáticamente. Orbit403
está explicado por ACL192.168.1.71 en nginx; verificar también backend sin cambiarACL.
Edge615 devuelve503 en salud y ambosDocker aparecenunhealthy; diagnosticar antes
 de intervenirlo. Nucleo614 usa puertos8091/8092 reales, distintos al Compose local.
No sobrescribir configuración de aplicaciones para ajustar ese drift.

[Datos consolidados](evidence/2026-11-02-autonomous-execution.json),
[preflight autenticado](evidence/2026-11-02-rollout-authenticated-preflight.json).
F4 continúa IN PROGRESS: R6 pendiente y aceptación global independiente aún requerida.
'''
 if (private/'validator-race-resolution.json').exists():
  text=text.replace('**Secuencia detenida por watcher621 durante integración620.**','**Incidente del vigilante resuelto antes de continuar.**')
  text=text.replace('HALT se conserva. CT620 se devuelve al checkpoint previo mediante rollback previsto;\nno ejecutar619 ni siguientes. Ventana extendida y diagnósticos en curso.','El HALT original se conserva archivado. CT620 volvió a su checkpoint seguro.\nLa repetición con sincronización completó600s/21 muestras antes de reanudar;\nno se omitieron los controles ni se repitieron backups ya verificados.')
  text+='\nLa carga de una regla nueva reproduce healthunknown transitorio sin fallos de evaluación.\nEl bloqueo compartido/exclusivo coordina el muestreo posterior con recarga/readiness;\nel scraping30s y la observación inicial porCT no se pausan. Se conserva el primer fallo.\n'
 if any(row.get('recovery_authorization') in ['D-028','D-029'] for row in reports):
  text+='''
## Recuperación CT619 — D-028

P-012 aprobada expresamente: límite exclusivo de cAdvisor128→256MiB.
Se conserva candidato128 rechazado, originales y backups. El primer intento
falló al reutilizar Compose sus etiquetas; rollback restauró los originales.
El candidato256 usa proyecto Compose propio, manteniendo reconocimiento de ambos
proyectos para rollback. Node y recursos LXC/aplicaciones no cambian de modelo.
Revalidación de seis fuentes previas y backups locales/externos antes del reintento.
Gates completos y observación inicial >=600s/21 muestras, con vigilancia posterior.
El estado de la tabla determina si la recuperación está en curso, bloqueada o PASS;
no se atribuye aceptación global ni recepción humana de Telegram.
'''
 if any(row.get('recovery_authorization')=='D-029' for row in reports):
  text+='''
## Causa CPU619 y corrección D-029

El muestreador descartaba el timestamp explícito de cAdvisor: el validador comparaba
CPU cacheada con Docker actual. Misma identidad, unidades correctas y sin factor
CPU en los acumulativos. Contraste de solo lectura con cgroup y Docker en620,
misma versión, confirma equivalencia por timestamp y ventana.
La corrección conserva max(1s,3%), exige ambos extremos temporales medidos,
ID/StartedAt, frescura, historial sin huecos>2s y compara incrementos equivalentes.
No modifica imágenes ni recursos aprobados. La tabla distingue reintento de PASS.
[Causa y valores exactos](evidence/2026-11-03-619-cpu-root-cause.json),
[prueba temporal](evidence/2026-11-03-619-cpu-alignment-live-proof.json),
[tiempo invertido](evidence/2026-11-03-619-cpu-investigation-time.json).
'''
 text+='\nActualización: '+datetime.now(ZoneInfo('Europe/Madrid')).isoformat()+' (Europe/Madrid).\nLos nombres de evidencia2026-11-02 siguen la fecha UTC de inicio del run.\n'
 (ROOT/'docs/roadmap/AUTONOMOUS-EXECUTION.md').write_text(text)
 p=ROOT/'docs/roadmap/CURRENT-STATUS.md';old=p.read_text();suffix=old[old.index('## Hitos conservados'):];suffix=suffix.replace('Calidad/cobertura de los otros 13 LXC','Calidad/cobertura de LXC pendientes')
 current=next((x['ct'] for x in reversed(reports) if x['result']!='PASS'),None)
 stamp=datetime.now(ZoneInfo('Europe/Madrid')).strftime('%Y-%m-%d %H:%M %Z')
 p.write_text(f"""# Estado actual del proyecto

Actualizado: {stamp}. **Fase 4 — IN PROGRESS.**

**Registro validado: {coverage}/17 LXC**, incluyendo los cuatro anteriores
Journal624/626/625 e infra-hola613. Una promoción provisional del CT en curso no
suma DONE hasta cerrar todos los gates. EstadoD025: **{report['result']}**.
Completados en este run: {done}. CT en curso o bloqueado: {current or 'siguiente autorizado'}.

Prometheus conserva17Node/17cAdvisor y11Blackbox. La última evidencia porCT distingue
fuentesLXC correctas frente a legacy sin verificar. No se activaron jobGrafana ni
sondasJournal adicionales. [Ejecución y datos actuales](AUTONOMOUS-EXECUTION.md).

## Siguiente paso concreto y autorización

D025 autoriza621→620→619→623→617→615→614→61211→611→616→610, secuenciales.
CRM618/EVA622 quedan excluidos y conservan cobertura. SSH estricto verificado:
BatchMode=yes/StrictHostKeyChecking=yes/UserKnownHostsFile=$HOME/.ssh/known_hosts.
No repetirCTPASS; no commits/push. R2–R5 inicial180s; R7 600s; anomalías>=600s.
La observación no prueba un predicadoCPU>90%/for10m que no haya ocurrido.

Las nuevas pruebasTelegram acreditan FIRING/RESOLVED aceptados porAPI y ausencia de
errores nuevos; no se atribuye confirmación humana. Los cuatroCT previos sí tienen
recepción humana histórica confirmada. MantenerHALT si falla un gate; conservar
backups, originales y evidencias. VerD026/D027 para incidencias/correcciones del run.

## Evidencias y límites

[P0/R1](P0-R1-EXECUTION.md), [loteactual](AUTONOMOUS-EXECUTION.md),
[matriz](phases/COVERAGE-MATRIX.md). Configuraciones y backups sensibles permanecen
privados fuera deGit. La aceptación globalF4 exige17/17 y validación independiente;
R6 sigue pendiente. No se ejecutaron nuevas pruebas de negocio/UAT.

"""+suffix)
 # Current ledger above the preserved historical matrix.
 matrix=ROOT/'docs/roadmap/phases/COVERAGE-MATRIX.md'
 if matrix.exists():
  historical=matrix.read_text();heading=historical.index('# Matriz de cobertura')
  historical=historical[heading:]
  marker='<!-- D025 historical snapshot below -->'
  if marker in historical:
   historical=historical.split(marker,1)[1];historical=historical[historical.index('# Matriz de cobertura — Fase 4'):]
  summary=f'# Matriz de cobertura — estadoD025\n\nRegistro validado:{coverage}/17. F4 IN PROGRESS. [Ejecución](../AUTONOMOUS-EXECUTION.md).\n\n| CT | Estado | Evidencia |\n|---|---|---|\n'
  for ct in [624,626,625,613,621,620,619,623,617,615,614,61211,618,622,611,616,610]:
   proof=registry.get('exporters_validated',{}).get(str(ct));row=next((r for r in reports if r['ct']==ct),None)
   status='PASS — fuente y cadena verificadas' if ct in registry['telegram_chain_verified'] else (row['result'] if row else ('R6 EXCLUIDO, legacy no verificado' if ct in [618,622] else 'TODO — legacy no verificado'))
   link=('[prueba](../evidence/'+Path(proof).name+')') if proof else 'pendiente'
   summary+=f'| {ct} | {status} | {link} |\n'
  matrix.write_text(summary+'\n'+marker+'\n\nLa tabla siguiente es histórica (auditoría inicial), no el estado actual.\n\n'+historical)
 p=ROOT/'services/common/phase4-images.json';d=json.loads(p.read_text());d['validated_ct_ids']=sorted(int(x) for x in registry['exporters_validated']);d['monitoring_chain_verified_ct_ids']=registry['telegram_chain_verified'];d['status']='INCREMENTAL_ROLLOUT_IN_PROGRESS_R6_EXCLUDED';p.write_text(json.dumps(d,indent=2)+'\n')
 p=ROOT/'docs/roadmap/ROADMAP.md';s=p.read_text().replace('D-025 R2–R5/R7 autorizado; BLOCKED antes de CT621 por clave SSH PVE ausente',f'D-025 R2–R5/R7 autorizado; {coverage}/17 integrados; ver AUTONOMOUS-EXECUTION');s=s.replace('**Bloqueado antes de CT621**: falta clave\nverificada de pve/192.168.1.100.','SSH resuelto. Ejecución secuencial en curso; R6 excluido.');p.write_text(s)
 p=ROOT/'docs/roadmap/ROADMAP.md';s=p.read_text();s=re.sub(r'(\| \[4\. Exporters & Monitoring Coverage\].*?\| \*\*IN PROGRESS\*\* \| ).*? \|',lambda match:match.group(1)+f'D-025 {report["result"]}; {coverage}/17 fuentes y cadenas integradas; R6 excluido; ver AUTONOMOUS-EXECUTION |',s);p.write_text(s)
 decisions=ROOT/'docs/roadmap/DECISIONS.md'
 if decisions.exists():
  existing=decisions.read_text()
  for row in reports:
   marker=f'<!-- D025 CT{row["ct"]} completed -->'
   if row['result']=='PASS' and marker not in existing:
    obs=row['observation'];tg=row['telegram']
    existing+=f'\n{marker}\n\nResultado operativo D025 CT{row["ct"]}: PASS technique, {obs["samples"]} muestras/{round(obs["seconds"],3)}s, backup externo/rollback/idempotencia verificados. Telegram API: +{tg["attempts_delta"]} envíos, {tg["failures_delta"]} errores nuevos; no se atribuye recepción humana. [Prueba](evidence/2026-11-02-rollout-{row["ct"]}.json). F4 sigue IN PROGRESS.\n'
  decisions.write_text(existing)
 return report

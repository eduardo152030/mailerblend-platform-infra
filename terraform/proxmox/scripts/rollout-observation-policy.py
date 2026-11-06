#!/usr/bin/env python3
"""Shared local policy: initial acceptance is separate from continuous watch and alert-for proof."""
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
REQUIRED=['node_ready','cadvisor_ready','lxc_cpu_ram_correct','docker_metrics_correct','no_new_oom','no_unexpected_restarts','application_available','prometheus_alertmanager_healthy']

def policy(batch):
 if batch in ['STANDARD','CRITICAL']:
  cfg=yaml.safe_load((ROOT/'services/common/phase4-validation-profiles.yml').read_text());p=cfg['profiles'][batch]
  return {'seconds':p['observation_seconds'],'minimum_samples':p['minimum_samples'],'interval':cfg['sample_interval_seconds'],'watch_seconds':p['post_watch_seconds'],'extended_seconds':0,'extended_minimum_samples':0}
 d=yaml.safe_load((ROOT/'services/common/rollout-observation.yml').read_text())
 assert batch in d['initial_windows']
 return d['initial_windows'][batch]|{'interval':d['sample_interval_seconds'],'watch_seconds':d['post_deployment']['external_watch_seconds'],'extended_seconds':d['anomaly']['minimum_extended_seconds'],'extended_minimum_samples':d['anomaly']['minimum_extended_samples']}

def assess(samples,batch,elapsed,extended=False):
 p=policy(batch);required=REQUIRED if batch not in ['STANDARD','CRITICAL'] else [k if k!='application_available' else 'application_no_regression' for k in REQUIRED]
 bad=[{'sample':i,'failed':[k for k in required if row.get(k) is not True]} for i,row in enumerate(samples) if not all(row.get(k) is True for k in required)]
 required_seconds=max(p['seconds'],600) if extended else p['seconds']
 required_samples=max(p['minimum_samples'],21) if extended else p['minimum_samples']
 ready=elapsed>=required_seconds and len(samples)>=required_samples and not bad
 return {'initial_window_passed':ready,'halt_advance':bool(bad),'anomalies':bad,
         'extended_observation_min_seconds':600 if bad else None,'extended_minimum_samples':21 if bad else None,
         'continuous_watch_still_required':p['watch_seconds']>0,'alert_for_runtime_firing_validated':False,
         'note':'No elapsed window proves a threshold alert without its predicate holding for the configured for.'}

class WindowTracker:
 def __init__(self,initial_seconds,minimum_samples,watch_seconds,extension_seconds=600):
  self.initial_seconds=initial_seconds;self.minimum_samples=minimum_samples;self.end_after=watch_seconds;self.extension_seconds=extension_seconds;self.samples=0;self.anomaly=False;self.initial_passed=False
 def observe(self,elapsed,healthy):
  self.samples+=1
  if not healthy:
   if not self.anomaly:self.end_after=max(self.end_after,elapsed+self.extension_seconds)
   self.anomaly=True;self.initial_passed=False
  if not self.anomaly and elapsed>=self.initial_seconds and self.samples>=self.minimum_samples:self.initial_passed=True
  return {'initial_window_passed':self.initial_passed,'halt_advance':self.anomaly,'end_after':self.end_after,'alert_for_runtime_firing_validated':False}
 def finished(self,elapsed):return elapsed>=self.end_after

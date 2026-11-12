"""Offline D078 analysis of previously collected JSON. No network, models or writes to CT."""
import argparse
import json
from pathlib import Path

ap=argparse.ArgumentParser();ap.add_argument('--private-dir',type=Path,required=True);ap.add_argument('--d077-trial',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
load=lambda name:json.loads((args.private_dir/name).read_text())
good=json.loads(args.d077_trial.read_text())['talker'];failed=load('jobs-detail.json')
runs={'D077':good,**{ident:d['supervisor'] for ident,d in failed.items()}}
result={'GiB_bytes':2**30,'runs':{},'no_inference_executed':True}
for ident,s in runs.items():
 rows=s['measurements'];base=s['baseline'];peak=max(rows,key=lambda x:x['ct_current'])
 stat=lambda x:x.get('ct_stat',x.get('ct_memory_stat',{}))
 cpu=[(y['worker_cpu']['usage_usec']-x['worker_cpu']['usage_usec'])/1e6/(y['elapsed']-x['elapsed']) for x,y in zip(rows,rows[1:]) if 'worker_cpu' in x and 'worker_cpu' in y]
 result['runs'][ident]={'baseline':{k:stat(base).get(k) for k in ['anon','file','kernel','active_file','inactive_file']},'baseline_current':base['ct_current'],'peak':{k:peak.get(k) for k in ['ct_current','worker_current','rss_bytes','ct_swap']},'peak_ct_stat':{k:stat(peak).get(k) for k in ['anon','file','kernel','active_file','inactive_file','file_dirty','file_mapped']},'peak_worker_stat':{k:peak.get('worker_stat',peak.get('worker_memory_stat',{})).get(k) for k in ['anon','file','kernel']},'other_anon_at_peak':stat(peak)['anon']-peak.get('worker_stat',peak.get('worker_memory_stat',{}))['anon'],'elapsed_supervisor':s['elapsed_total'],'cpu_mean_sampled_cores':sum(cpu)/len(cpu),'cpu_peak_sampled_cores':max(cpu),'ct_high_events_delta':rows[-1]['ct_events']['high']-base['ct_events']['high'],'ct_oom_delta':rows[-1]['ct_events']['oom_kill']-base['ct_events']['oom_kill'],'ct_swap_max':max(x['ct_swap'] for x in rows),'ct_psi_full_avg10_max':max(x['ct_psi_full_avg10'] for x in rows),'host_available_min':min(x['host_available'] for x in rows),'error':s.get('error'),'process_stopped':not s['container_state']['Running'] and s['container_state']['Pid']==0}
 if ident!='D077':result['runs'][ident].update(reference_ready=False,new_narration_tokens=0,new_narration_EOS=False,checkpoint_exists=failed[ident]['checkpoint_dir_exists'],events=failed[ident]['events'])
result['recovery']='No narration checkpoint in either failed job; Decoder-only recovery impossible'
args.output.write_text(json.dumps(result,indent=2)+'\n')

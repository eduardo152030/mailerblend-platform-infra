#!/usr/bin/env python3
"""PVE: selecciona PP2048 más rápido entre candidatos seguros; conserva ranking y r3."""
import pathlib,json
ROOT=pathlib.Path('/root/ia-local/latency');records=[];selected={}
for alias in ['gemma-4-26b','qwen3.6-35b']:
 candidates=[]
 for b in [512,2048]:
  for ub in [128,256,512]:
   kinds={};peak=0
   for kind in ['pp','tg']:
    stem=f'{alias}-b{b}-ub{ub}-{kind}';rows=json.loads((ROOT/'bench'/str(stem+'.json')).read_text());proof=json.loads((ROOT/'bench'/str(stem+'-memory.json')).read_text());assert proof['pass']
    assert all(len(row['samples_ts'])==3 for row in rows),'Missing repetitions'
    assert all(row['n_threads']==(4 if kind=='pp' else 3) for row in rows)
    assert all(max(s['rss'],s['resident'])<.9*s['limit'] for s in proof['samples'])
    peak=max(peak,max(max(s['rss'],s['resident']) for s in proof['samples']))
    for row in rows:kinds['pp'+str(row['n_prompt']) if kind=='pp' else 'tg128']=row['avg_ts']
   candidates.append({'model':alias,'batch_size':b,'ubatch_size':ub,'threads':3,'threads_batch':4,'peak_resident_or_rss_gib':peak/1024**3,**kinds})
 ranked=sorted(candidates,key=lambda r:(r['pp2048'],r['pp512'],r['tg128']),reverse=True);records+=candidates;selected[alias]={k:ranked[0][k] for k in ['batch_size','ubatch_size','threads','threads_batch']};selected[alias]['ranking']=[{k:r[k] for k in ['batch_size','ubatch_size','pp512','pp2048','tg128','peak_resident_or_rss_gib']} for r in ranked]
(ROOT/'benchmark-summary.json').write_text(json.dumps({'selection':'Highest pp2048, pp512 and tg128 as tie-breakers; all r3 and RSS/resident<90%','rows':records},indent=2)+'\n');(ROOT/'performance-tuning.json').write_text(json.dumps(selected,indent=2)+'\n');print(json.dumps(selected,indent=2))

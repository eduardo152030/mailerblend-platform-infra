#!/usr/bin/env python3
"""CPU dtype/SDPA timings on bounded synthetic matrices, not model inference."""
import json,time,statistics,resource
import torch
out={'torch':torch.__version__,'cpu_capability':torch.backends.cpu.get_cpu_capability(),'mkldnn':torch.backends.mkldnn.enabled,'original_threads':torch.get_num_threads(),'original_interop':torch.get_num_interop_threads(),'tests':[]}
for threads in [1,2,3]:
 torch.set_num_threads(threads)
 for dtype in [torch.float32,torch.bfloat16,torch.float16]:
  for seq in [1,48]:
   x=torch.randn(seq,1024,dtype=dtype);w=torch.randn(3072,1024,dtype=dtype);times=[]
   with torch.inference_mode():
    for i in range(4):
     t=time.perf_counter();y=torch.nn.functional.linear(x,w);elapsed=time.perf_counter()-t
     if i:times.append(elapsed)
   out['tests'].append({'threads':threads,'dtype':str(dtype),'op':'linear','shape':[seq,1024,3072],'median_seconds':statistics.median(times),'finite':bool(torch.isfinite(y).all())})
  q=torch.randn(1,8,48,128,dtype=dtype)
  with torch.inference_mode():
   t=time.perf_counter();y=torch.nn.functional.scaled_dot_product_attention(q,q,q,is_causal=True);dt=time.perf_counter()-t
  out['tests'].append({'threads':threads,'dtype':str(dtype),'op':'sdpa','seconds':dt,'finite':bool(torch.isfinite(y).all())})
out['rss_peak_bytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
print(json.dumps(out,indent=2))

"""Small bounded FP32/BF16 benchmark in the existing Voicebox runtime. No Qwen import/load."""
import os,time,json,resource,signal,statistics,importlib.metadata
resource.setrlimit(resource.RLIMIT_CPU,(45,50));signal.alarm(60)
import torch
before={'threads':torch.get_num_threads(),'interop_threads':torch.get_num_interop_threads()}
torch.set_num_threads(2);torch.set_num_interop_threads(1);torch.manual_seed(42)
r={'torch':torch.__version__,'qwen_tts_package':importlib.metadata.version('qwen-tts'),'before_threads':before,'benchmark_threads':torch.get_num_threads(),'benchmark_interop_threads':torch.get_num_interop_threads(),'cpu_capability':torch.backends.cpu.get_cpu_capability(),'mkldnn_available':torch.backends.mkldnn.is_available(),'mkldnn_enabled':torch.backends.mkldnn.enabled,'mkl_available':torch.backends.mkl.is_available(),'openmp_available':torch.backends.openmp.is_available(),'environment':{k:os.environ.get(k) for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','OMP_WAIT_POLICY','KMP_AFFINITY','MKL_DYNAMIC','OMP_DYNAMIC']},'parallel_info':torch.__config__.parallel_info(),'build_config':torch.__config__.show(),'cpu_native_bf16':getattr(torch.cpu,'_is_avx512_bf16_supported',lambda:None)(),'results':[]}
with torch.inference_mode():
 for shape in [(1,1024,1024),(64,1024,1024),(512,512,512)]:
  M,K,N=shape;a=torch.randn(M,K);b=torch.randn(K,N);values={torch.float32:(a,b),torch.bfloat16:(a.bfloat16(),b.bfloat16())};times={str(t):[] for t in values}
  for dtype,(x,y) in values.items():
   for _ in range(2):torch.mm(x,y)
  for repeat in range(5):
   for dtype in ([torch.float32,torch.bfloat16] if repeat%2==0 else [torch.bfloat16,torch.float32]):
    x,y=values[dtype];t=time.perf_counter();z=torch.mm(x,y);times[str(dtype)].append(time.perf_counter()-t);assert torch.isfinite(z).all()
  ref=torch.mm(a,b);got=torch.mm(a.bfloat16(),b.bfloat16()).float();med={k:statistics.median(v) for k,v in times.items()}
  r['results'].append({'operator':'mm','shape_MKN':shape,'seconds':times,'median_seconds':med,'bf16_over_fp32':med['torch.bfloat16']/med['torch.float32'],'relative_l2_error':float(torch.linalg.vector_norm(got-ref)/torch.linalg.vector_norm(ref))})
 a=torch.randn(1,64,256);b=torch.randn(64,64,3);times={}
 for dtype in [torch.float32,torch.bfloat16]:
  x=a.to(dtype);y=b.to(dtype);torch.nn.functional.conv1d(x,y,padding=1);vals=[]
  for _ in range(5):t=time.perf_counter();z=torch.nn.functional.conv1d(x,y,padding=1);vals.append(time.perf_counter()-t);assert torch.isfinite(z).all()
  times[str(dtype)]=vals
 med={k:statistics.median(v) for k,v in times.items()};r['results'].append({'operator':'conv1d','input_shape':[1,64,256],'weight_shape':[64,64,3],'seconds':times,'median_seconds':med,'bf16_over_fp32':med['torch.bfloat16']/med['torch.float32']})
r['rss_hwm_bytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;r['model_loaded']=False;print(json.dumps(r));signal.alarm(0)

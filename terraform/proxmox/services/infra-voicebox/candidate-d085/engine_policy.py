"""Candidate admission. Pure Python: no imports or loading of ML models."""
if __package__:
    from .qwen_language_policy import validate_request as validate_qwen, OWNER, WORKER_PROTOCOL, EXPECTED_WORKER_SHA256, policy_fingerprint
else:
    from qwen_language_policy import validate_request as validate_qwen, OWNER, WORKER_PROTOCOL, EXPECTED_WORKER_SHA256, policy_fingerprint
LANGUAGES = ['es','en']
CB = {'engine':'chatterbox','variant':'multilingual-v3','model_size':'default',
      'max_chars':240,'max_tokens':400,'timeout_seconds':300,
      'worker_hard_bytes':8*2**30,'worker_stop_bytes':7*2**30,
      'predicted_increment_bytes':7*2**30,'margin_bytes':512*2**20}

def validate(request):
    engine=request.get('engine','qwen')
    if engine=='qwen':return validate_qwen(request)
    if engine!='chatterbox':raise ValueError('Motor aislado no habilitado')
    if request.get('profile_id')!=OWNER or type(request.get('seed')) is not int or request['seed']!=42:
        raise ValueError('Chatterbox requiere Eduardo y semilla42')
    if request.get('language') not in LANGUAGES or request.get('model_size') not in [None,'default']:
        raise ValueError('Selecciona Chatterbox Multilingual V3, español o inglés')
    if request.get('instruct') or request.get('personality'):
        raise ValueError('Instrucciones y personalidad no habilitadas')
    if not isinstance(request.get('text'),str) or not 1<=len(request['text'])<=CB['max_chars']:
        raise ValueError('Chatterbox experimental admite1..240caracteres; narraciones largas no validadas')
    return request

def admission(data):
    """Called BEFORE creating a history row or model-management task."""
    if data.seed is None:data.seed=42
    if data.engine == "chatterbox" and "model_size" not in getattr(data,"model_fields_set",set()):
        data.model_size=None  # Qwen default must not leak into Chatterbox admission.
    return validate({'engine':data.engine,'profile_id':data.profile_id,'text':data.text,
                     'seed':data.seed,'language':data.language,'model_size':data.model_size,
                     'instruct':data.instruct,'personality':data.personality})

def preflight(sample):
    projected=sample['ct_current']+CB['predicted_increment_bytes']+CB['margin_bytes']
    return (projected<=14*2**30 and sample['host_available']>=10*2**30
            and sample['ct_psi_full_avg10']<5 and sample['ct_swap']<1792*2**20)

def stop_reason(sample,baseline):
    if sample.get('worker_current',0)>=CB['worker_stop_bytes']:return 'CHATTERBOX_WORKER_7_GIB'
    if sample['ct_current']>=14*2**30:return 'CT_MEMORY_14_GIB'
    if sample['ct_swap']-baseline['ct_swap']>128*2**20:return 'SWAP_GROWTH_128_MIB'
    if sample['ct_psi_full_avg10']>=5:return 'LOCAL_PSI_5_PERCENT'
    if sample['host_available']<4*2**30:return 'HOST_AVAILABLE_4_GIB'
    if sample['host_oom']>baseline['host_oom']:return 'HOST_OOM'
    if sample['ct_events']['oom']>baseline['ct_events']['oom'] or sample['ct_events']['oom_kill']>baseline['ct_events']['oom_kill']:return 'CT_OOM'
    if sample.get('worker_events',{}).get('oom',0) or sample.get('worker_events',{}).get('oom_kill',0):return 'WORKER_OOM'
    return None

def capabilities(heartbeat,now):
    fresh=heartbeat.get('status')=='healthy' and heartbeat.get('ct')==627 and 0<=now-heartbeat.get('timestamp',0)<8
    qwen=fresh and heartbeat.get('protocol')==WORKER_PROTOCOL and heartbeat.get('worker_source_sha256')==EXPECTED_WORKER_SHA256 and heartbeat.get('language_policy_sha256')==policy_fingerprint() and heartbeat.get('languages')==LANGUAGES
    cb=qwen and heartbeat.get('chatterbox',{}).get('ready') is True and heartbeat.get('chatterbox',{}).get('protocol')=='d085-cb-v1'
    return {'qwen':{'ready':bool(qwen),'languages':LANGUAGES,'model_sizes':['0.6B'],'max_chars':1200},
            'chatterbox':{'ready':bool(cb),'languages':LANGUAGES,'model_sizes':['default'],'max_chars':240,'experimental':True,'variant':'multilingual-v3'},
            'chatterbox_turbo':{'ready':False},'kokoro':{'ready':True},'piper':{'ready':True}}

"""Voicebox adapter: shared persistent queue, separate Chatterbox artifacts/runtime."""
import asyncio,hashlib,json,time,uuid
import soundfile as sf
from . import isolated_backend as qwen
from .engine_policy import validate,CB


def worker_health():
    h=qwen.worker_health();cb=h.get('chatterbox',{})
    if not cb.get('ready') or cb.get('protocol')!='d085-cb-v1':
        raise RuntimeError('Chatterbox aislado no está preparado; no se descargan ni cargan modelos automáticamente')
    return cb


class IsolatedChatterboxBackend(qwen.IsolatedQwenBackend):
    model_size='default';_current_model_size='default'
    def _get_model_path(self,size='default'):
        if size not in [None,'default']:raise ValueError('Solo Chatterbox Multilingual V3')
        return 'ResembleAI/chatterbox'
    def _is_model_cached(self,size='default'):
        self._get_model_path(size)
        try:worker_health();return True
        except Exception:return False
    async def load_model_async(self,size='default'):
        self._get_model_path(size);worker_health()
    async def load_model(self,size='default'):await self.load_model_async(size)
    # Reference verification is inherited unchanged: same original and transcript.
    async def generate(self,text,voice_prompt,language='es',seed=None,instruct=None):
        request=validate({'engine':'chatterbox','model_size':'default','profile_id':voice_prompt.get('profile_id'),
                          'text':text,'language':language,'seed':42 if seed is None else seed,'instruct':instruct})
        worker_health();parent=qwen.CONTEXT.get()
        if not parent:raise ValueError('Chatterbox requiere un trabajo persistente de Voicebox')
        path=qwen.ROOT/uuid.UUID(parent).hex
        if path.exists():
            raise ValueError('Este intento ya existe: conservar evidencias. Chatterbox no reanuda checkpoints Qwen; un reintento exige un nuevo intento explícito')
        path.mkdir(mode=0o700);(path/'text.txt').write_text(text);(path/'text.txt').chmod(0o600)
        qwen.atomic(path/'request.json',request);qwen.atomic(path/'state.json',{'status':'queued','engine':'chatterbox','created_at':time.time()})
        try:
            deadline=time.monotonic()+CB['timeout_seconds']+30
            while time.monotonic()<deadline:
                state=json.loads((path/'state.json').read_text())
                if state['status']=='completed':
                    wav=path/'chatterbox.wav'
                    if hashlib.sha256(wav.read_bytes()).hexdigest()!=state['wav_sha256']:raise ValueError('WAV checksum incorrecto')
                    return sf.read(wav,dtype='float32')
                if state['status'] in ['failed','cancelled']:raise RuntimeError(state.get('error',state['status']))
                worker_health();await asyncio.sleep(.3)
            raise TimeoutError('Chatterbox excedió300s; el trabajo se conserva')
        except BaseException:
            (path/'cancel.flag').touch(mode=0o600)
            async def reap():
                for _ in range(100):
                    state=json.loads((path/'state.json').read_text())
                    if state['status'] in ['completed','failed','cancelled']:return
                    await asyncio.sleep(.3)
                raise RuntimeError('Cancelación pendiente: no iniciar otro motor')
            await asyncio.shield(reap());raise

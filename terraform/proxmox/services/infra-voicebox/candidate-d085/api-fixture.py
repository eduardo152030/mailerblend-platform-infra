"""Run in candidate image, offline, no persistent binds. Real routes, fake execution."""
import asyncio,json,tempfile,types,sys
sys.path.insert(0,"/app")
from pathlib import Path
from unittest.mock import AsyncMock,Mock,patch
import torch,huggingface_hub,safetensors.torch
def forbidden(*args,**kwargs):raise AssertionError('No model load/download authorized in API fixture')
torch.load=forbidden;huggingface_hub.hf_hub_download=forbidden;safetensors.torch.load_file=forbidden
from backend import config
config.set_data_dir('/tmp/d085-api-data')
from backend import models
from backend.routes import generations as api
from backend.routes import models as model_api
from backend.backends import get_tts_backend_for_engine,TTS_ENGINES
from backend.backends import isolated_backend as qb,isolated_chatterbox_backend as cb
from fastapi import HTTPException
OWNER='1fd00418-2a79-4178-883f-af6c3f5e07ee'

async def main():
    checks=0;captured=[]
    assert 'piper' in TTS_ENGINES and 'kokoro' in TTS_ENGINES
    assert type(get_tts_backend_for_engine('qwen')).__name__=='IsolatedQwenBackend'
    assert type(get_tts_backend_for_engine('chatterbox')).__name__=='IsolatedChatterboxBackend'
    for engine in ['qwen','chatterbox']:
      for lang in ['es','en']:
        data=models.GenerationRequest(profile_id=OWNER,text='Texto de prueba.' if lang=='es' else 'Test text.',language=lang,engine=engine,effects_chain=[])
        create=AsyncMock(return_value=types.SimpleNamespace(id='fake',status='generating'))
        def run(**kwargs):captured.append(kwargs);return object()
        with patch.object(api.profiles,'get_profile',AsyncMock(return_value=types.SimpleNamespace())),patch.object(api.profiles,'validate_profile_engine'),patch.object(api.history,'create_generation',create),patch.object(api,'run_generation',new=run),patch.object(api,'enqueue_generation'),patch.object(api,'get_task_manager',return_value=Mock()),patch.object(cb,'worker_health',return_value={'ready':True}):
            result=await api.generate_speech(data,db=Mock())
        assert captured[-1]['engine']==engine and captured[-1]['language']==lang and captured[-1]['seed']==42
        assert create.await_args.kwargs['language']==lang;checks+=1
    # Admission must precede history creation when backend is not available.
    data=models.GenerationRequest(profile_id=OWNER,text='Test',language='en',engine='chatterbox',effects_chain=[])
    create=AsyncMock()
    with patch.object(api.profiles,'get_profile',AsyncMock(return_value=types.SimpleNamespace())),patch.object(api.history,'create_generation',create),patch.object(cb,'worker_health',side_effect=RuntimeError('not ready')):
        try:await api.generate_speech(data,db=Mock());raise AssertionError('Should reject')
        except HTTPException as exc:assert exc.status_code==409
    create.assert_not_awaited();checks+=1
    # Reject foreign profile/oversize/unsupported size without altering history.
    for change in [{'profile_id':'other'},{'text':'x'*241},{'model_size':'0.6B'}]:
        data=models.GenerationRequest(profile_id=change.get('profile_id',OWNER),text=change.get('text','Test'),language='en',engine='chatterbox',effects_chain=[],**({'model_size':change['model_size']} if 'model_size' in change else {}))
        with patch.object(api.profiles,'get_profile',AsyncMock(return_value=types.SimpleNamespace())),patch.object(api.history,'create_generation',create):
            try:await api.generate_speech(data,db=Mock());raise AssertionError('Should reject')
            except HTTPException as exc:assert exc.status_code==400
        checks+=1
    for engine in ['qwen','chatterbox']:
      for fn,status in [(api.retry_generation,'failed'),(api.regenerate_generation,'completed')]:
        gen=types.SimpleNamespace(engine=engine,status=status,error='retained',audio_path='retained.wav')
        db=Mock();db.query.return_value.filter_by.return_value.first.return_value=gen
        try:await fn('id',db=db);raise AssertionError('No automatic retry')
        except HTTPException as exc:assert exc.status_code==409
        db.commit.assert_not_called();assert gen.status==status and gen.audio_path=='retained.wav';checks+=1
    # Streaming bypass cannot create an untracked heavy inference.
    with patch.object(api.profiles,'get_profile',AsyncMock(return_value=types.SimpleNamespace())):
        data=models.GenerationRequest(profile_id=OWNER,text='Test',language='en',engine='chatterbox')
        try:await api.stream_speech(data,db=Mock());raise AssertionError('No streaming')
        except HTTPException as exc:assert exc.status_code==409
    checks+=1
    # Native download/delete must not touch Chatterbox isolated weights.
    with patch.object(cb,'worker_health',return_value={'ready':True}):
        out=await model_api.trigger_model_download(models.ModelDownloadRequest(model_name='chatterbox-tts'));assert 'message' in out
    try:await model_api.delete_model('chatterbox-tts');raise AssertionError('No delete')
    except HTTPException as exc:assert exc.status_code==409
    checks+=1
    from backend.utils.effects import BUILTIN_PRESETS,apply_effects,validate_effects_chain
    import numpy as np
    wanted={'Robotic','Radio','Echo Chamber','Deep Voice'}
    presets=[v for v in BUILTIN_PRESETS.values() if v['name'] in wanted];assert len(presets)==4
    effects_forwarded=0
    for engine in ['qwen','chatterbox']:
      for preset in presets:
        data=models.GenerationRequest(profile_id=OWNER,text='Test text.',language='en',engine=engine,effects_chain=[models.EffectConfig(**e) for e in preset['effects_chain']])
        create=AsyncMock(return_value=types.SimpleNamespace(id='fake',status='generating'))
        def run(**kwargs):captured.append(kwargs);return object()
        with patch.object(api.profiles,'get_profile',AsyncMock(return_value=types.SimpleNamespace())),patch.object(api.profiles,'validate_profile_engine'),patch.object(api.history,'create_generation',create),patch.object(api,'run_generation',new=run),patch.object(api,'enqueue_generation'),patch.object(api,'get_task_manager',return_value=Mock()),patch.object(cb,'worker_health',return_value={'ready':True}):
            await api.generate_speech(data,db=Mock())
        assert captured[-1]['effects_chain']==preset['effects_chain'];assert captured[-1]['profile_id']==OWNER
        effects_forwarded+=1
    x=(.15*np.sin(2*np.pi*220*np.arange(24000)/24000)+.05*np.sin(2*np.pi*440*np.arange(24000)/24000)).astype(np.float32);original=x.copy();dsp=[]
    for preset in presets:
        assert validate_effects_chain(preset['effects_chain']) is None
        y=apply_effects(x,24000,preset['effects_chain'])
        assert np.isfinite(y).all() and y.size>0 and not np.allclose(x,y)
        assert np.array_equal(x,original),'DSP must not modify the source array'
        dsp.append(preset['name'])
    from backend.database import session as database_session
    from backend.services import effects as effects_service
    database_session.init_db()
    with database_session.SessionLocal() as db:
        seeded=effects_service.list_presets(db);assert wanted.issubset({v.name for v in seeded})
    print(json.dumps({'api_checks':checks,'result':'PASS','model_generations':0,'history_simulated':True,'routes_from_candidate_image':True,'effects_forward_checks':effects_forwarded,'dsp_synthetic_pass':dsp,'builtin_presets_seeded_in_temporary_db':True}))
asyncio.run(main())

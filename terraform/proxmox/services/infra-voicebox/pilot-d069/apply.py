"""D069: recognize the actual owner's UUID while retaining reference guards."""
from pathlib import Path
p=Path('/app/backend/backends/pytorch_backend.py');s=p.read_text()
old='owner = db.query(VoiceProfile).filter(VoiceProfile.name == "Eduardo — Personal Voice").first()'
new='owner = db.query(VoiceProfile).filter(VoiceProfile.id == "1fd00418-2a79-4178-883f-af6c3f5e07ee", VoiceProfile.voice_type == "cloned").first()'
assert s.count(old)==1;s=s.replace(old,new)
old='                        raise ValueError("Real owner reference recordings required before loading Base")'
new=old+'''\n                    from .. import config\n                    refs = db.query(ProfileSample).filter(ProfileSample.profile_id == owner.id).all()\n                    if not all(r.reference_text.strip() and config.resolve_storage_path(r.audio_path) is not None and config.resolve_storage_path(r.audio_path).is_file() for r in refs):\n                        raise ValueError("Owner reference files and transcript required")\n                import os
                if os.environ.get("VOICEBOX_BASE_CPU_ENABLED", "0") != "1":
                    raise ValueError("Owner reference is valid; Base CPU requires a controlled pilot (D069)")
                torch.set_num_threads(2)'''
assert s.count(old)==1;s=s.replace(old,new)
old='            self.model.model.speech_tokenizer.model.float()'
new=old+'''\n            import functools, time\n            def trace(fn, stage):\n                @functools.wraps(fn)\n                def call(*args, **kwargs):\n                    start = time.monotonic()\n                    logger.info("D069 stage=%s event=start", stage)\n                    try:\n                        return fn(*args, **kwargs)\n                    finally:\n                        logger.info("D069 stage=%s event=end seconds=%.3f", stage, time.monotonic()-start)\n                return call\n            for obj, name, stage in [(self.model, "create_voice_clone_prompt", "reference_prompt"), (self.model, "generate_voice_clone", "clone"), (self.model.model, "generate", "tokens"), (self.model.model.speech_tokenizer, "encode", "reference_encode"), (self.model.model.speech_tokenizer, "decode", "codec_decode")]:\n                setattr(obj, name, trace(getattr(obj, name), stage))'''
assert s.count(old)==1;s=s.replace(old,new);p.write_text(s)

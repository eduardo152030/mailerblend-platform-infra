#!/usr/bin/env python3
"""Dentro del contenedor WebUI: solo claves explícitas no secretas."""
import asyncio,json
import open_webui.config
from open_webui.models.config import Config
keys=['ollama.enable','openai.enable','ui.default_locale','ui.default_models','ui.default_interface_settings','ui.enable_signup','web.search.enable','web.search.engine','web.search.searxng_query_url','web.search.result_count','web.search.concurrent_requests','rag.top_k','rag.embedding_engine','rag.embedding_model','rag.embedding_query_prefix','rag.embedding_content_prefix','audio.stt.engine','audio.stt.whisper_model','audio.tts.engine','task.follow_up.enable','task.tags.enable','task.title.enable','task.query.search.enable','task.query.retrieval.enable','task.autocomplete.enable','models.default_params','models.default_metadata']
async def main():print('IA_CONFIG_JSON='+json.dumps(await Config.get_many(*keys),ensure_ascii=False))
asyncio.run(main())

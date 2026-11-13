#!/usr/bin/env python3
"""Dentro del contenedor WebUI, fuera de servicio: limpia solo fixture técnica propia.
Usa los métodos internos versionados; el administrador real aún no existe.
"""
import asyncio,json,pathlib
from sqlalchemy import select,update
from open_webui.internal.db import get_async_db_context
from open_webui.models.auths import Auths
from open_webui.models.users import Users
from open_webui.models.models import Model
from open_webui.models.config import Config
async def main():
 data=json.loads(pathlib.Path('/app/backend/data/ia-validation-auth.json').read_text());id=data['id']
 user=await Users.get_user_by_id(id)
 assert user and user.email=='ia-chat-validation@example.com'
 async with get_async_db_context() as db:
  await db.execute(update(Model).where(Model.user_id==id).values(user_id='system'))
  await db.commit()
 assert await Auths.delete_auth_by_id(id)
 await Config.upsert({'ui.enable_signup':True})
 assert not await Users.get_user_by_id(id)
 assert await Users.get_num_users()==0
 pathlib.Path('/app/backend/data/ia-validation-auth.json').unlink()
 print('Fixture de usuario eliminada; cuenta del propietario pendiente')
asyncio.run(main())

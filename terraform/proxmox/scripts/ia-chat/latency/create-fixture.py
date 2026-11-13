#!/usr/bin/env python3
"""Dentro de WebUI vía docker exec: usuario admin efímero aislado; no toca usuarios reales."""
import asyncio,json,pathlib,secrets,sqlite3,urllib.request
from open_webui.models.auths import Auths,Auth
from open_webui.internal.db import get_async_db_context
import uuid
from open_webui.utils.auth import get_password_hash,create_token
from open_webui.models.users import Users
from datetime import timedelta
p=pathlib.Path('/app/backend/data/.ia-latency-auth.json')
async def main():
 if p.exists():print('Fixture existente');return
 db=sqlite3.connect('/app/backend/data/webui.db');dest=pathlib.Path('/app/backend/data/.ia-latency-before.db');
 if not dest.exists():
  backup=sqlite3.connect(dest);db.backup(backup);backup.close();dest.chmod(0o600)
 before=sqlite3.connect(dest).execute('select count(*) from user').fetchone()[0];email='ia-latency-validation@example.com'
 u=await Users.get_user_by_email(email)
 if u is None:u=await Auths.insert_new_auth(email,await get_password_hash(secrets.token_urlsafe(36)),'Prueba temporal de latencia',role='admin')
 assert u and u.role=='admin'
 auth=await Auths.get_auth_by_id(u.id)
 if auth is None:
  async with get_async_db_context() as db_session:
   db_session.add(Auth(id=u.id,email=email,password=await get_password_hash(secrets.token_urlsafe(36)),active=True,session_stamp=str(uuid.uuid4())))
   await db_session.commit()
  auth=await Auths.get_auth_by_id(u.id)
 token=create_token(data={'id':u.id,'typ':'session','session_stamp':auth.session_stamp},expires_delta=timedelta(hours=24))
 p.write_text(json.dumps({'id':u.id,'email':email,'token':token,'users_before':before}));p.chmod(0o600);print(json.dumps({'fixture_created':True,'real_users_preserved':before}))
asyncio.run(main())

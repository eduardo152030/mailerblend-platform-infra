#!/usr/bin/env python3
"""Dentro WebUI: borra solo nuestra fixture, conserva cuentas reales y configuración.
No abre registro ni restaura SQLite; elimina chats propios mediante API interna.
"""
import asyncio,json,pathlib,urllib.request,urllib.error
from open_webui.models.users import Users
from open_webui.models.auths import Auths
p=pathlib.Path('/app/backend/data/.ia-latency-auth.json')
async def main():
 a=json.loads(p.read_text());assert a['email']=='ia-latency-validation@example.com';u=await Users.get_user_by_id(a['id']);assert u and u.email==a['email']
 assert await Auths.delete_auth_by_id(u.id);assert not await Users.get_user_by_id(u.id);assert not await Auths.get_auth_by_id(u.id)
 assert await Users.get_num_users()>=a['users_before'],'Real users missing'
 req=urllib.request.Request('http://127.0.0.1:8080/api/v1/auths/',headers={'Authorization':'Bearer '+a['token']})
 try:urllib.request.urlopen(req);raise AssertionError('JWT still accepted')
 except urllib.error.HTTPError as e:assert e.code==401,e.code
 p.unlink()
 for label in ['baseline','after-a','after-b','after-c','after-d','after-e','after-e-cache-fix','after-e-swa-full','final','weekday','idle-final','web-search-final','qwen-final']:
  f=p.with_name('.ia-latency-'+label+'.json')
  if f.exists():f.unlink()
 print(json.dumps({'fixture_deleted':True,'old_token_status':401,'users_remaining':await Users.get_num_users(),'registration_unchanged':True,'real_users_preserved':True}))
asyncio.run(main())

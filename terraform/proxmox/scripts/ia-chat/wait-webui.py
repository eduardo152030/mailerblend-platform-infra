#!/usr/bin/env python3
import urllib.request,time
for _ in range(300):
 try:
  with urllib.request.urlopen('http://127.0.0.1:3000/health',timeout=2) as r:
   if r.status==200:print('WebUI health HTTP200');break
 except Exception:pass
 time.sleep(2)
else:raise SystemExit('WebUI no ready tras600s')

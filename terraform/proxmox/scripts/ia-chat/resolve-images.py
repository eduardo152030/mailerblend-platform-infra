#!/usr/bin/env python3
import urllib.request,json,pathlib,re,datetime
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
def get(url,headers={}):return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'infra-ia-chat',**headers}),timeout=60)
for registry,repo,tag in [('registry-1.docker.io','searxng/searxng',None),('ghcr.io','open-webui/open-webui','v0.13.3')]:
 auth='https://auth.docker.io/token?service=registry.docker.io&scope=repository:'+repo+':pull' if registry.startswith('registry-1') else 'https://ghcr.io/token?service=ghcr.io&scope=repository:'+repo+':pull'
 token=json.load(get(auth))['token'];headers={'Authorization':'Bearer '+token}
 if tag is None:
  tags=json.load(get('https://'+registry+'/v2/'+repo+'/tags/list?n=10000',headers))['tags'];dated=sorted(t for t in tags if re.match(r'2026\.11\.',t));tag=dated[-1] if dated else sorted(t for t in tags if re.match(r'\d{4}[.\-]',t))[-1]
 headers['Accept']='application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.list.v2+json, application/vnd.docker.distribution.manifest.v2+json'
 r=get('https://'+registry+'/v2/'+repo+'/manifests/'+tag,headers)
 out[repo]={'tag':tag,'digest':r.headers['Docker-Content-Digest'],'manifest':json.load(r)}
 print(repo,tag,out[repo]['digest'])
pathlib.Path('services/ia-local/images.lock.json').write_text(json.dumps(out,indent=2)+'\n')

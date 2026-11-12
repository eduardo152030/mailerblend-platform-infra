"""CT627: finish only the 44 approved cache IDs; explicit prevalidation, no broad prune."""
import json,sys,hashlib,subprocess,socket,http.client,re
EXPECTED='d2396813e51c98e171052f0bc8765c69476467db53b098d89727954474fc8b00'
raw=sys.stdin.read();assert hashlib.sha256(raw.encode()).hexdigest()==EXPECTED;m=json.loads(raw)
class C(http.client.HTTPConnection):
 def connect(self):self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(60);self.sock.connect('/var/run/docker.sock')
def state():
 c=C('localhost');c.request('GET','/system/df');r=c.getresponse();assert r.status==200;return json.loads(r.read())
before=state();cache={x['ID']:x for x in before['BuildCache']};ids=[]
for x in m['entries']:
 if x['kind']!='buildkit_cache_record':continue
 if x['identifier'] not in cache:continue
 v=cache[x['identifier']];assert not v['InUse'] and not v['Shared'] and v['Size']==x['allocated_bytes'];ids.append(x['identifier'])
assert len(ids)<=44
pattern='^('+'|'.join(re.escape(x) for x in sorted(ids))+')$'
# Only the ID allowlist is used; boolean field filters are presence selectors in this builder.
p=subprocess.run(['docker','buildx','prune','--filter','id~='+pattern,'--force','--verbose'],capture_output=True,text=True,timeout=120);assert p.returncode==0,p.stderr
after=state();remaining={x['ID'] for x in after['BuildCache']};assert {x['Id'] for x in before['Images']}=={x['Id'] for x in after['Images']}
print(json.dumps({'approved_manifest_sha256':EXPECTED,'attempted_ids':sorted(ids),'removed_ids':[x for x in ids if x not in remaining],'retained_ids':[x for x in ids if x in remaining],'images_preserved':True,'df_after':subprocess.check_output(['df','-B1','/'],text=True),'stdout':p.stdout,'stderr':p.stderr}))

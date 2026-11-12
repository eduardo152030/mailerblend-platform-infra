"""CT627: owner-approved D074 exact manifest only. No services/resources/images touched."""
import json,sys,hashlib,os,subprocess,shutil,re,stat,time,socket,http.client
from pathlib import Path
EXPECTED='d2396813e51c98e171052f0bc8765c69476467db53b098d89727954474fc8b00'
assert socket.gethostname()=='infra-voicebox'
request=json.load(sys.stdin);raw=request['manifest'].encode();assert hashlib.sha256(raw).hexdigest()==EXPECTED
m=json.loads(raw);assert m['entry_count']==len(m['entries'])==105 and m['target_ct']==627
assert request['offhost_revalidated'] is True
verified={x['name']:x for x in request['backup_pair_checks']};assert len(verified)==14 and all(x['status']=='IDENTICAL' or (x['status']=='IDENTICAL_EXCEPT_EMPTY_SQLITE_SIDECARS' and x.get('derived_sidecars_only') is True) for x in verified.values())
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def run(a):return subprocess.check_output(a,text=True,timeout=35)
class UnixConnection(http.client.HTTPConnection):
 def connect(self):self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(45);self.sock.connect('/var/run/docker.sock')
def diskapi():
 c=UnixConnection('localhost');c.request('GET','/system/df');r=c.getresponse();assert r.status==200;return json.loads(r.read())
def invariant():
 ids=run(['docker','ps','-aq']).split();cs=json.loads(run(['docker','inspect',*ids]));data={}
 for root in ['/srv/voicebox/data/profiles','/srv/voicebox/private-originals','/srv/voicebox/data/generations']:
  for p in Path(root).rglob('*'):
   if p.is_file():data[str(p)]=digest(p)
 api=diskapi()
 return {'containers':{x['Id']:{'image':x['Image'],'started':x['State']['StartedAt'],'restarts':x['RestartCount'],'health':x['State'].get('Health',{}).get('Status')} for x in cs},'image_ids':sorted(x['Id'] for x in api.get('Images',[])),'protected_audio_hashes':data}
state_before=invariant();df_before=run(['df','-B1','/']);print(json.dumps({'stage':'before','df':df_before,'manifest_sha256':EXPECTED,'protected_audio_count':len(state_before['protected_audio_hashes'])}),flush=True)
api=diskapi();cache={x['ID']:x for x in api.get('BuildCache',[])};ready=[];skips=[]
# Finish all validations before the first material removal.
for x in m['entries']:
 ident=x['identifier'];kind=x['kind']
 if kind=='buildkit_cache_record':
  cur=cache.get(ident)
  if not cur:skips.append({'identifier':ident,'reason':'already_absent'});continue
  if cur['Shared'] or cur['InUse'] or cur['Size']!=x['allocated_bytes']:skips.append({'identifier':ident,'reason':'cache_drift'});continue
  ready.append(x);continue
 p=Path(ident);assert p.is_absolute() and not p.is_symlink()
 if not p.exists():skips.append({'identifier':ident,'reason':'already_absent'});continue
 if kind=='expanded_backup_duplicate':
  assert p.parent==Path('/opt/voicebox/backups') and p.is_dir()
  v=verified[p.name];assert v['archive_sha256']==x['dependencies']['archive_sha256'] and (p/'manifest.json').is_file();assert digest(p/'manifest.json')==x['dependencies']['manifest_sha256']
 elif kind=='public_build_directory':assert ident=='/srv/voicebox/pilot-d072/build' and p.is_dir()
 else:
  assert p.is_file() and (ident.startswith('/var/cache/apt/') or ident.startswith('/var/lib/apt/lists/') or ident=='/srv/voicebox/pilot-d072/build.tar.gz')
  if p.stat().st_blocks*512!=x['allocated_bytes'] or p.stat().st_size!=x['apparent_bytes'] or (x.get('sha256') and digest(p)!=x['sha256']):skips.append({'identifier':ident,'reason':'file_drift'});continue
 ready.append(x)
comms=set(run(['ps','-eo','comm=']).split());assert not comms.intersection({'apt','apt-get','dpkg'}),'Package operation active'
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:
  if (proc/'comm').read_text().strip().startswith('unattended'):
   argv=(proc/'cmdline').read_bytes().split(b'\0')
   assert any(b'unattended-upgrade-shutdown' in a for a in argv) and b'--wait-for-signal' in argv,'Active unattended upgrade'
 except FileNotFoundError:pass
locks=subprocess.run(['fuser','/var/lib/dpkg/lock','/var/lib/dpkg/lock-frontend','/var/lib/apt/lists/lock','/var/cache/apt/archives/lock'],capture_output=True,text=True,timeout=10)
assert locks.returncode==1 and not locks.stdout.strip(),'Package lock in use'
print(json.dumps({'stage':'preflight','ready_count':len(ready),'skips':skips}),flush=True)
removed=[]
# Remove only paths in the approved allowlist. No wildcard expansion or Docker objects.
for x in ready:
 if x['kind']=='buildkit_cache_record':continue
 p=Path(x['identifier']);assert not p.is_symlink()
 if p.is_dir():shutil.rmtree(p)
 else:p.unlink()
 removed.append(x['identifier']);print(json.dumps({'stage':'removed_path','identifier':x['identifier']}),flush=True)
ids=sorted(x['identifier'] for x in ready if x['kind']=='buildkit_cache_record')
if ids:
 pattern='^('+'|'.join(re.escape(x) for x in ids)+')$'
 # Exact per-ID allowlist; never unfiltered builder/system prune. Docker owns layer GC.
 p=subprocess.run(['docker','buildx','prune','--filter','id~='+pattern,'--force','--verbose'],capture_output=True,text=True,timeout=120)
 print(json.dumps({'stage':'cache_prune','returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}),flush=True);assert p.returncode==0,'Selective cache removal failed'
after=diskapi();remaining={x['ID'] for x in after.get('BuildCache',[])};removed_cache=[x for x in ids if x not in remaining];retained=[x for x in ids if x in remaining]
state_after=invariant();assert state_after==state_before,'Protected container/image/audio invariant changed'
print(json.dumps({'stage':'result','manifest_sha256':EXPECTED,'removed_paths':removed,'removed_cache_ids':removed_cache,'retained_approved_cache_ids':retained,'skips':skips,'df_before':df_before,'df_after':run(['df','-B1','/']),'protected_invariants_preserved':True,'restart_or_resource_change':False}),flush=True)

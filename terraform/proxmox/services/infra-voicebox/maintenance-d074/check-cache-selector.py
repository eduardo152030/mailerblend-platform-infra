"""CT627 read-only check: exact BuildKit allowlist selector; never prune."""
import json,subprocess,re,sys
m=json.load(sys.stdin);ids={x['identifier'] for x in m['entries'] if x['kind']=='buildkit_cache_record'}
pattern='^('+'|'.join(re.escape(x) for x in sorted(ids))+')$'
r=subprocess.run(['docker','buildx','du','--filter','id~='+pattern,'--format','json'],capture_output=True,text=True,timeout=30);assert r.returncode==0,r.stderr
rows=[json.loads(x) for x in r.stdout.splitlines() if x.strip()];assert {x['ID'] for x in rows}==ids;assert all(x['Reclaimable'] and not x['Shared'] for x in rows)
print(json.dumps({'result':'PASS','selected_ids':sorted(ids),'selected_count':len(rows),'selector_exact_allowlist':True,'command_executed':'docker buildx du (read-only)','prune_executed':False}))

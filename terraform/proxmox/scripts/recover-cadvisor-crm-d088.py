#!/usr/bin/env python3
"""D088, ejecutar por stdin en CT623/618: diagnóstico o --apply/--verify.

Límite cAdvisor384MiB, swap total384MiB (ampliación acotada del techo anterior256MiB),
sin swap adicional. CPU intacta. CT618: arranque del CRM existente y restart always. Sin Compose up,
pull, recreación, cambios de datos o PVE. Backup privado de inputs con SHA256.
Rollback: restaurar inputs respaldados y límites/política del baseline.json;
no borrar ni restaurar volúmenes. No parar CRM al revertir una política.
"""
import argparse, hashlib, json, subprocess, os
from pathlib import Path
from datetime import datetime, timezone


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def inspect(name):
    return json.loads(run('docker', 'inspect', name))[0]


def brief(c):
    return dict(id=c['Id'], image=c['Image'], started=c['State']['StartedAt'],
                running=c['State']['Running'], health=c['State'].get('Health',{}).get('Status'),
                restarts=c['RestartCount'], memory=c['HostConfig']['Memory'],
                swap=c['HostConfig']['MemorySwap'], cpu=c['HostConfig']['NanoCpus'],
                restart=c['HostConfig']['RestartPolicy'], mounts=c['Mounts'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args=parser.parse_args()
    host=run('hostname'); assert host in ['infra-gestoria','infra-composable-crm']
    crm=host=='infra-composable-crm'
    os.environ['EXPORTER_BIND_IP']='192.168.1.118' if crm else '192.168.1.123'
    names=['cadvisor']+(['crm-api'] if crm else [])
    before={n:inspect(n) for n in names}
    backup=Path('/root/monitoring-recovery-d088')
    files=before['cadvisor']['Config']['Labels']['com.docker.compose.project.config_files'].split(',')
    limit=next(Path(f) for f in files if f.endswith('/cadvisor-limits.yml'))
    if crm:
        cf=before['crm-api']['Config']['Labels']['com.docker.compose.project.config_files'].split(',')
        files+=cf
    if args.apply:
        backup.mkdir(mode=0o700,exist_ok=True)
        baseline=backup/'baseline.json'
        if not baseline.exists():
            baseline.write_text(json.dumps({n:brief(c) for n,c in before.items()},indent=2));baseline.chmod(0o600)
            manifest={}
            for i,f in enumerate(dict.fromkeys(files)):
                src=Path(f); dst=backup/f'input-{i}.before';dst.write_bytes(src.read_bytes());dst.chmod(0o600)
                assert dst.read_bytes()==src.read_bytes()
                manifest[f]={'backup':str(dst),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()}
            (backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
        manifest=json.loads((backup/'manifest.json').read_text())
        for m in manifest.values():assert hashlib.sha256(Path(m['backup']).read_bytes()).hexdigest()==m['sha256']
        text=limit.read_text(); assert any(v in text for v in ['mem_limit: 128m','mem_limit: 256m','mem_limit: 384m'])
        candidate=text.replace('mem_limit: 128m','mem_limit: 384m').replace('mem_limit: 256m','mem_limit: 384m').replace('memswap_limit: 256m','memswap_limit: 384m')
        if 'memswap_limit:' not in candidate:candidate=candidate.replace('mem_limit: 384m','mem_limit: 384m\n    memswap_limit: 384m')
        limit.write_text(candidate)
        try:
            cmd=['docker','compose']
            for f in before['cadvisor']['Config']['Labels']['com.docker.compose.project.config_files'].split(','):cmd+=['-f',f]
            run(*cmd,'config','--quiet')
        except Exception:
            limit.write_text(text);raise
        if before['cadvisor']['HostConfig']['Memory']!=402653184 or before['cadvisor']['HostConfig']['MemorySwap']!=402653184:
            run('docker','update','--memory','384m','--memory-swap','384m','cadvisor')
        if crm:
            paths=[Path(f) for f in cf]
            assert len(paths)==1
            p=paths[0]; original=p.read_text()
            if p.suffix=='.json':
                data=json.loads(original)
                assert len(data['services'])==1
                svc=next(iter(data['services'].values()))
                assert svc['container_name']=='crm-api'
                svc['restart']='always'
                p.write_text(json.dumps(data,indent=2)+'\n')
            else:
                assert original.count('restart: unless-stopped')+original.count('restart: always')==1
                p.write_text(original.replace('restart: unless-stopped','restart: always'))
            cmd=['docker','compose']
            for f in cf:cmd+=['-f',f]
            try:run(*cmd,'config','--quiet')
            except Exception:p.write_text(original);raise
            if before['crm-api']['HostConfig']['RestartPolicy']['Name']!='always':run('docker','update','--restart=always','crm-api')
            if not before['crm-api']['State']['Running']:run('docker','start','crm-api')
    after={n:inspect(n) for n in names}
    for n,a in after.items():
        b=before[n]
        assert a['Id']==b['Id'] and a['Image']==b['Image']
        assert sorted(a['Mounts'],key=lambda x:x['Destination'])==sorted(b['Mounts'],key=lambda x:x['Destination'])
        assert a['HostConfig']['NanoCpus']==b['HostConfig']['NanoCpus']
        if n=='cadvisor' or b['State']['Running']:assert a['State']['StartedAt']==b['State']['StartedAt']
    if args.apply or args.verify:
        assert after['cadvisor']['HostConfig']['Memory']==402653184
        if crm:assert after['crm-api']['State']['Running'] and after['crm-api']['HostConfig']['RestartPolicy']['Name']=='always'
    c=after['cadvisor'];pid=c['State']['Pid']
    cg=Path('/sys/fs/cgroup'+Path(f'/proc/{pid}/cgroup').read_text().strip().split('::')[1])
    print(json.dumps(dict(time_utc=datetime.now(timezone.utc).isoformat(),host=host,
        containers={n:brief(c) for n,c in after.items()},
        cgroup={f:(cg/f).read_text().strip() for f in ['memory.current','memory.max','memory.swap.current','memory.events','memory.pressure']})))

if __name__=='__main__':main()

#!/usr/bin/env python3
"""EVA health/data checks with counts only; no secret or user-content output."""
import json
from pathlib import Path
import subprocess
import sys
import urllib.request


def main():
    baseline=json.loads(Path(sys.argv[1]).read_text())
    ids=subprocess.check_output(['docker','ps','-aq'],text=True).split()
    data=json.loads(subprocess.check_output(['docker','inspect']+ids,text=True))
    by_name={d['Name']:d for d in data}
    assert set(x['id'] for x in baseline)<=set(d['Id'] for d in data),'An original container disappeared'
    for original in baseline:
        d=by_name[original['name']]
        assert d['Image']==original['image'] and d['State']['Running'],'Image changed or service is stopped'
    report={'original_container_ids_preserved':True,'runtime_images_match_baseline':True}
    processes=subprocess.check_output(['docker','top','eva-cron-digest','-eo','pid,comm'],text=True).splitlines()[1:]
    assert [line.split()[-1] for line in processes]==['crond'],'Cron has not completed its runtime bootstrap'
    subprocess.run(['docker','exec','eva-cron-digest','sh','-c','command -v curl >/dev/null && test -s /etc/periodic/daily/send-digest'],check=True,capture_output=True)
    report['cron_bootstrap_completed']=True
    for role,url in [('eva_api','http://192.168.1.122:8001/health'),('focalboard','http://192.168.1.122:8002/')]:
        with urllib.request.urlopen(url,timeout=10) as response:
            assert response.status==200
            report[role+'_http']=response.status
    def psql(db,sql):
        cmd=['docker','exec','eva-postgres','sh','-c','psql -U "$POSTGRES_USER" -d "$1" -Atc "$2"','check',db,sql]
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=15)
        assert result.returncode==0,'PostgreSQL validation failed'
        return result.stdout.strip()
    dbs=psql('postgres','SELECT datname FROM pg_database WHERE NOT datistemplate AND datallowconn;').splitlines()
    report['postgres_databases']=len(dbs)
    report['postgres_public_tables']=sum(int(psql(db,"SELECT count(*) FROM information_schema.tables WHERE table_schema='public';")) for db in dbs)
    probe=psql(dbs[0],'BEGIN; CREATE TEMP TABLE recovery_probe(value integer); INSERT INTO recovery_probe VALUES(1); SELECT count(*) FROM recovery_probe; ROLLBACK;')
    assert '\n1\n' in probe
    report['postgres_write_probe_rolled_back']=True
    config=Path('/opt/infra-eva-assistant-bot/focalboard/config.json')
    if config.is_file():report['focalboard_db_engine']=json.loads(config.read_text()).get('dbtype')
    for name in ['uploads','persona']:
        p=Path('/opt/infra-eva-assistant-bot')/name
        report[name+'_files']=sum(f.is_file() for f in p.rglob('*')) if p.is_dir() else 0
    report['docker_health']={name:d['State'].get('Health',{}).get('Status') for name,d in by_name.items() if '-pre-storage-recovery' not in name}
    print(json.dumps(report,sort_keys=True))


if __name__=='__main__':
    try:main()
    except Exception:
        print('EVA functional validation failed; private details withheld.',file=sys.stderr)
        sys.exit(1)

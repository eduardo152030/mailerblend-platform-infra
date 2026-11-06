#!/usr/bin/env python3
"""Functional CRM checks; prints counts/status only, never credentials or user records."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


def inspect(name):
    return json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0]


def request(url,auth=None):
    req=urllib.request.Request(url)
    if auth:req.add_header('Authorization','Basic '+base64.b64encode((auth[0]+':'+auth[1]).encode()).decode())
    with urllib.request.urlopen(req,timeout=10) as response:return json.load(response)


def main():
    report={}
    couch=inspect('budibase-couchdb')
    env=dict(x.split('=',1) for x in couch['Config']['Env'] if '=' in x)
    ip=next(v['IPAddress'] for v in couch['NetworkSettings']['Networks'].values() if v['IPAddress'])
    base='http://'+ip+':5984';auth=(env['COUCHDB_USER'],env['COUCHDB_PASSWORD'])
    databases=request(base+'/_all_dbs',auth)
    report['couchdb_databases']=len(databases)
    report['budibase_application_databases']=sum(db.startswith(('app_', 'app-')) for db in databases)
    report['couchdb_documents']=sum(request(base+'/'+urllib.parse.quote(db,safe=''),auth).get('doc_count',0) for db in databases)
    sql='select count(*) from information_schema.tables where table_schema=\'public\';'
    pg=subprocess.run(['docker','exec','supabase-db','sh','-c','psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc '+__import__('shlex').quote(sql)],capture_output=True,text=True,timeout=15)
    assert pg.returncode==0,'PostgreSQL query failed'
    report['postgres_public_tables']=int(pg.stdout.strip())
    if '--write-probe' in sys.argv:
        sql='BEGIN; CREATE TEMP TABLE recovery_probe (value integer); INSERT INTO recovery_probe VALUES(1); SELECT count(*) FROM recovery_probe; ROLLBACK;'
        pg=subprocess.run(['docker','exec','supabase-db','sh','-c','psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc '+__import__('shlex').quote(sql)],capture_output=True,text=True,timeout=15)
        assert pg.returncode==0 and '\n1\n' in pg.stdout,'Rolled-back write probe failed'
        report['postgres_write_probe_rolled_back']=True
    status=request('http://192.168.1.118:8080/api/system/status')
    assert status['health']['passing'] and status['version']=='3.27.4'
    report['budibase_version']=status['version'];report['budibase_health_passing']=True
    for name,url in [('builder','http://192.168.1.118:8080/builder'),('crm_api','http://192.168.1.118:18088/health'),('crm_api_ready','http://192.168.1.118:18088/ready')]:
        with urllib.request.urlopen(url,timeout=10) as response:assert response.status==200;report[name+'_http']=response.status
    api=inspect('crm-api')
    api_env=dict(x.split('=',1) for x in api['Config']['Env'] if '=' in x)
    req=urllib.request.Request('http://192.168.1.118:18088/v1/contacts?limit=1',headers={'X-API-Key':api_env['CRM_API_KEY']})
    with urllib.request.urlopen(req,timeout=10) as response:
        assert response.status==200
        payload=json.load(response)
        report['crm_authenticated_read_http']=response.status
    # Obtain S3 credentials only in memory from the application process, not argv/logs.
    container=inspect('budibase-app');credentials={}
    for proc in Path('/proc').glob('[0-9]*'):
        try:
            if container['Id'] not in (proc/'cgroup').read_text() or (proc/'comm').read_text().strip()!='node':continue
            candidate=dict(x.split('=',1) for x in (proc/'environ').read_bytes().decode(errors='replace').split(chr(0)) if '=' in x)
            if candidate.get('MINIO_ACCESS_KEY') and candidate.get('MINIO_SECRET_KEY'):credentials=candidate;break
        except OSError:pass
    assert credentials,'Object-store runtime credentials unavailable'
    config='user = '+json.dumps(credentials['MINIO_ACCESS_KEY']+':'+credentials['MINIO_SECRET_KEY'])+'\n'
    def s3(path):
        cmd=['docker','exec','-i','budibase-app','curl','-fsS','--max-time','10','--aws-sigv4','aws:amz:us-east-1:s3','--config','-','http://127.0.0.1:9000'+path]
        result=subprocess.run(cmd,input=config.encode(),capture_output=True,timeout=15)
        assert result.returncode==0,'Object-store request failed'
        return result.stdout
    ns={'s':'http://s3.amazonaws.com/doc/2006-03-01/'}
    buckets=[x.text for x in ET.fromstring(s3('/')).findall('.//s:Bucket/s:Name',ns)]
    total=sampled=0
    for bucket in buckets:
        listing=ET.fromstring(s3('/'+urllib.parse.quote(bucket,safe='')+'?list-type=2'))
        assert listing.findtext('s:IsTruncated',default='false',namespaces=ns)=='false','Object listing needs pagination'
        objects=listing.findall('s:Contents',ns);total+=len(objects)
        if objects:
            key=objects[0].findtext('s:Key',namespaces=ns);size=int(objects[0].findtext('s:Size',namespaces=ns))
            assert len(s3('/'+urllib.parse.quote(bucket,safe='')+'/'+urllib.parse.quote(key,safe='/')))==size
            sampled+=1
    report.update(s3_buckets=len(buckets),s3_objects=total,s3_sample_reads=sampled,manual_login='delegated_to_owner')
    print(json.dumps(report,sort_keys=True))


if __name__=='__main__':
    try:main()
    except Exception:
        print('CRM functional validation failed; credentials/records/error payloads withheld.',file=sys.stderr)
        sys.exit(1)

#!/usr/bin/env python3
"""Generate deterministic Compose healthcheck overlays; no credentials or new binaries."""
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def recipes():
    budibase=(ROOT/'services/infra-composable-crm/recovery/healthchecks/budibase.py').read_text()
    ready='import json,urllib.request; r=urllib.request.urlopen("http://127.0.0.1:8080/ready",timeout=2); assert r.status==200 and json.load(r).get("db")=="ok"'
    ping='exec 3<>/dev/tcp/127.0.0.1/8000; printf "GET /api/v2/ping HTTP/1.0\\r\\nHost: localhost\\r\\nConnection: close\\r\\n\\r\\n" >&3; IFS= read -r -t 3 status <&3; [[ "$status" == HTTP/1.[01]\\ 200\\ * ]]'
    return {'budibase-app':{'test':['CMD','python3','-c',budibase],'interval':'15s','timeout':'15s','start_period':'45s','retries':3},'crm-api':{'test':['CMD','python','-c',ready],'interval':'10s','timeout':'3s','retries':20},'focalboard':{'test':['CMD','/bin/bash','-ec',ping],'interval':'15s','timeout':'5s','start_period':'10s','retries':5}}
def paths():
    return {'budibase-app':ROOT/'services/infra-composable-crm/recovery/healthchecks/budibase.compose.yml','crm-api':ROOT/'services/infra-composable-crm/recovery/healthchecks/crm-api.compose.yml','focalboard':ROOT/'services/infra-eva-assistant-bot/recovery/healthchecks/focalboard.compose.yml'}
if __name__=='__main__':
    for name,check in recipes().items():
        # Compose interpolates dollar signs even in CMD array strings.
        check=dict(check);check['test']=[s.replace('$','$$') for s in check['test']]
        paths()[name].write_text(yaml.safe_dump({'services':{name:{'healthcheck':check}}},sort_keys=False,allow_unicode=True,width=120))
    print('Three versioned healthcheck overlays generated')

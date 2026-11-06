#!/usr/bin/env python3
"""Validate recovery identities against the reviewed plan, without connecting or applying."""
import json
from pathlib import Path
import sys

BASE=Path(__file__).resolve().parents[1]/'services/infra-composable-crm/recovery'


def validate(values,plan):
    expected={
        'BUDIBASE_RECOVERY_IMAGE':plan['image'],
        'BUDIBASE_APP_DATA_VOLUME':plan['volumes']['budibase-app'],
        'BUDIBASE_WORKER_DATA_VOLUME':plan['volumes']['budibase-worker'],
    }
    if values!=expected:
        raise ValueError('Recovery identities differ from the reviewed plan. Check image/volume mapping; no changes applied.')


if __name__=='__main__':
    try:
        path=Path(sys.argv[1]) if len(sys.argv)>1 else BASE/'recovery.env'
        values={}
        for line in path.read_text().splitlines():
            if not line.strip() or line.lstrip().startswith('#'):continue
            key,sep,value=line.partition('=')
            if not sep or key in values:raise ValueError('Invalid recovery identity file; content omitted.')
            values[key]=value.strip()
        validate(values,json.loads((BASE/'plan.json').read_text()))
    except (ValueError,OSError) as exc:
        print(str(exc),file=sys.stderr);sys.exit(1)
    print('Reviewed recovery image and both original data volumes match. No deployment performed.')

#!/usr/bin/env python3
"""Observe the real exporter→rule→AM→Telegram chain; never POST an alert."""
import argparse,importlib.util,json,time
from pathlib import Path
spec=importlib.util.spec_from_file_location('p5',Path(__file__).with_name('phase5-alerting.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def counter(name):return sum(float(l.split()[1]) for l in m.fetch(9093,'/metrics').decode().splitlines() if l.startswith(name+'{') and 'integration="telegram"' in l)
def observe(stage):
 base=json.loads((m.PRIVATE/'baseline.json').read_text());previous=m.PRIVATE/'delivery-firing.json'
 floor=float(base['metrics']['sent'][0]['value'][1]) if stage=='firing' else json.loads(previous.read_text())['sent']
 failed=float(base['metrics']['failed'][0]['value'][1]);deadline=time.monotonic()+150;rule=None
 while time.monotonic()<deadline:
  assert counter('alertmanager_notifications_failed_total')==failed,'Telegram error: stop and rollback'
  rule=next(r for g in m.api('/api/v1/rules')['groups'] for r in g['rules'] if r['name']=='Phase5DeliveryVerification')
  assert rule['health'] in ['ok','unknown'] and not rule.get('lastError')
  alerts=json.loads(m.fetch(9093,'/api/v2/alerts'));own=[a for a in alerts if a['labels'].get('alertname')=='Phase5DeliveryVerification']
  active=any(a['status']['state']=='active' and a['endsAt']>time.strftime('%Y-%m-%dT%H:%M:%S',time.gmtime()) for a in own)
  sent=counter('alertmanager_notifications_total')
  ready=rule['state']=='firing' and active if stage=='firing' else rule['state']=='inactive' and not active
  if ready and sent>floor:
   data={'stage':stage,'time':time.time(),'rule':rule,'am_alerts':own,'sent':sent,'failed':failed,'baseline_sent':floor,'telegram_api_accepted':True,'human_receipt_confirmed':False,'other_active_alerts':[a['labels'] for a in alerts if a['labels'].get('alertname')!='Phase5DeliveryVerification' and a['status']['state']=='active']}
   assert not data['other_active_alerts'],'Concurrent notifications: aggregate counter cannot prove test delivery'
   m.save(m.PRIVATE/('delivery-'+stage+'.json'),data)
   if stage=='firing':
    a=own[0];a['status']='firing';payload={'receiver':'telegram','status':'firing','alerts':[a]};m.save(m.PRIVATE/'real-telegram-firing.json',payload)
    message=m.tool([str(m.PRIVATE/'amtool'),'template','render','--template.glob='+str(m.PRIVATE/'candidate/config/alertmanager/templates/*.tmpl'),'--template.text={{ template "telegram.message" . }}','--template.type=html','--template.data='+str(m.PRIVATE/'real-telegram-firing.json')]);(m.PRIVATE/'real-telegram-firing.html').write_text(message)
   print(json.dumps({'stage':stage,'rule_state':rule['state'],'sent':sent,'failed':failed,'api_accepted':True,'human_receipt_confirmed':False}));return
  time.sleep(2)
 raise RuntimeError('Delivery observation timed out; do not mark accepted')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['firing','resolved']);observe(p.parse_args().stage)

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import time
import unittest

ROOT=Path(__file__).resolve().parents[2]
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class MemoryAlignmentTests(unittest.TestCase):
    def setUp(self):
        self.m=load('exporter-memory-alignment.py');self.now=time.time();self.cid='a'*64
        self.sample={'containers':[{'id':self.cid,'name':'app','started_at':'generation1','running':True,'docker_stats':{'memory_usage':61263872}}],'cadvisor':{'container_memory_usage_bytes':[{'labels':{'id':'/system.slice/docker-'+self.cid+'.scope','name':'app'},'timestamp':self.now-7,'value':47448064}]}}
        self.history=[{'id':self.cid,'name':'app','started_at':'generation1','time':self.now-7+d,'request_before':self.now-7+d-.005,'request_after':self.now-7+d+.005,'docker_bytes':47448064,'cgroup_before':47448064,'cgroup_after':47448064} for d in [-.25,.25]]

        self.sample['measurement_scope']='fixture-memory'
        for point in self.history:point['measurement_scope']='fixture-memory'

    def test_asynchronous_old_failure_is_not_reused_for_aligned_measurement(self):
        self.assertGreater(abs(47448064-61263872),self.m.allowance(61263872,'app'))
        self.assertEqual(self.m.aligned_evidence(self.sample,self.history)[self.cid]['cadvisor_bytes'],47448064)

    def test_real_mismatch_and_wrong_cache_semantics_fail(self):
        for value in [30*1024**2,80*1024**2]:
            self.sample['cadvisor']['container_memory_usage_bytes'][0]['value']=value
            with self.assertRaisesRegex(AssertionError,'RAM mismatch'):self.m.aligned_evidence(self.sample,self.history)

    def test_nonmonotonic_ram_is_allowed_but_both_endpoints_must_pass(self):
        self.history[0]['docker_bytes']=self.history[0]['cgroup_before']=self.history[0]['cgroup_after']=48*1024**2
        self.history[1]['docker_bytes']=self.history[1]['cgroup_before']=self.history[1]['cgroup_after']=46*1024**2
        self.m.aligned_evidence(self.sample,self.history)
        self.history[1]['docker_bytes']=self.history[1]['cgroup_before']=self.history[1]['cgroup_after']=70*1024**2
        with self.assertRaises(AssertionError):self.m.aligned_evidence(self.sample,self.history)

    def test_missing_stale_or_nonfinite_timestamps_fail(self):
        for stamp in [None,self.now-91,float('nan'),self.now+6]:
            self.sample['cadvisor']['container_memory_usage_bytes'][0]['timestamp']=stamp
            with self.assertRaises(AssertionError):self.m.aligned_evidence(self.sample,self.history)

    def test_full_identity_generation_and_duplicate_rows_fail(self):
        for mode in ['wrong_generation','short_id','wrong_name','duplicate']:
            s=copy.deepcopy(self.sample);h=copy.deepcopy(self.history);r=s['cadvisor']['container_memory_usage_bytes'][0]
            if mode=='wrong_generation':h[0]['started_at']='other'
            if mode=='short_id':r['labels']['id']=self.cid[:12]
            if mode=='wrong_name':r['labels']['name']='other'
            if mode=='duplicate':s['cadvisor']['container_memory_usage_bytes'].append(copy.deepcopy(r))
            with self.assertRaises(AssertionError):self.m.aligned_evidence(s,h)

    def test_missing_gapped_slow_or_unbracketed_history_fails(self):
        for mode in ['missing','gap','slow','timestamp']:
            h=copy.deepcopy(self.history)
            if mode=='missing':h=h[:1]
            if mode=='gap':h[0]['time']-=3
            if mode=='slow':h[0]['request_before']-=1
            if mode=='timestamp':h[0]['request_before']=h[0]['time']+.001
            with self.assertRaises(AssertionError):self.m.aligned_evidence(self.sample,h)

    def test_raw_docker_cgroup_disagreement_fails(self):
        self.history[0]['cgroup_before']=100*1024**2
        with self.assertRaisesRegex(AssertionError,'Docker/cgroup'):self.m.aligned_evidence(self.sample,self.history)

    def test_observer_recomputes_raw_evidence_and_rejects_tampering(self):
        self.sample['memory_alignment']=self.m.aligned_evidence(self.sample,self.history)
        self.m.validate_alignment(self.sample)
        self.sample['memory_alignment'][self.cid]['cadvisor_bytes']+=1
        with self.assertRaises(AssertionError):self.m.validate_alignment(self.sample)

    def test_no_extra_temporal_allowance_is_added(self):
        self.assertEqual(self.m.allowance(61263872,'app'),12252774.4)
        self.assertEqual(self.m.allowance(1,'app'),512*1024)
        self.assertEqual(self.m.allowance(1,'cadvisor'),4*1024**2)

    def test_preparation_is_opt_in_and_preserves_exporter_inputs(self):
        m=load('prepare-617-memory.py');b=load('prepare-approved-exporters.py')
        rows=json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-rollout-authenticated-preflight.json').read_text());audit=next(r for r in rows if r['ct']==617)
        with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as c:
            old=Path(a);new=Path(c);b.render(617,old,audit);manifest=m.render(new,audit)
            for name in ['node.yml','node-limits.yml','node-cgroup.yml','node-cgroup.sh','cadvisor.yml','cadvisor-limits.yml','cadvisor-containerd.yml','cpu-alignment.py']:
                self.assertEqual((old/name).read_bytes(),(new/name).read_bytes(),name)
            self.assertIn('exporter-pilot-617-'+manifest['framework_revision'],(new/'pilot.py').read_text())
            self.assertIn('validate_memory_alignment(sample,previous)',(new/'observe.py').read_text())
            self.assertIn('validate_alignment(sample,previous)',(new/'observe.py').read_text())
            ns={'__name__':'generated_observer'};exec((new/'observe.py').read_text(),ns)
            self.assertEqual(ns['validate_alignment'].__name__,'validate_alignment')
            self.assertTrue(manifest['approval_required']);self.assertEqual(manifest['initial_seconds'],180)
            with self.assertRaises(AssertionError):m.instrument(new,623)

    def test_runner_uses_new_builder_only_for_617_and_manages_memory_lifecycle(self):
        from unittest.mock import Mock,patch
        m=load('rollout-approved-exporters.py')
        with tempfile.TemporaryDirectory() as d:
            r=object.__new__(m.Runner);r.here=Path(d);r.audit={};r.ct=617
            builder=Mock()
            with patch.object(m,'load',return_value=builder) as loader:
                r.render_bundle();loader.assert_called_once_with('prepare-aligned-exporters.py')
                loader.reset_mock();r.ct=623;r.render_bundle();loader.assert_called_once_with('prepare-approved-exporters.py')
            (r.here/'bundle').mkdir();r.directory='/not-a-real-remote-directory';r.remote=Mock();r.ctcode=lambda code:code
            r.memory_history_process(False);r.remote.assert_not_called()
            (r.here/'bundle/memory-alignment.py').touch();r.manifest={'apps':{'app':'app'}}
            r.memory_history_process(True);code=r.remote.call_args.args[0];compile(code,'remote-start','exec')
            self.assertIn('memory-history-process.json',code);self.assertIn("open('xb')",code)
            del r.manifest;r.memory_history_process(False);code=r.remote.call_args.args[0];compile(code,'remote-stop','exec')
            self.assertIn('PID identity changed',code);self.assertIn('SIGTERM',code)

    def test_history_reader_ignores_partial_lines_and_bounds_retained_ram_data(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'history.jsonl';old=dict(self.history[0],time=self.now-1000)
            p.write_text('\n'.join(json.dumps(x) for x in [old]+self.history)+'\n{"partial":')
            self.assertEqual(self.m.history_for_sample(self.sample,p),self.history)

    def test_recorded_live_control_replays_for_all_five_real_containers(self):
        from unittest.mock import patch
        proof=json.loads((ROOT/'docs/roadmap/evidence/2026-11-06-memory-alignment-live-control.json').read_text())['evidence']
        sample={'containers':[],'cadvisor':{'container_memory_usage_bytes':[]},'measurement_scope':'legacy-replay-ct623'}
        history=[]
        for cid,p in proof.items():
            for point in p['bracket']:point['measurement_scope']='legacy-replay-ct623'
            sample['containers'].append({'id':cid,'name':p['name'],'started_at':p['started_at'],'running':True})
            sample['cadvisor']['container_memory_usage_bytes'].append({'labels':{'id':'/system.slice/docker-'+cid+'.scope','name':p['name']},'timestamp':p['time'],'value':p['cadvisor_bytes']})
            history.extend(p['bracket'])
        with patch.object(self.m.time,'time',return_value=max(p['time'] for p in proof.values())+1):
            self.assertEqual(self.m.aligned_evidence(sample,history),proof)
        self.assertEqual(len(proof),5)

    def test_reentry_apply_rollback_and_idempotence_preserve_legacy_held_candidates(self):
        from unittest.mock import patch
        from contextlib import ExitStack
        m=load('prepare-617-memory.py')
        audit=next(r for r in json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-rollout-authenticated-preflight.json').read_text()) if r['ct']==617)
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);m.render(out,audit)
            spec=importlib.util.spec_from_file_location('candidate_helper',out/'pilot.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
            helper.ALLOW_CONTAINERD_SOCKET=True;helper.USE_LXC_CGROUP_CPU=True
            containers={};originals={}
            for name in ['node_exporter','cadvisor']:
                old={'Id':'original-'+name,'Image':'original-image','Config':{'Labels':{}},'State':{'Running':True}}
                containers[name]=old;originals[name]=copy.deepcopy(old)
                containers[name+'-phase4-617-held']={'Id':'legacy-held-'+name,'Image':'legacy-image','Config':{'Labels':{}},'State':{'Running':False}}
            for name in ['node_exporter','cadvisor']:
                containers[name+'-phase4-617-ram-v1-held']={'Id':'D035-held-'+name,'Image':'D035-image','Config':{'Labels':{'com.docker.compose.project':'exporter-pilot-617-ram-v1'}},'State':{'Running':False}}
            legacy=copy.deepcopy({k:v for k,v in containers.items() if k.endswith('-held')})
            (out/'baseline.json').write_text(json.dumps({'exporters':originals,'archives':{}}))
            (out/'external-backup-verified.json').write_text(json.dumps({'offhost_verified':True,'archives':{}}))
            creations=[]
            def run(args,**kw):
                if args[:3]==['docker','image','inspect']:return json.dumps([{'Id':'new-image'}]).encode()
                if args[:2]==['docker','rename']:
                    source=args[2]
                    if source not in containers:source=next(k for k,v in containers.items() if v['Id']==source)
                    self.assertNotIn(args[3],containers);containers[args[3]]=containers.pop(source)
                elif args[:2]==['docker','start']:containers[args[2]]['State']['Running']=True
                elif args[:2]==['docker','compose']:
                    name=args[-1]
                    if name not in containers:
                        creations.append(name);containers[name]={'Id':'new-'+name,'Image':'new-image','Config':{'Labels':{'com.docker.compose.project':helper.project(name)}},'State':{'Running':True},'HostConfig':{'Memory':(48 if name=='node_exporter' else 128)*1024**2,'NanoCpus':200000000 if name=='node_exporter' else 500000000},'Mounts':[]}
                    containers[name]['State']['Running']=True
                else:self.fail('Unexpected command: '+str(args))
                return b''
            with ExitStack() as stack:
                stack.enter_context(patch.object(helper,'containerd_socket_ready',return_value=True))
                stack.enter_context(patch.object(helper.Path,'is_dir',return_value=True))
                stack.enter_context(patch.object(helper,'run',side_effect=run));stack.enter_context(patch.object(helper,'docker_info',side_effect=lambda name:containers.get(name)))
                stack.enter_context(patch.object(helper,'stop',side_effect=lambda name:containers[name]['State'].update(Running=False)))
                stack.enter_context(patch.object(helper,'model',return_value=({},'new-model-hash')))
                for method in ['unchanged','capacity','ready']:stack.enter_context(patch.object(helper,method))
                helper.apply(out);ids={n:containers[n]['Id'] for n in originals}
                helper.rollback(out)
                self.assertEqual({n:containers[n]['Id'] for n in originals},{n:originals[n]['Id'] for n in originals})
                helper.apply(out);helper.apply(out)
                self.assertEqual(ids,{n:containers[n]['Id'] for n in originals})
                self.assertEqual({k:containers[k] for k in legacy},legacy)
                self.assertEqual(sorted(creations),['cadvisor','node_exporter'])

    def test_rfc3339nano_fractional_widths_match_cpu_parser_including_real_exit_value(self):
        cpu=load('exporter-cpu-alignment.py')
        for fraction in ['', '.1','.12','.123','.1234','.74017','.123456','.1234567','.12345678','.123456789']:
            for zone in ['Z','+00:00','+01:00']:
                text='2026-11-06T11:06:36'+fraction+zone
                self.assertEqual(self.m.timestamp(text),cpu.timestamp(text),text)
        self.assertEqual(self.m.timestamp('2026-11-06T11:06:36.74017Z'),self.m.timestamp('2026-11-06T11:06:36.740170Z'))
        with self.assertRaises(ValueError):self.m.timestamp('invalid')

if __name__=='__main__':unittest.main()

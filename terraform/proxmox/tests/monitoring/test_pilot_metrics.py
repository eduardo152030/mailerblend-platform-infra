"""Metric parser/identity guards: explicit timestamps must never become RAM/CPU values."""
import importlib.util
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('sample',ROOT/'scripts/sample-exporter-pilot-624.py')
sample=importlib.util.module_from_spec(spec)
with patch.object(socket,'gethostname',return_value='infra-journal-web'):
    spec.loader.exec_module(sample)


class MetricTests(unittest.TestCase):
    def test_explicit_prometheus_timestamp_is_not_the_metric_value(self):
        text='container_memory_usage_bytes{name="web",id="/docker-id"} 1675264 1793633981033\n'
        self.assertEqual(sample.rows(text,'container_memory_usage_bytes')[0]['value'],1675264)

    def test_cpu_value_and_identity_survive_timestamp_and_label_order(self):
        text='container_cpu_usage_seconds_total{cpu="total",name="web",container_label_com_docker_compose_service="web"} 3.647206 1793633981033\n'
        row=sample.rows(text,'container_cpu_usage_seconds_total')[0]
        self.assertEqual(row['value'],3.647206)
        self.assertEqual(row['labels']['container_label_com_docker_compose_service'],'web')

    def test_non_timestamped_node_memory_works(self):
        self.assertEqual(sample.rows('node_memory_MemTotal_bytes 5.36870912e+08\n','node_memory_MemTotal_bytes')[0]['value'],536870912)

    def test_other_metric_names_and_sensitive_labels_are_not_forwarded(self):
        text='container_memory_usage_bytes_extra{name="web"} 2\ncontainer_memory_usage_bytes{name="web",password="sentinel"} 1\n'
        rows=sample.rows(text,'container_memory_usage_bytes')
        self.assertEqual(len(rows),1)
        self.assertNotIn('password',rows[0]['labels'])



class AuditCollectorContractTests(unittest.TestCase):
    def test_lan_binding_and_node_endpoint_key_survive_cgroup_parsing(self):
        import ast
        import re
        import time
        import urllib.request
        from unittest.mock import patch
        module=ast.parse((ROOT/'scripts/audit-monitoring-runtime.py').read_text())
        collector=next(a.value.value for a in module.body if isinstance(a,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='collector' for t in a.targets))
        tree=ast.parse(collector)
        loop=next(n for n in tree.body if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple) and [x.id for x in n.target.elts]==['port','key'])
        node='node_memory_MemTotal_bytes 536870912\nlxc_cpu_capacity_cores{ct_id="624"} 1\nlxc_cpu_collector_success{ct_id="624"} 1\nlxc_cpu_collector_timestamp_seconds{ct_id="624"} 1000\nlxc_cpu_usage_seconds_total{ct_id="624"} 10\n'
        cad='container_memory_usage_bytes{name="web"} 1 1000000\ncontainer_cpu_usage_seconds_total{name="web"} 2 1000000\n'
        calls=[]
        class Response:
            def __init__(self,text):self.text=text
            def read(self):return self.text.encode()
        def open_url(url,timeout):
            calls.append(url)
            return Response(node if ':9100/' in url else cad)
        namespace={'r':{},'address':'192.0.2.124','urllib':__import__('urllib'),'re':re,'time':time}
        with patch.object(urllib.request,'urlopen',side_effect=open_url),patch.object(time,'time',return_value=1001):
            exec(compile(ast.Module(body=[loop],type_ignores=[]),'<audit-metrics>','exec'),namespace)
        self.assertEqual(set(namespace['r']),{'node_endpoint','cadvisor_endpoint'})
        self.assertEqual(namespace['r']['node_endpoint']['cpu_count'],1)
        self.assertEqual(namespace['r']['node_endpoint']['cpu_collector_age_seconds'],1)
        self.assertTrue(all('192.0.2.124' in url for url in calls))


if __name__=='__main__':unittest.main()

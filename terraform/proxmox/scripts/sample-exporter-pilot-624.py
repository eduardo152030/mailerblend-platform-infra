#!/usr/bin/env python3
"""Read-only, sanitized pilot sample inside CT 624 (no application data or environment)."""
import hashlib
import http.client
import json
from pathlib import Path
import re
import socket
import subprocess
import time
import urllib.request

assert socket.gethostname() == 'infra-journal-web'
IP='192.168.1.124'


def fetch(url):
    with urllib.request.urlopen(url,timeout=8) as r:
        assert r.status==200
        return r.read()


def rows(text,metric):
    out=[]
    for line in text.splitlines():
        if not line.startswith(metric+'{') and not line.startswith(metric+' '):continue
        labels=dict(re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)="([^"\n]*)"',line))
        try:
            tail=line[line.rfind('}')+1:] if line.startswith(metric+'{') else line[len(metric):]
            value=float(tail.split()[0])
        except ValueError:continue
        allowed=['name','id','image','cpu','mode','fstype','mountpoint','container_label_com_docker_compose_project','container_label_com_docker_compose_service','version','cadvisorVersion','dockerVersion','kernelVersion','osVersion','ct_id','resource_scope','cpu_source']
        out.append({'labels':{k:v for k,v in labels.items() if k in allowed},'value':value})
    return out


class Docker(http.client.HTTPConnection):
    def connect(self):
        self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        self.sock.settimeout(8);self.sock.connect('/var/run/docker.sock')


def api(path):
    conn=Docker('localhost');conn.request('GET',path);r=conn.getresponse()
    assert r.status==200
    data=json.loads(r.read());conn.close();return data


if __name__=='__main__':
    out={'time':time.time(),'ct':624}
    ids=subprocess.check_output(['docker','ps','-aq'],text=True).split()
    containers=json.loads(subprocess.check_output(['docker','inspect']+ids))
    out['containers']=[]
    for c in containers:
        item={'name':c['Name'].lstrip('/'),'id':c['Id'],'image':c['Image'],'running':c['State']['Running'],
              'started_at':c['State']['StartedAt'],'restarts':c['RestartCount'],'oom_killed':c['State']['OOMKilled'],
              'memory_limit':c['HostConfig']['Memory'],'nano_cpus':c['HostConfig']['NanoCpus'],
              'cgroupns':c['HostConfig'].get('CgroupnsMode')}
        if c['State']['Running']:
            stats=api('/containers/'+c['Id']+'/stats?stream=false&one-shot=true')
            item['docker_stats']={'memory_usage':stats.get('memory_stats',{}).get('usage'),
                'memory_limit':stats.get('memory_stats',{}).get('limit'),
                'cpu_total_ns':stats.get('cpu_stats',{}).get('cpu_usage',{}).get('total_usage')}
        out['containers'].append(item)
    web=fetch('http://'+IP+':8090/')
    out['web']={'status':200,'sha256':hashlib.sha256(web).hexdigest()}
    mem=Path('/proc/meminfo').read_text()
    out['lxc_proc']={'cpu_count':len(re.findall(r'^cpu\d+ ',Path('/proc/stat').read_text(),re.M)),
        'mem_total_bytes':int(re.search(r'MemTotal:\s+(\d+)',mem).group(1))*1024,
        'mem_available_bytes':int(re.search(r'MemAvailable:\s+(\d+)',mem).group(1))*1024}
    for name,port in [('node',9100),('cadvisor',8085)]:
        text=fetch('http://'+IP+':'+str(port)+'/metrics').decode()
        if name=='node':
            metrics=['node_memory_MemTotal_bytes','node_memory_MemAvailable_bytes','node_cpu_seconds_total','node_filesystem_size_bytes','node_filesystem_avail_bytes','node_exporter_build_info','lxc_cpu_usage_seconds_total','lxc_cpu_user_seconds_total','lxc_cpu_system_seconds_total','lxc_cpu_capacity_cores','lxc_cpu_collector_success','lxc_cpu_collector_timestamp_seconds','node_textfile_scrape_error']
        else:metrics=['container_memory_usage_bytes','container_memory_working_set_bytes','container_cpu_usage_seconds_total','container_spec_memory_limit_bytes','container_last_seen','cadvisor_version_info']
        out[name]={metric:rows(text,metric) for metric in metrics}
    print(json.dumps(out,sort_keys=True))

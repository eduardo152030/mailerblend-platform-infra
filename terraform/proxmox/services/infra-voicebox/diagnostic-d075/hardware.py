"""PVE read-only hardware, actual CT627 controls and memory counters."""
import subprocess,json,time,datetime
from pathlib import Path

def read(p):
 try:return Path(p).read_text().strip()
 except OSError:return None
def sample():
 cg=Path('/sys/fs/cgroup/lxc/627')
 return {'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cgroup':{k:read(cg/k) for k in ['memory.current','memory.stat','memory.pressure','memory.swap.current','memory.swap.max','memory.events','cpu.stat','cpu.max','cpuset.cpus.effective','cpuset.mems.effective']},'meminfo':read('/proc/meminfo'),'host_memory_pressure':read('/proc/pressure/memory'),'cpu_frequencies':{p.parent.name:{q.name:read(q) for q in p.glob('*') if q.name in ['scaling_cur_freq','cpuinfo_max_freq','cpuinfo_min_freq','scaling_min_freq','scaling_max_freq','scaling_governor','scaling_driver']} for p in Path('/sys/devices/system/cpu').glob('cpu[0-9]*/cpufreq')},'thermal_throttle':{str(p):read(p) for p in Path('/sys/devices/system/cpu').glob('cpu[0-9]*/thermal_throttle/*throttle_count')}}
dmi=subprocess.run(['dmidecode','-t','16','-t','17'],capture_output=True,text=True,timeout=10);keep=['Size:','Locator:','Bank Locator:','Type:','Speed:','Configured Memory Speed:','Number Of Devices:','Maximum Capacity:'];dmi_lines=[line.strip() for line in dmi.stdout.splitlines() if any(line.strip().startswith(k) for k in keep)]
r={'lscpu':subprocess.check_output(['lscpu','-J'],text=True),'dmi_memory':{'returncode':dmi.returncode,'filtered':dmi_lines},'before':sample()};time.sleep(5);r['after']=sample();print(json.dumps(r))

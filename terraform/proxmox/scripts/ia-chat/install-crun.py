#!/usr/bin/env python3
"""Dentro631: runtime OCI crun fijo, conserva perfil LXC/seccomp; sin downgrade."""
import urllib.request,hashlib,pathlib,json,subprocess
p=pathlib.Path('/usr/local/bin/crun');url='https://github.com/containers/crun/releases/download/1.31/crun-1.31-linux-amd64';sha='8cacae171bb0e5f9e275adac2eeb2c6ec8c69fdedff7b008eadd8cdd25b0d349'
if not p.exists():
 data=urllib.request.urlopen(url,timeout=90).read();assert hashlib.sha256(data).hexdigest()==sha;p.write_bytes(data);p.chmod(0o755)
assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
cfg=pathlib.Path('/etc/docker/daemon.json');settings=json.loads(cfg.read_text()) if cfg.exists() else {};settings.setdefault('runtimes',{})['crun']={'path':str(p)};cfg.write_text(json.dumps(settings,indent=2)+'\n')
subprocess.run(['systemctl','restart','docker'],check=True)
subprocess.run([str(p),'--version'],check=True)

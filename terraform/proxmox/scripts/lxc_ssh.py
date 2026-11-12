"""Public-key parsing and SSH bootstrap artifacts. Never reads private key files."""
import base64,hashlib,json,struct,shutil
from pathlib import Path

def public_key(text):
 if 'PRIVATE KEY' in text:raise ValueError('Private key input refused')
 lines=[line.strip() for line in text.splitlines() if line.strip()]
 if len(lines)!=1:raise ValueError('Expected one OpenSSH public key')
 fields=lines[0].split()
 if len(fields)<2 or fields[0] not in ['ssh-ed25519','ssh-rsa','ecdsa-sha2-nistp256','ecdsa-sha2-nistp384','ecdsa-sha2-nistp521']:raise ValueError('Invalid public key type')
 try:
  blob=base64.b64decode(fields[1],validate=True);n=struct.unpack('>I',blob[:4])[0]
  if blob[4:4+n].decode()!=fields[0]:raise ValueError('Public key wire type mismatch')
 except Exception as exc:raise ValueError('Invalid public key encoding') from exc
 return fields[0]+' '+fields[1], 'SHA256:'+base64.b64encode(hashlib.sha256(blob).digest()).decode().rstrip('=')

def render(root,out,data,key_file,protected):
 key_file=Path(key_file).expanduser()
 if key_file.is_symlink() or key_file.suffix!='.pub':raise ValueError('Only .pub public-key sources are accepted')
 key,fingerprint=public_key(key_file.read_text());out.mkdir(mode=0o700)
 (out/'owner.pub').write_text(key+'\n');(out/'owner.pub').chmod(0o600)
 for name in ['bootstrap-ssh-guest.py','00-lxc-bootstrap.conf']:shutil.copy2(root/'templates/provisioning/ssh'/name,out/name)
 conf={'schema':1,'owner_public_key_file':str(key_file.resolve()),'ct_id':data['service']['vmid'],'hostname':data['service']['name'],'ip':data['service']['ip'].split('/')[0],'pve_host':'pve','key_fingerprint':fingerprint,'protected_ct_ids':sorted(protected),'docker':data['monitoring']['docker'],'fixture':data['service']['ip'].startswith(('192.0.2.','198.51.100.','203.0.113.'))}
 (out/'bootstrap.json').write_text(json.dumps(conf,indent=2)+'\n');(out/'bootstrap.json').chmod(0o600)
 return fingerprint

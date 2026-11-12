"""Pinned public sources; patch only ES import selection and explicit local model paths."""
from pathlib import Path
import urllib.request,hashlib,tarfile,io,json
locks=json.loads(Path('/build/source-lock.json').read_text())
for name,info in locks.items():
 raw=urllib.request.urlopen(info['url'],timeout=60).read();assert hashlib.sha256(raw).hexdigest()==info['sha256']
 with tarfile.open(fileobj=io.BytesIO(raw)) as t:
  for m in t:
   parts=Path(m.name).parts[1:]
   if not parts or '..' in parts:continue
   target=Path('/src')/name/Path(*parts)
   if m.isdir():target.mkdir(parents=True,exist_ok=True)
   elif m.isfile():target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(t.extractfile(m).read())
# Melo only needs Spanish phonemization; avoid unrelated-language package imports/downloads.
p=Path('/src/melo/melo/text/cleaner.py');s=p.read_text();s=s.replace('from . import chinese, japanese, english, chinese_mix, korean, french, spanish','from . import spanish');start=s.index('language_module_map =');end=s.index('\n\ndef clean_text',start);s=s[:start]+"language_module_map = {'ES': spanish, 'SP': spanish}"+s[end:];p.write_text(s)
p=Path('/src/melo/melo/download_utils.py');p.write_text('''import torch\nfrom . import utils\ndef load_or_download_config(language,use_hf=True,config_path=None):\n assert config_path, "Explicit pinned local config required"\n return utils.get_hparams_from_file(config_path)\ndef load_or_download_model(language,device,use_hf=True,ckpt_path=None):\n assert ckpt_path, "Explicit pinned local checkpoint required"\n return torch.load(ckpt_path,map_location=device)\n''')
# Force only the verified local Spanish tokenizer; no remote fetch on module import.
p=Path('/src/melo/melo/text/spanish.py');s=p.read_text().replace("model_id = 'dccuchile/bert-base-spanish-wwm-uncased'","model_id = '/models/tokenizer'");p.write_text(s)

# Upstream forwards its converter-only flag into a base constructor that rejects it.
p=Path('/src/openvoice/openvoice/api.py');s=p.read_text();old="        super().__init__(*args, **kwargs)\n\n        if kwargs.get('enable_watermark', True):";assert s.count(old)==1;s=s.replace(old,"        enable_watermark = kwargs.pop('enable_watermark', True)\n        super().__init__(*args, **kwargs)\n\n        if enable_watermark:");p.write_text(s)

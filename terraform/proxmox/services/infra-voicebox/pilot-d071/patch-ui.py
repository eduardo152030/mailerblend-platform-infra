"""Add an engine using the existing selector; no UI architecture changes."""
from pathlib import Path
root=Path('/build/app/src')
p=root/'components/Generation/EngineModelSelector.tsx';s=p.read_text();start=s.index('const ENGINE_OPTIONS = [');end=s.index('] as const;',start)+len('] as const;');s=s[:start]+'''const ENGINE_OPTIONS = [
  {value:'openvoice',label:'OpenVoice V2 · Mi voz (CPU)',engine:'openvoice'},
  {value:'kokoro',label:'Kokoro 82M',engine:'kokoro'},
  {value:'piper',label:'Piper español',engine:'piper'},
] as const;'''+s[end:];s=s.replace('const CLONING_ENGINES = new Set([','const CLONING_ENGINES = new Set([\n  \'openvoice\',');s=s.replace('const ENGINE_DESCRIPTIONS: Record<string, string> = {',"const ENGINE_DESCRIPTIONS: Record<string, string> = {openvoice:'Clonación personal en español',piper:'Voz española integrada',");p.write_text(s)
p=root/'lib/hooks/useGenerationForm.ts';s=p.read_text().replace("      'qwen',","      'openvoice',\n      'piper',\n      'qwen',",1).replace("const modelName =\n", "const modelName = engine === 'openvoice' ? 'openvoice-es' : engine === 'piper' ? 'piper-es-es' :\n").replace('const displayName =\n',"const displayName = engine === 'openvoice' ? 'OpenVoice V2 + MeloES' : engine === 'piper' ? 'Piper español' :\n");p.write_text(s)
p=root/'lib/api/types.ts';s=p.read_text().replace("    | 'qwen'","    | 'openvoice'\n    | 'piper'\n    | 'qwen'",1);p.write_text(s)
p=root/'lib/constants/languages.ts';s=p.read_text().replace("  qwen: [","  openvoice: ['es'],\n  piper: ['es'],\n  qwen: [",1);p.write_text(s)
p=root/'lib/utils/format.ts';s=p.read_text().replace("  qwen: 'Qwen',","  openvoice: 'OpenVoice V2 + MeloES',\n  piper: 'Piper español',\n  qwen: 'Qwen',");p.write_text(s)

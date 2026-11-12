import fs from 'node:fs';
const root='/build/app/src/';
function edit(path,fn){let s=fs.readFileSync(root+path,'utf8');fs.writeFileSync(root+path,fn(s));}
edit('components/Generation/EngineModelSelector.tsx',s=>s.replace(/const ENGINE_OPTIONS = \[[\s\S]*?\] as const;/,`const ENGINE_OPTIONS = [
 {value:'openvoice',label:'OpenVoice V2 · Mi voz (CPU)',engine:'openvoice'},
 {value:'kokoro',label:'Kokoro 82M',engine:'kokoro'},
 {value:'piper',label:'Piper español',engine:'piper'},
] as const;`).replace('const CLONING_ENGINES = new Set([',"const CLONING_ENGINES = new Set([\n 'openvoice',").replace('const ENGINE_DESCRIPTIONS: Record<string, string> = {',"const ENGINE_DESCRIPTIONS: Record<string, string> = {openvoice:'Clonación personal en español',piper:'Voz española integrada',"));
edit('lib/hooks/useGenerationForm.ts',s=>s.replace("      'qwen',","      'openvoice',\n      'piper',\n      'qwen',").replace('const modelName =\n',"const modelName = engine === 'openvoice' ? 'openvoice-es' : engine === 'piper' ? 'piper-es-es' :\n").replace('const displayName =\n',"const displayName = engine === 'openvoice' ? 'OpenVoice V2 + MeloES' : engine === 'piper' ? 'Piper español' :\n"));
edit('lib/api/types.ts',s=>s.replace("    | 'qwen'","    | 'openvoice'\n    | 'piper'\n    | 'qwen'"));
edit('lib/constants/languages.ts',s=>s.replace('  qwen: [',"  openvoice: ['es'],\n  piper: ['es'],\n  qwen: ["));
edit('lib/utils/format.ts',s=>s.replace("  qwen: 'Qwen',","  openvoice: 'OpenVoice V2 + MeloES',\n  piper: 'Piper español',\n  qwen: 'Qwen',"));

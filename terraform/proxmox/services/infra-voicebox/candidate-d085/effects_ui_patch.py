"""Small asserted patch to pinned FloatingGenerateBox. No profile defaults changed."""
from pathlib import Path

def apply(src):
    p=Path(src)/'components/Generation/FloatingGenerateBox.tsx';s=p.read_text()
    assert 'prioritizeGenerationEffects' not in s
    s="import { prioritizeGenerationEffects } from '@/lib/constants/generationEffects';\n"+s
    assert s.count('{effectPresets?.map((preset) => (')==1
    s=s.replace('{effectPresets?.map((preset) => (','{prioritizeGenerationEffects(effectPresets ?? []).map((preset) => (')
    old='<SelectTrigger className="h-8 text-xs bg-card border-border rounded-full hover:bg-background/50 transition-all">\n                        <SelectValue placeholder={t(\'generation.effects.none\')} />'
    assert s.count(old)==1
    s=s.replace(old,old.replace('<SelectTrigger className=', '<SelectTrigger aria-label="Audio effects" className='))
    p.write_text(s)
if __name__=='__main__':
    import sys
    apply(sys.argv[1])

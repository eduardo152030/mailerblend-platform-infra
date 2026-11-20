import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { useLSSInviteTemplates } from "@/hooks/use-api";
import { MessageSquare, Eye, AlertTriangle, Trophy, Info } from "lucide-react";

const TYPE_LABELS: Record<string, string> = {
  PROFESSIONAL_NEUTRAL: "Profesional Neutral",
  MICRO_CONTEXTUAL: "Micro-contextual",
  CUSTOM: "Custom",
};

/* ───── Template Card ───── */
function TemplateCard({
  template,
  onViewStats,
}: {
  template: any;
  onViewStats: () => void;
}) {
  const rate = template.times_sent > 0
    ? ((template.times_accepted / template.times_sent) * 100).toFixed(1)
    : "0.0";

  return (
    <Card className={`border-l-4 ${template.is_active ? "border-l-emerald-500" : "border-l-muted"}`}>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div className="space-y-1 min-w-0">
            <CardTitle className="text-sm font-medium flex items-center gap-2 flex-wrap">
              <span className={`inline-block h-2 w-2 rounded-full ${template.is_active ? "bg-emerald-500" : "bg-muted-foreground/40"}`} />
              {template.display_name || template.template_name}
              {template.is_default && <Badge className="text-[10px]">Default</Badge>}
            </CardTitle>
            <div className="flex gap-2 flex-wrap text-[10px]">
              <Badge variant="outline">{TYPE_LABELS[template.template_type] || template.template_type}</Badge>
              <span className="text-muted-foreground">Pack: {template.target_pack || "ALL"}</span>
              <span className="text-muted-foreground">Peso: {template.weight}%</span>
            </div>
          </div>
          <div className="flex gap-1 shrink-0">
            <Button size="icon" variant="ghost" className="h-7 w-7" onClick={onViewStats}><Eye size={13} /></Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="text-xs space-y-2 pt-0">
        <div className="bg-muted/50 rounded-md p-2.5 italic text-muted-foreground whitespace-pre-wrap">
          "{template.template_text}"
        </div>
        <p className="text-muted-foreground">
          📊 {template.times_sent ?? 0} enviadas · {template.times_accepted ?? 0} aceptadas · {rate}% rate
        </p>
        {template.description && <p className="text-muted-foreground/70">{template.description}</p>}
      </CardContent>
    </Card>
  );
}

function StatsModal({ open, onClose, template, allTemplates }: { open: boolean; onClose: () => void; template: any; allTemplates: any[] }) {
  const rate = template.times_sent > 0 ? (template.times_accepted / template.times_sent) * 100 : 0;
  const bestRate = Math.max(...allTemplates.map((t: any) => t.times_sent > 0 ? (t.times_accepted / t.times_sent) * 100 : 0));
  const isBest = rate >= bestRate && template.times_sent > 0;

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="text-base">Stats – {template.display_name || template.template_name}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 text-sm">
          <Card>
            <CardContent className="pt-4 space-y-3">
              <div className="text-center">
                <p className="text-2xl font-bold">{rate.toFixed(1)}%</p>
                <p className="text-xs text-muted-foreground">Acceptance Rate</p>
              </div>
              <Progress value={rate} className="h-2" />
              <div className="grid grid-cols-3 gap-2 text-center text-xs">
                <div><p className="font-semibold">{template.times_sent ?? 0}</p><p className="text-muted-foreground">Enviadas</p></div>
                <div><p className="font-semibold">{template.times_accepted ?? 0}</p><p className="text-muted-foreground">Aceptadas</p></div>
                <div><p className="font-semibold">{(template.times_sent ?? 0) - (template.times_accepted ?? 0)}</p><p className="text-muted-foreground">Pend/Rech</p></div>
              </div>
            </CardContent>
          </Card>

          <div className="space-y-2">
            <p className="text-xs font-semibold">📊 Comparación con otros templates</p>
            <div className="border rounded-md overflow-hidden">
              <table className="w-full text-xs">
                <thead className="bg-muted/50"><tr><th className="text-left p-2">Template</th><th className="text-right p-2">Enviadas</th><th className="text-right p-2">Accept Rate</th></tr></thead>
                <tbody>
                  {allTemplates.map((t: any) => {
                    const r = t.times_sent > 0 ? ((t.times_accepted / t.times_sent) * 100).toFixed(1) : "0.0";
                    const isThis = t.id === template.id;
                    const isBestRow = t.times_sent > 0 && parseFloat(r) >= bestRate;
                    return (
                      <tr key={t.id} className={isThis ? "bg-muted/30" : ""}>
                        <td className="p-2 font-medium">{t.display_name || t.template_name} {isBestRow && <Trophy size={11} className="inline text-amber-500 ml-1" />}</td>
                        <td className="p-2 text-right">{t.times_sent ?? 0}</td>
                        <td className="p-2 text-right">{r}%</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {isBest && (
            <div className="space-y-1">
              <p className="text-xs font-semibold">💡 Insights</p>
              <ul className="text-xs text-muted-foreground space-y-0.5 list-disc pl-4">
                <li>Este template tiene el mejor performance</li>
                <li>Considera aumentar el peso a 60-70%</li>
              </ul>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" size="sm" onClick={onClose}>Cerrar</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

/* ───── Main Section ───── */
export default function InviteTemplatesSection() {
  const { data, isLoading , isError } = useLSSInviteTemplates({ limit: 50 });

  const templates: any[] = (data as any)?.templates ?? (data as any)?.items ?? [];
  const active = templates.filter((t) => t.is_active);
  const inactive = templates.filter((t) => !t.is_active);

  const totalSent = templates.reduce((s, t) => s + (t.times_sent ?? 0), 0);
  const totalAccepted = templates.reduce((s, t) => s + (t.times_accepted ?? 0), 0);
  const globalRate = totalSent > 0 ? ((totalAccepted / totalSent) * 100).toFixed(1) : "0.0";
  const totalWeight = active.reduce((s, t) => s + (t.weight ?? 0), 0);

  const [statsModal, setStatsModal] = useState<{ open: boolean; template?: any }>({ open: false });

  if (isError) return <p role="alert" className="text-destructive">No se pudo cargar esta configuración.</p>;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <MessageSquare size={16} className="text-muted-foreground" />
          <span className="text-sm font-medium">Invite Templates</span>
        </div>
      </div>

      {/* Info banner */}
      <div className="flex items-start gap-2 rounded-md border border-border bg-muted/30 p-3 text-xs text-muted-foreground">
        <Info size={14} className="shrink-0 mt-0.5" />
        Los templates se rotan automáticamente (A/B testing) para maximizar el acceptance rate.
      </div>

      {/* Global stats */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: "Enviadas", value: totalSent },
          { label: "Aceptadas", value: totalAccepted },
          { label: "Accept Rate", value: `${globalRate}%` },
        ].map((s) => (
          <Card key={s.label}>
            <CardContent className="py-3 text-center">
              <p className="text-lg font-bold">{s.value}</p>
              <p className="text-[10px] text-muted-foreground">{s.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {isLoading ? (
        <div className="space-y-3">{Array.from({ length: 2 }).map((_, i) => <Skeleton key={i} className="h-32 w-full" />)}</div>
      ) : (
        <>
          {/* Active */}
          <div className="space-y-2">
            <p className="text-xs font-semibold">🎯 TEMPLATES ACTIVOS ({active.length})</p>
            {active.length === 0 && <p className="text-xs text-muted-foreground py-4 text-center">No hay templates activos.</p>}
            {active.map((t) => (
              <TemplateCard key={t.id} template={t}
                onViewStats={() => setStatsModal({ open: true, template: t })}
              />
            ))}
          </div>

          {/* Weight validation */}
          {active.length > 0 && (
            <div className={`flex items-center gap-2 text-xs rounded-md border p-2.5 ${totalWeight === 100 ? "border-emerald-500/40 bg-emerald-500/5 text-emerald-700" : "border-destructive/40 bg-destructive/5 text-destructive"}`}>
              {totalWeight === 100 ? "✅" : <AlertTriangle size={13} />}
              Peso total: {active.map((t) => `${t.weight}%`).join(" + ")} = {totalWeight}%
              {totalWeight !== 100 && " — debe sumar 100%"}
            </div>
          )}

          {/* Inactive */}
          {inactive.length > 0 && (
            <div className="space-y-2">
              <Separator />
              <p className="text-xs font-semibold text-muted-foreground">INACTIVOS ({inactive.length})</p>
              {inactive.map((t) => (
                <TemplateCard key={t.id} template={t}
                  onViewStats={() => setStatsModal({ open: true, template: t })}
                />
              ))}
            </div>
          )}
        </>
      )}

      {/* Modals */}
      {statsModal.open && statsModal.template && (
        <StatsModal open onClose={() => setStatsModal({ open: false })} template={statsModal.template} allTemplates={templates} />
      )}
    </div>
  );
}
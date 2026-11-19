import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { useLSSInviteTemplates, useLSSCreateInviteTemplate, useLSSPatchInviteTemplate } from "@/hooks/use-api";
import { toast } from "sonner";
import { MessageSquare, Plus, Pencil, Eye, Power, AlertTriangle, Trophy, Info } from "lucide-react";

const TYPE_LABELS: Record<string, string> = {
  PROFESSIONAL_NEUTRAL: "Profesional Neutral",
  MICRO_CONTEXTUAL: "Micro-contextual",
  CUSTOM: "Custom",
};

const PACK_LABELS: Record<string, string> = {
  ALL: "Todos los packs",
  GUARDIAN: "GUARDIAN",
  MOTOR: "MOTOR",
  FORTALEZA: "FORTALEZA",
};

/* ───── Template Card ───── */
function TemplateCard({
  template,
  onEdit,
  onToggleActive,
  onViewStats,
}: {
  template: any;
  onEdit: () => void;
  onToggleActive: () => void;
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
            <Button size="icon" variant="ghost" className="h-7 w-7" onClick={onEdit}><Pencil size={13} /></Button>
            <Button size="icon" variant="ghost" className="h-7 w-7" onClick={onViewStats}><Eye size={13} /></Button>
            <Button size="icon" variant="ghost" className="h-7 w-7" onClick={onToggleActive}>
              <Power size={13} className={template.is_active ? "text-emerald-500" : "text-muted-foreground"} />
            </Button>
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

/* ───── Create / Edit Modal ───── */
function TemplateFormModal({
  open,
  onClose,
  editTemplate,
}: {
  open: boolean;
  onClose: () => void;
  editTemplate?: any;
}) {
  const createMut = useLSSCreateInviteTemplate();
  const patchMut = useLSSPatchInviteTemplate();

  const [form, setForm] = useState({
    template_name: editTemplate?.template_name ?? "",
    display_name: editTemplate?.display_name ?? "",
    template_type: editTemplate?.template_type ?? "CUSTOM",
    template_text: editTemplate?.template_text ?? "",
    target_pack: editTemplate?.target_pack ?? "ALL",
    weight: editTemplate?.weight ?? 50,
    description: editTemplate?.description ?? "",
    notes: editTemplate?.notes ?? "",
  });

  const detectedVars = useMemo(() => {
    const m = form.template_text.match(/\{\{(\w+)\}\}/g) || [];
    return [...new Set(m.map((v: string) => v.replace(/\{\{|\}\}/g, "")))];
  }, [form.template_text]);

  const charCount = form.template_text.length;
  const isEditing = !!editTemplate;

  const handleSave = async () => {
    const payload = { ...form, required_variables: detectedVars };
    try {
      if (isEditing) {
        await patchMut.mutateAsync({ id: editTemplate.id, data: payload });
      } else {
        await createMut.mutateAsync(payload);
      }
      toast.success(isEditing ? "Template actualizado" : "Template creado");
      onClose();
    } catch (e: any) {
      toast.error(e.message || "Error al guardar");
    }
  };

  const set = (k: string, v: any) => setForm((prev) => ({ ...prev, [k]: v }));

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-base">{isEditing ? "Editar" : "Nuevo"} Template de Invitación</DialogTitle>
        </DialogHeader>

        <div className="space-y-3 text-sm">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label className="text-xs">Nombre (ID)</Label>
              <Input className="h-8 text-xs" value={form.template_name} onChange={(e) => set("template_name", e.target.value)} placeholder="custom_saas_v1" disabled={isEditing} />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Nombre descriptivo</Label>
              <Input className="h-8 text-xs" value={form.display_name} onChange={(e) => set("display_name", e.target.value)} placeholder="Custom para SaaS" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label className="text-xs">Tipo de estrategia</Label>
              <Select value={form.template_type} onValueChange={(v) => set("template_type", v)}>
                <SelectTrigger className="h-8 text-xs"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {Object.entries(TYPE_LABELS).map(([k, v]) => <SelectItem key={k} value={k}>{v}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Pack objetivo</Label>
              <Select value={form.target_pack} onValueChange={(v) => set("target_pack", v)}>
                <SelectTrigger className="h-8 text-xs"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {Object.entries(PACK_LABELS).map(([k, v]) => <SelectItem key={k} value={k}>{v}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-1">
            <Label className="text-xs">Texto del mensaje</Label>
            <p className="text-[10px] text-muted-foreground">Variables: {"{{nombre}}, {{empresa}}, {{rol}}, {{ciudad}}, {{sector}}"}</p>
            <Textarea className="text-xs min-h-[80px]" maxLength={300} value={form.template_text} onChange={(e) => set("template_text", e.target.value)} placeholder="Hola {{nombre}}, ..." />
            <p className={`text-[10px] ${charCount > 280 ? "text-destructive" : "text-muted-foreground"}`}>{charCount}/300 caracteres</p>
          </div>

          {detectedVars.length > 0 && (
            <div className="flex gap-1.5 flex-wrap">
              <span className="text-[10px] text-muted-foreground">Variables detectadas:</span>
              {detectedVars.map((v: string) => <Badge key={v} variant="secondary" className="text-[10px] font-mono">{v}</Badge>)}
            </div>
          )}

          <div className="space-y-1">
            <Label className="text-xs">Peso A/B testing (0-100)</Label>
            <Input className="h-8 text-xs w-24" type="number" min={0} max={100} value={form.weight} onChange={(e) => set("weight", parseInt(e.target.value) || 0)} />
            <p className="text-[10px] text-muted-foreground flex items-center gap-1"><Info size={10} /> Mayor peso = más probabilidad de ser seleccionado</p>
          </div>

          <div className="space-y-1">
            <Label className="text-xs">Descripción (opcional)</Label>
            <Input className="h-8 text-xs" value={form.description} onChange={(e) => set("description", e.target.value)} />
          </div>
          <div className="space-y-1">
            <Label className="text-xs">Notas internas (opcional)</Label>
            <Textarea className="text-xs min-h-[50px]" value={form.notes} onChange={(e) => set("notes", e.target.value)} />
          </div>
        </div>

        <DialogFooter className="gap-2">
          <Button variant="outline" size="sm" onClick={onClose}>Cancelar</Button>
          <Button size="sm" onClick={handleSave} disabled={!form.template_name || !form.template_text || createMut.isPending || patchMut.isPending}>
            {isEditing ? "Actualizar" : "Guardar"} Template
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

/* ───── Stats Modal ───── */
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
  const { data, isLoading } = useLSSInviteTemplates({ limit: 50 });
  const patchMut = useLSSPatchInviteTemplate();

  const templates: any[] = (data as any)?.templates ?? (data as any)?.items ?? [];
  const active = templates.filter((t) => t.is_active);
  const inactive = templates.filter((t) => !t.is_active);

  const totalSent = templates.reduce((s, t) => s + (t.times_sent ?? 0), 0);
  const totalAccepted = templates.reduce((s, t) => s + (t.times_accepted ?? 0), 0);
  const globalRate = totalSent > 0 ? ((totalAccepted / totalSent) * 100).toFixed(1) : "0.0";
  const totalWeight = active.reduce((s, t) => s + (t.weight ?? 0), 0);

  const [formModal, setFormModal] = useState<{ open: boolean; template?: any }>({ open: false });
  const [statsModal, setStatsModal] = useState<{ open: boolean; template?: any }>({ open: false });

  const toggleActive = async (t: any) => {
    try {
      await patchMut.mutateAsync({ id: t.id, data: { is_active: !t.is_active } });
      toast.success(t.is_active ? "Template desactivado" : "Template activado");
    } catch (e: any) {
      toast.error(e.message);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <MessageSquare size={16} className="text-muted-foreground" />
          <span className="text-sm font-medium">Invite Templates</span>
        </div>
        <Button size="sm" className="h-7 text-xs" onClick={() => setFormModal({ open: true })}>
          <Plus size={13} className="mr-1" /> Nuevo Template
        </Button>
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
                onEdit={() => setFormModal({ open: true, template: t })}
                onToggleActive={() => toggleActive(t)}
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
                  onEdit={() => setFormModal({ open: true, template: t })}
                  onToggleActive={() => toggleActive(t)}
                  onViewStats={() => setStatsModal({ open: true, template: t })}
                />
              ))}
            </div>
          )}
        </>
      )}

      {/* Modals */}
      {formModal.open && (
        <TemplateFormModal open onClose={() => setFormModal({ open: false })} editTemplate={formModal.template} />
      )}
      {statsModal.open && statsModal.template && (
        <StatsModal open onClose={() => setStatsModal({ open: false })} template={statsModal.template} allTemplates={templates} />
      )}
    </div>
  );
}
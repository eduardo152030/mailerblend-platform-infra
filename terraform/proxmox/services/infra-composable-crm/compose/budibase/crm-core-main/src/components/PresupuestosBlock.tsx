import { useState, useMemo } from "react";
import { useCreatePresupuesto, usePatchPresupuesto } from "@/hooks/use-api";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { formatDistanceToNow } from "date-fns";
import { es } from "date-fns/locale";
import {
  Plus, Pencil, FileText, Send, Check, X, Copy, ExternalLink, Loader2, Trash2,
} from "lucide-react";

// ─── Types ──────────────────────────────────────────────────────
interface LineItem {
  item: string;
  description: string;
  quantity: number;
  unit_price: number;
  total: number;
}

interface PresupuestosBlockProps {
  presupuestos: Record<string, unknown>[];
  oportunidad: Record<string, unknown>;
  contacto: Record<string, unknown> | undefined;
}

// ─── Helpers ────────────────────────────────────────────────────
function formatDate(v: unknown) {
  if (!v) return "—";
  try {
    return new Date(String(v)).toLocaleDateString("es-ES", { day: "2-digit", month: "short", year: "numeric" });
  } catch {
    return "—";
  }
}

function relativeTime(v: unknown) {
  if (!v) return "—";
  try {
    return formatDistanceToNow(new Date(String(v)), { addSuffix: true, locale: es });
  } catch {
    return "—";
  }
}

function formatCurrency(v: unknown, currency?: unknown) {
  if (v == null || v === "") return "—";
  const cur = String(currency ?? "EUR");
  return new Intl.NumberFormat("es-ES", { style: "currency", currency: cur }).format(Number(v));
}

function getStatusBadge(quote: Record<string, unknown>): { text: string; className: string; warning: boolean } {
  const status = String(quote.status ?? "");
  const validUntil = quote.valid_until ? new Date(String(quote.valid_until)) : null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  if (validUntil) validUntil.setHours(0, 0, 0, 0);
  const isExpired = validUntil && validUntil < today;

  const map: Record<string, { text: string; className: string }> = {
    Draft: { text: "Borrador", className: "bg-muted text-muted-foreground" },
    Sent: { text: "Enviado", className: "bg-accent text-accent-foreground" },
    Accepted: { text: "Aceptado", className: "bg-success/20 text-success" },
    Rejected: { text: "Rechazado", className: "bg-destructive/20 text-destructive" },
    Expired: { text: "Expirado", className: "bg-warning/20 text-warning" },
  };

  if (isExpired && status === "Sent") {
    return { text: "Vencido", className: "bg-warning/20 text-warning", warning: true };
  }

  const base = map[status] ?? { text: status || "—", className: "bg-muted text-muted-foreground" };
  return { ...base, warning: false };
}

const STATUSES = ["Draft", "Sent", "Accepted", "Rejected", "Expired"];
const CURRENCIES = ["EUR", "USD", "GBP"];

// ─── Component ──────────────────────────────────────────────────
export default function PresupuestosBlock({ presupuestos, oportunidad, contacto }: PresupuestosBlockProps) {
  const { toast } = useToast();
  const createPresupuesto = useCreatePresupuesto();
  const patchPresupuesto = usePatchPresupuesto();

  const [showCreate, setShowCreate] = useState(false);
  const [editingQuote, setEditingQuote] = useState<Record<string, unknown> | null>(null);

  // ─── Create defaults ────────────────────────────────────────
  const getDefaults = () => {
    const thirtyDays = new Date();
    thirtyDays.setDate(thirtyDays.getDate() + 30);
    return {
      title: `Propuesta - ${String(oportunidad.deal_name ?? "")}`,
      version: 1,
      quote_value: oportunidad.deal_value ?? 0,
      currency: String(oportunidad.currency ?? "EUR"),
      line_items: [] as LineItem[],
      status: "Draft",
      valid_until: thirtyDays.toISOString().split("T")[0],
      notes: "",
      internal_notes: "",
    };
  };

  const [formData, setFormData] = useState(getDefaults);
  const [lineItems, setLineItems] = useState<LineItem[]>([]);

  const openCreate = () => {
    const d = getDefaults();
    setFormData(d);
    setLineItems([]);
    setShowCreate(true);
  };

  const quoteValue = useMemo(
    () => lineItems.reduce((s, i) => s + (i.quantity || 0) * (i.unit_price || 0), 0),
    [lineItems]
  );

  const handleCreate = async () => {
    const title = String(formData.title ?? "").trim();
    if (!title) { toast({ title: "Título requerido", variant: "destructive" }); return; }
    const payload: Record<string, unknown> = {
      contacto_id: contacto?.id,
      oportunidad_id: oportunidad.id,
      title,
      version: Number(formData.version) || 1,
      quote_value: lineItems.length > 0 ? quoteValue : Number(formData.quote_value) || 0,
      currency: formData.currency,
      status: formData.status,
      valid_until: formData.valid_until || null,
      notes: formData.notes || null,
      internal_notes: formData.internal_notes || null,
    };
    if (lineItems.length > 0) {
      payload.line_items = lineItems.map((i) => ({
        ...i,
        total: (i.quantity || 0) * (i.unit_price || 0),
      }));
    }
    Object.keys(payload).forEach((k) => { if (payload[k] === "") payload[k] = null; });
    try {
      await createPresupuesto.mutateAsync(payload);
      toast({ title: "✓ Presupuesto creado" });
      setShowCreate(false);
    } catch (e) {
      toast({ title: "Error", description: String(e), variant: "destructive" });
    }
  };

  // ─── Quick actions ──────────────────────────────────────────
  const quickPatch = async (id: string, data: Record<string, unknown>, msg: string) => {
    try {
      await patchPresupuesto.mutateAsync({ id, data });
      toast({ title: msg });
    } catch (e) {
      toast({ title: "Error", description: String(e), variant: "destructive" });
    }
  };

  const markSent = (q: Record<string, unknown>) =>
    quickPatch(String(q.id), { status: "Sent", sent_at: new Date().toISOString() }, "Presupuesto enviado");

  const markAccepted = (q: Record<string, unknown>) =>
    quickPatch(String(q.id), { status: "Accepted", accepted_at: new Date().toISOString() }, "✓ Presupuesto aceptado");

  const markRejected = (q: Record<string, unknown>) =>
    quickPatch(String(q.id), { status: "Rejected", rejected_at: new Date().toISOString() }, "Presupuesto rechazado");

  const duplicateQuote = async (q: Record<string, unknown>) => {
    const payload: Record<string, unknown> = {
      contacto_id: q.contacto_id ?? contacto?.id,
      oportunidad_id: q.oportunidad_id ?? oportunidad.id,
      title: String(q.title ?? ""),
      version: (Number(q.version) || 1) + 1,
      quote_value: q.quote_value,
      currency: q.currency ?? "EUR",
      line_items: q.line_items ?? null,
      status: "Draft",
      valid_until: (() => { const d = new Date(); d.setDate(d.getDate() + 30); return d.toISOString().split("T")[0]; })(),
      notes: q.notes ?? null,
      internal_notes: q.internal_notes ?? null,
    };
    try {
      await createPresupuesto.mutateAsync(payload);
      toast({ title: "✓ Nueva versión creada (Draft)" });
    } catch (e) {
      toast({ title: "Error", description: String(e), variant: "destructive" });
    }
  };

  // ─── Edit ───────────────────────────────────────────────────
  const [editLineItems, setEditLineItems] = useState<LineItem[]>([]);

  const openEdit = (q: Record<string, unknown>) => {
    const items = Array.isArray(q.line_items) ? (q.line_items as LineItem[]) : [];
    setEditLineItems(items);
    setEditingQuote({
      _id: q.id,
      title: q.title ?? "",
      version: q.version ?? 1,
      quote_value: q.quote_value ?? 0,
      currency: q.currency ?? "EUR",
      status: q.status ?? "Draft",
      valid_until: q.valid_until ? String(q.valid_until).substring(0, 10) : "",
      pdf_url: q.pdf_url ?? "",
      notes: q.notes ?? "",
      internal_notes: q.internal_notes ?? "",
    });
  };

  const editQuoteValue = useMemo(
    () => editLineItems.reduce((s, i) => s + (i.quantity || 0) * (i.unit_price || 0), 0),
    [editLineItems]
  );

  const handleEdit = async () => {
    if (!editingQuote) return;
    const id = String(editingQuote._id);
    const payload: Record<string, unknown> = { ...editingQuote };
    delete payload._id;
    if (editLineItems.length > 0) {
      payload.line_items = editLineItems.map((i) => ({ ...i, total: (i.quantity || 0) * (i.unit_price || 0) }));
      payload.quote_value = editQuoteValue;
    }
    Object.keys(payload).forEach((k) => { if (payload[k] === "") payload[k] = null; });
    try {
      await patchPresupuesto.mutateAsync({ id, data: payload });
      toast({ title: "✓ Presupuesto actualizado" });
      setEditingQuote(null);
    } catch (e) {
      toast({ title: "Error", description: String(e), variant: "destructive" });
    }
  };

  // ─── Render ─────────────────────────────────────────────────
  return (
    <>
      <div className="border rounded-lg p-3">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-xs font-semibold text-muted-foreground flex items-center gap-1">
            <FileText size={14} /> PRESUPUESTOS ({presupuestos.length})
          </h4>
          <Button size="sm" variant="outline" className="h-7 text-xs" onClick={openCreate}>
            <Plus size={12} className="mr-1" /> Crear presupuesto
          </Button>
        </div>

        {presupuestos.length === 0 ? (
          <div className="text-center py-6">
            <p className="text-sm text-muted-foreground mb-2">Sin presupuestos todavía</p>
            <p className="text-xs text-muted-foreground mb-3">Crea presupuestos formales para enviar a tus clientes</p>
            <Button size="sm" variant="outline" onClick={openCreate}>
              <Plus size={12} className="mr-1" /> Crear primer presupuesto
            </Button>
          </div>
        ) : (
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {presupuestos.map((q, i) => {
              const badge = getStatusBadge(q);
              const st = String(q.status ?? "");
              return (
                <div key={i} className={`text-sm p-2.5 rounded border ${badge.warning ? "bg-orange-50 border-orange-200 dark:bg-orange-950/20 dark:border-orange-800/30" : "bg-muted/30 border-border/50"}`}>
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0 flex-1 space-y-1">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className="font-mono text-xs text-muted-foreground">{String(q.quote_number ?? "")}</span>
                        <span className="font-medium">{String(q.title ?? "—")}</span>
                        {q.version != null && <Badge variant="secondary" className="text-[10px] px-1.5 py-0">v{String(q.version)}</Badge>}
                        <Badge className={`text-[10px] px-1.5 py-0 border-0 ${badge.className}`}>{badge.text}</Badge>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-muted-foreground flex-wrap">
                        <span className="font-semibold text-foreground">{formatCurrency(q.quote_value, q.currency)}</span>
                        {q.valid_until && <span>Válido: {formatDate(q.valid_until)}</span>}
                        <span>{relativeTime(q.updated_at || q.created_at)}</span>
                      </div>
                    </div>
                    <div className="flex gap-1 shrink-0 flex-wrap">
                      {st === "Draft" && (
                        <Button variant="ghost" size="sm" className="h-6 w-6 p-0" title="Marcar Enviado"
                          onClick={() => markSent(q)} disabled={patchPresupuesto.isPending}>
                          <Send className="h-3 w-3 text-blue-500" />
                        </Button>
                      )}
                      {st === "Sent" && (
                        <>
                          <Button variant="ghost" size="sm" className="h-6 w-6 p-0" title="Aceptado"
                            onClick={() => markAccepted(q)} disabled={patchPresupuesto.isPending}>
                            <Check className="h-3 w-3 text-success" />
                          </Button>
                          <Button variant="ghost" size="sm" className="h-6 w-6 p-0" title="Rechazado"
                            onClick={() => markRejected(q)} disabled={patchPresupuesto.isPending}>
                            <X className="h-3 w-3 text-destructive" />
                          </Button>
                        </>
                      )}
                      {q.pdf_url && (
                        <Button variant="ghost" size="sm" className="h-6 w-6 p-0" title="Ver PDF"
                          onClick={() => window.open(String(q.pdf_url), "_blank")}>
                          <ExternalLink className="h-3 w-3 text-muted-foreground" />
                        </Button>
                      )}
                      <Button variant="ghost" size="sm" className="h-6 w-6 p-0" title="Duplicar (nueva versión)"
                        onClick={() => duplicateQuote(q)} disabled={createPresupuesto.isPending}>
                        <Copy className="h-3 w-3 text-muted-foreground" />
                      </Button>
                      <Button variant="ghost" size="sm" className="h-6 w-6 p-0" title="Editar"
                        onClick={() => openEdit(q)}>
                        <Pencil className="h-3 w-3 text-muted-foreground" />
                      </Button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* ─── CREATE MODAL ──────────────────────────────────── */}
      <Dialog open={showCreate} onOpenChange={(o) => { if (!o) setShowCreate(false); }}>
        <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText size={18} className="text-primary" /> Nuevo presupuesto
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {/* Context */}
            <div className="rounded-lg border bg-muted/20 p-3 space-y-1 text-sm">
              <div className="flex gap-2"><span className="text-muted-foreground">Oportunidad:</span> <span className="font-medium">{String(oportunidad.deal_name ?? "—")}</span></div>
              <div className="flex gap-2"><span className="text-muted-foreground">Contacto:</span> <span className="font-medium">{String(contacto?.nombre ?? "—")}</span></div>
            </div>

            <div className="space-y-1">
              <Label>Título *</Label>
              <Input value={String(formData.title ?? "")} onChange={(e) => setFormData((p) => ({ ...p, title: e.target.value }))} />
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div className="space-y-1">
                <Label>Versión</Label>
                <Input type="number" min={1} value={String(formData.version ?? 1)} onChange={(e) => setFormData((p) => ({ ...p, version: Number(e.target.value) || 1 }))} />
              </div>
              <div className="space-y-1">
                <Label>Moneda</Label>
                <Select value={formData.currency} onValueChange={(v) => setFormData((p) => ({ ...p, currency: v }))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>{CURRENCIES.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label>Estado</Label>
                <Select value={formData.status} onValueChange={(v) => setFormData((p) => ({ ...p, status: v }))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>{STATUSES.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-1">
              <Label>Válido hasta</Label>
              <Input type="date" value={String(formData.valid_until ?? "")} onChange={(e) => setFormData((p) => ({ ...p, valid_until: e.target.value }))} />
            </div>

            {/* Line Items Editor */}
            <LineItemsEditor items={lineItems} onChange={setLineItems} currency={formData.currency} />

            {/* Total */}
            <div className="flex items-center justify-between rounded-lg border bg-muted/30 p-3">
              <span className="text-sm font-semibold">Total del presupuesto</span>
              <span className="text-lg font-bold">
                {lineItems.length > 0
                  ? formatCurrency(quoteValue, formData.currency)
                  : <Input type="number" step="0.01" className="w-32 h-8 text-right" value={String(formData.quote_value ?? 0)}
                      onChange={(e) => setFormData((p) => ({ ...p, quote_value: Number(e.target.value) || 0 }))} />
                }
              </span>
            </div>

            <div className="space-y-1">
              <Label>Notas (visibles al cliente)</Label>
              <Textarea rows={2} value={String(formData.notes ?? "")} onChange={(e) => setFormData((p) => ({ ...p, notes: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label>Notas internas</Label>
              <Textarea rows={2} value={String(formData.internal_notes ?? "")} onChange={(e) => setFormData((p) => ({ ...p, internal_notes: e.target.value }))} />
            </div>

            <Button onClick={handleCreate} disabled={createPresupuesto.isPending || !String(formData.title ?? "").trim()} className="w-full">
              {createPresupuesto.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Crear presupuesto"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* ─── EDIT MODAL ────────────────────────────────────── */}
      <Dialog open={!!editingQuote} onOpenChange={(o) => { if (!o) setEditingQuote(null); }}>
        <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Pencil size={18} className="text-muted-foreground" /> Editar presupuesto
            </DialogTitle>
          </DialogHeader>
          {editingQuote && (
            <div className="space-y-4">
              <div className="space-y-1">
                <Label>Título *</Label>
                <Input value={String(editingQuote.title ?? "")} onChange={(e) => setEditingQuote((p) => p ? { ...p, title: e.target.value } : p)} />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-1">
                  <Label>Versión</Label>
                  <Input type="number" min={1} value={String(editingQuote.version ?? 1)} onChange={(e) => setEditingQuote((p) => p ? { ...p, version: Number(e.target.value) || 1 } : p)} />
                </div>
                <div className="space-y-1">
                  <Label>Moneda</Label>
                  <Select value={String(editingQuote.currency ?? "EUR")} onValueChange={(v) => setEditingQuote((p) => p ? { ...p, currency: v } : p)}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>{CURRENCIES.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <Label>Estado</Label>
                  <Select value={String(editingQuote.status ?? "Draft")} onValueChange={(v) => setEditingQuote((p) => p ? { ...p, status: v } : p)}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>{STATUSES.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <Label>Válido hasta</Label>
                  <Input type="date" value={String(editingQuote.valid_until ?? "")} onChange={(e) => setEditingQuote((p) => p ? { ...p, valid_until: e.target.value } : p)} />
                </div>
                <div className="space-y-1">
                  <Label>URL del PDF</Label>
                  <Input value={String(editingQuote.pdf_url ?? "")} onChange={(e) => setEditingQuote((p) => p ? { ...p, pdf_url: e.target.value } : p)} placeholder="https://..." />
                </div>
              </div>

              <LineItemsEditor items={editLineItems} onChange={setEditLineItems} currency={String(editingQuote.currency ?? "EUR")} />

              <div className="flex items-center justify-between rounded-lg border bg-muted/30 p-3">
                <span className="text-sm font-semibold">Total</span>
                <span className="text-lg font-bold">
                  {editLineItems.length > 0
                    ? formatCurrency(editQuoteValue, editingQuote.currency)
                    : <Input type="number" step="0.01" className="w-32 h-8 text-right" value={String(editingQuote.quote_value ?? 0)}
                        onChange={(e) => setEditingQuote((p) => p ? { ...p, quote_value: Number(e.target.value) || 0 } : p)} />
                  }
                </span>
              </div>

              <div className="space-y-1">
                <Label>Notas (visibles al cliente)</Label>
                <Textarea rows={2} value={String(editingQuote.notes ?? "")} onChange={(e) => setEditingQuote((p) => p ? { ...p, notes: e.target.value } : p)} />
              </div>
              <div className="space-y-1">
                <Label>Notas internas</Label>
                <Textarea rows={2} value={String(editingQuote.internal_notes ?? "")} onChange={(e) => setEditingQuote((p) => p ? { ...p, internal_notes: e.target.value } : p)} />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" onClick={() => setEditingQuote(null)}>Cancelar</Button>
                <Button onClick={handleEdit} disabled={patchPresupuesto.isPending || !String(editingQuote.title ?? "").trim()}>
                  {patchPresupuesto.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}
                  Guardar cambios
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}

// ─── Line Items Editor ──────────────────────────────────────────
function LineItemsEditor({
  items,
  onChange,
  currency,
}: {
  items: LineItem[];
  onChange: (items: LineItem[]) => void;
  currency: string;
}) {
  const addItem = () => {
    onChange([...items, { item: "", description: "", quantity: 1, unit_price: 0, total: 0 }]);
  };

  const updateItem = (index: number, field: keyof LineItem, value: string | number) => {
    const updated = items.map((it, i) => {
      if (i !== index) return it;
      const next = { ...it, [field]: value };
      next.total = (next.quantity || 0) * (next.unit_price || 0);
      return next;
    });
    onChange(updated);
  };

  const removeItem = (index: number) => {
    onChange(items.filter((_, i) => i !== index));
  };

  const total = items.reduce((s, i) => s + (i.quantity || 0) * (i.unit_price || 0), 0);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <Label className="text-xs font-semibold text-muted-foreground">ITEMS DEL PRESUPUESTO</Label>
        <Button type="button" variant="outline" size="sm" className="h-7 text-xs" onClick={addItem}>
          <Plus size={12} className="mr-1" /> Añadir item
        </Button>
      </div>
      {items.length > 0 && (
        <div className="space-y-2">
          {items.map((it, idx) => (
            <div key={idx} className="grid grid-cols-12 gap-2 items-start border rounded p-2 bg-muted/10">
              <div className="col-span-3 space-y-1">
                <Input placeholder="Item" value={it.item} className="h-8 text-xs"
                  onChange={(e) => updateItem(idx, "item", e.target.value)} />
              </div>
              <div className="col-span-3 space-y-1">
                <Input placeholder="Descripción" value={it.description} className="h-8 text-xs"
                  onChange={(e) => updateItem(idx, "description", e.target.value)} />
              </div>
              <div className="col-span-2 space-y-1">
                <Input type="number" placeholder="Cant." min={0} value={it.quantity} className="h-8 text-xs text-right"
                  onChange={(e) => updateItem(idx, "quantity", Number(e.target.value) || 0)} />
              </div>
              <div className="col-span-2 space-y-1">
                <Input type="number" placeholder="P. Unit." min={0} step="0.01" value={it.unit_price} className="h-8 text-xs text-right"
                  onChange={(e) => updateItem(idx, "unit_price", Number(e.target.value) || 0)} />
              </div>
              <div className="col-span-1 flex items-center justify-end h-8 text-xs font-semibold">
                {((it.quantity || 0) * (it.unit_price || 0)).toFixed(2)}
              </div>
              <div className="col-span-1 flex items-center justify-center">
                <Button variant="ghost" size="sm" className="h-6 w-6 p-0" onClick={() => removeItem(idx)}>
                  <Trash2 className="h-3 w-3 text-destructive" />
                </Button>
              </div>
            </div>
          ))}
          {items.length > 1 && (
            <div className="text-right text-xs font-semibold text-muted-foreground pr-14">
              Subtotal: {formatCurrency(total, currency)}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

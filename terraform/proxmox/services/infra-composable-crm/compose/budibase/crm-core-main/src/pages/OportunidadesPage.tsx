import { useState, useMemo } from "react";
import { useOportunidades, useOportunidadSnapshot, usePatchOportunidad, useCreatePendiente, usePatchPendiente } from "@/hooks/use-api";
import PresupuestosBlock from "@/components/PresupuestosBlock";
import { DataTable, Column } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Loader2, Clock, Eye, Pencil, X, Plus, Phone, Mail, Building2, User, Check, CalendarPlus, AlertTriangle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { formatDistanceToNow } from "date-fns";
import { es } from "date-fns/locale";
import { useQuery } from "@tanstack/react-query";
import * as api from "@/lib/api";

// ─── Canonical values ───────────────────────────────────────────
const ESTADOS = ["Nuevo", "En contacto", "Presupuesto enviado", "Negociación", "Ganado", "Perdido"] as const;
const LEAD_TAGS = ["Hot", "Warm", "Cold", "Qualified", "Unqualified"] as const;
const PRIORIDADES = ["Alta", "Media", "Baja"] as const;
const PACKS = ["GUARDIAN", "MOTOR", "FORTALEZA", "NO_ASIGNADO"] as const;
const NEXT_ACTIONS = ["SEND_EMAIL", "CALL", "BOOK_MEETING", "SEND_PROPOSAL", "FOLLOW_UP", "NO_ACTION"] as const;
const LOST_REASONS = ["Precio alto", "No responde", "Eligió competidor", "No tiene presupuesto", "Timing incorrecto", "No es fit", "Otro"] as const;
const URGENCIAS = ["Lo antes posible", "Durante este mes", "En los próximos 2-3 meses", "Aún no lo sé"] as const;
const CURRENCIES = ["EUR", "USD"] as const;

// ─── Helpers ────────────────────────────────────────────────────
function formatDate(v: unknown) {
  if (!v) return "—";
  try { return new Date(String(v)).toLocaleDateString("es-ES", { day: "2-digit", month: "short", year: "numeric" }); }
  catch { return "—"; }
}

function relativeTime(v: unknown) {
  if (!v) return "—";
  try { return formatDistanceToNow(new Date(String(v)), { addSuffix: true, locale: es }); }
  catch { return "—"; }
}

function formatCurrency(v: unknown, currency?: unknown) {
  if (v == null || v === "") return "—";
  const cur = String(currency ?? "EUR");
  return new Intl.NumberFormat("es-ES", { style: "currency", currency: cur }).format(Number(v));
}

// ─── Table columns ──────────────────────────────────────────────
const columns: Column[] = [
  { key: "deal_name", label: "Deal", render: (v) => <span className="font-medium">{String(v ?? "—")}</span> },
  { key: "contacto_nombre", label: "Contacto" },
  { key: "estado", label: "Estado", render: (v) => <StatusBadge value={v as string} /> },
  { key: "lead_tag", label: "Lead Tag", render: (v) => <StatusBadge value={v as string} /> },
  { key: "prioridad", label: "Prioridad", render: (v) => <StatusBadge value={v as string} type="priority" /> },
  { key: "pack", label: "Pack", render: (v) => v && v !== "NO_ASIGNADO" ? String(v) : <span className="text-muted-foreground">—</span> },
  { key: "deal_value", label: "Valor", render: (v, row) => formatCurrency(v, row.currency), className: "text-right" },
  { key: "probabilidad", label: "Prob.", render: (v) => v != null ? `${v}%` : "—", className: "text-right" },
  { key: "next_action", label: "Próxima acción", render: (v) => <StatusBadge value={v as string} /> },
  { key: "next_action_date", label: "Fecha acción", render: formatDate },
  { key: "updated_at", label: "Actualizado", render: relativeTime },
];

// ─── Main component ─────────────────────────────────────────────
export default function OportunidadesPage() {
  const { toast } = useToast();
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const [estado, setEstado] = useState("");
  const [leadTag, setLeadTag] = useState("");
  const [pack, setPack] = useState("");
  const [prioridad, setPrioridad] = useState("");
  const [urgencia, setUrgencia] = useState("");

  // Detail & edit
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [showEdit, setShowEdit] = useState(false);
  const [editData, setEditData] = useState<Record<string, unknown>>({});

  const { data, isLoading } = useOportunidades({
    q: search || undefined,
    estado: estado || undefined,
    lead_tag: leadTag || undefined,
    pack: pack || undefined,
    prioridad: prioridad || undefined,
    urgencia: urgencia || undefined,
    offset,
    limit: 50,
  });

  const { data: snapshot, isLoading: snapLoading } = useOportunidadSnapshot(selectedId);
  const patchMutation = usePatchOportunidad();
  const createPendiente = useCreatePendiente();
  const patchPendiente = usePatchPendiente();

  // Fetch allowed values from backend
  const { data: allowedValues } = useQuery({
    queryKey: ["pendientes-allowed-values"],
    queryFn: () => api.pendientes.allowedValues(),
    staleTime: 5 * 60 * 1000,
  });

  // Create task modal
  const [showCreateTask, setShowCreateTask] = useState(false);
  const [taskData, setTaskData] = useState<Record<string, unknown>>({ status: "TODO" });
  const [showDupConfirm, setShowDupConfirm] = useState(false);

  const op = (snapshot as Record<string, unknown>)?.oportunidad as Record<string, unknown> | undefined;
  const contacto = (snapshot as Record<string, unknown>)?.contacto as Record<string, unknown> | undefined;
  const historial = (snapshot as Record<string, unknown>)?.historial as Record<string, unknown>[] ?? [];
  const snapshotPendientes = ((snapshot as Record<string, unknown>)?.pendientes as Record<string, unknown>[]) ?? null;
  const snapshotPresupuestos = ((snapshot as Record<string, unknown>)?.presupuestos as Record<string, unknown>[]) ?? null;

  // Fallback: fetch pendientes separately if snapshot doesn't include them
  const { data: fallbackPendientesData } = useQuery({
    queryKey: ["pendientes", { oportunidad_id: selectedId }],
    queryFn: () => api.pendientes.list({ oportunidad_id: selectedId!, limit: 200, offset: 0 }),
    enabled: !!selectedId && snapshotPendientes === null,
  });

  // Fallback: fetch presupuestos separately if snapshot doesn't include them
  const { data: fallbackPresupuestosData } = useQuery({
    queryKey: ["presupuestos", { oportunidad_id: selectedId }],
    queryFn: () => api.presupuestos.list({ oportunidad_id: selectedId!, limit: 100, offset: 0 }),
    enabled: !!selectedId && snapshotPresupuestos === null,
  });

  const pendientes = snapshotPendientes ?? (fallbackPendientesData?.items as Record<string, unknown>[] ?? []);
  const presupuestosData = snapshotPresupuestos ?? (fallbackPresupuestosData?.items as Record<string, unknown>[] ?? []);

  // Sort pendientes: DONE last, then by due_date
  const sortedPendientes = useMemo(() => {
    return [...pendientes].sort((a, b) => {
      if (String(a.status) === "DONE" && String(b.status) !== "DONE") return 1;
      if (String(a.status) !== "DONE" && String(b.status) === "DONE") return -1;
      return 0;
    });
  }, [pendientes]);

  // Edit task modal
  const [editingTask, setEditingTask] = useState<Record<string, unknown> | null>(null);

  // Task helpers
  const getTaskDateClass = (t: Record<string, unknown>) => {
    if (String(t.status) === "DONE") return "done";
    if (!t.due_date) return "none";
    const d = new Date(String(t.due_date));
    d.setHours(0, 0, 0, 0);
    const today = new Date(); today.setHours(0, 0, 0, 0);
    const tomorrow = new Date(today); tomorrow.setDate(tomorrow.getDate() + 1);
    if (d < today) return "overdue";
    if (d.getTime() === today.getTime()) return "today";
    if (d.getTime() === tomorrow.getTime()) return "tomorrow";
    return "future";
  };

  const openCreateTask = () => {
    if (!op) return;
    const defaultDue = op.next_action_date
      ? String(op.next_action_date).substring(0, 10)
      : new Date(Date.now() + 2 * 86400000).toISOString().substring(0, 10);
    const defaultTitle = op.next_action
      ? `Follow-up: ${String(op.next_action)}`
      : "Follow-up oportunidad";
    const prioMap: Record<string, string> = { "Alta": "HIGH", "Media": "MEDIUM", "Baja": "LOW" };
    const descParts = [`Oportunidad: ${String(op.deal_name ?? "")}`, `Estado: ${String(op.estado ?? "")}`, `LeadTag: ${String(op.lead_tag ?? "")}`];
    if (op.notas_internas) descParts.push(`Notas: ${String(op.notas_internas)}`);

    setTaskData({
      title: defaultTitle,
      description: descParts.join("\n"),
      status: "TODO",
      priority: prioMap[String(op.prioridad ?? "")] ?? "",
      assigned_to: String(op.owner ?? "") || "Eduardo",
      due_date: defaultDue,
      due_time: "",
      reminder_enabled: false,
      reminder_datetime: "",
      contacto_id: op.contacto_id ?? contacto?.id ?? null,
      oportunidad_id: op.id,
    });
    setShowCreateTask(true);
  };

  const doCreateTask = async () => {
    const title = String(taskData.title ?? "").trim();
    if (!title) { toast({ title: "Título requerido", variant: "destructive" }); return; }
    const payload: Record<string, unknown> = { ...taskData, title };
    Object.keys(payload).forEach((k) => { if (payload[k] === "") payload[k] = undefined; });
    try {
      await createPendiente.mutateAsync(payload);
      toast({ title: "✓ Tarea creada" });
      setShowCreateTask(false);
      setShowDupConfirm(false);
    } catch (e) {
      const msg = String(e);
      if (msg.includes("400") || msg.includes("422")) {
        toast({ title: "Valor inválido", description: "Usa valores canónicos.", variant: "destructive" });
      } else {
        toast({ title: "Error", description: msg, variant: "destructive" });
      }
    }
  };

  const handleCreateTask = () => {
    const title = String(taskData.title ?? "").trim().toLowerCase();
    const hasDup = pendientes.some(
      (t) => String(t.status) !== "DONE" && String(t.title ?? "").trim().toLowerCase() === title
    );
    if (hasDup) { setShowDupConfirm(true); return; }
    doCreateTask();
  };

  const quickTaskDone = async (id: string) => {
    try {
      await patchPendiente.mutateAsync({ id, data: { status: "DONE" } });
      toast({ title: "✓ Tarea completada" });
    } catch (e) { toast({ title: "Error", description: String(e), variant: "destructive" }); }
  };

  const quickTaskSnooze = async (id: string, currentDueDate?: unknown) => {
    const base = currentDueDate ? new Date(String(currentDueDate)) : new Date();
    base.setDate(base.getDate() + 1);
    try {
      await patchPendiente.mutateAsync({ id, data: { due_date: base.toISOString().substring(0, 10) } });
      toast({ title: "Pospuesto +1 día" });
    } catch (e) { toast({ title: "Error", description: String(e), variant: "destructive" }); }
  };

  const handleEditTask = async () => {
    if (!editingTask) return;
    const id = String(editingTask._id);
    const payload: Record<string, unknown> = { ...editingTask };
    delete payload._id;
    Object.keys(payload).forEach((k) => { if (payload[k] === "") payload[k] = undefined; });
    try {
      await patchPendiente.mutateAsync({ id, data: payload });
      toast({ title: "✓ Tarea actualizada" });
      setEditingTask(null);
    } catch (e) {
      const msg = String(e);
      if (msg.includes("400")) {
        toast({ title: "Valor inválido", description: "Usa valores canónicos.", variant: "destructive" });
      } else {
        toast({ title: "Error", description: msg, variant: "destructive" });
      }
    }
  };

  // ─── Edit helpers ───
  const openEdit = () => {
    if (!op) return;
    setEditData({
      deal_name: op.deal_name ?? "",
      estado: op.estado ?? "",
      lead_tag: op.lead_tag ?? "",
      prioridad: op.prioridad ?? "",
      urgencia: op.urgencia ?? "",
      next_action: op.next_action ?? "",
      next_action_date: op.next_action_date ?? "",
      probabilidad: op.probabilidad ?? 0,
      deal_value: op.deal_value ?? "",
      currency: op.currency ?? "EUR",
      owner: op.owner ?? "",
      team: op.team ?? "",
      pack: op.pack ?? "",
      expected_close_date: op.expected_close_date ?? "",
      won_at: op.won_at ?? "",
      lost_at: op.lost_at ?? "",
      lost_reason: op.lost_reason ?? "",
      lost_reason_notes: op.lost_reason_notes ?? "",
      notas_internas: op.notas_internas ?? "",
      tags: op.tags ?? [],
    });
    setShowEdit(true);
  };

  const setField = (key: string, value: unknown) => {
    setEditData((d) => ({ ...d, [key]: value }));
  };

  const handleSave = async () => {
    if (!selectedId) return;
    const payload = { ...editData };

    // Validate probabilidad
    const prob = Number(payload.probabilidad);
    if (isNaN(prob) || prob < 0 || prob > 100) {
      toast({ title: "Error", description: "Probabilidad debe ser 0-100", variant: "destructive" });
      return;
    }
    payload.probabilidad = prob;

    // Clean conditional fields
    if (payload.estado !== "Perdido") {
      payload.lost_reason = null;
      payload.lost_reason_notes = null;
    }

    // Clean empty strings to null for optional fields
    for (const k of ["owner", "team", "next_action_date", "expected_close_date", "won_at", "lost_at", "notas_internas", "deal_value"]) {
      if (payload[k] === "") payload[k] = null;
    }

    // deal_value to number
    if (payload.deal_value != null && payload.deal_value !== null) {
      payload.deal_value = Number(payload.deal_value);
    }

    try {
      await patchMutation.mutateAsync({ id: selectedId, data: payload });
      toast({ title: "Actualizado", description: "Oportunidad guardada correctamente" });
      setShowEdit(false);
    } catch (e: unknown) {
      const msg = String(e);
      if (msg.includes("check") || msg.includes("constraint") || msg.includes("400")) {
        toast({ title: "Valor inválido", description: "Debe ser uno de los valores canónicos del sistema.", variant: "destructive" });
      } else {
        toast({ title: "Error", description: msg, variant: "destructive" });
      }
    }
  };

  // Tags management
  const [tagInput, setTagInput] = useState("");
  const currentTags = (editData.tags as string[]) ?? [];
  const addTag = () => {
    const t = tagInput.trim();
    if (t && !currentTags.includes(t)) {
      setField("tags", [...currentTags, t]);
    }
    setTagInput("");
  };
  const removeTag = (t: string) => setField("tags", currentTags.filter((x) => x !== t));

  const currentEstado = editData.estado as string;

  return (
    <>
      <PageHeader
        title="Oportunidades"
        subtitle={data ? `${data.total} oportunidades` : undefined}
        searchValue={search}
        onSearch={(q) => { setSearch(q); setOffset(0); }}
        searchPlaceholder="Buscar deals..."
      />

      {/* Filters */}
      <div className="mb-4 space-y-2">
        {/* Estado tabs */}
        <div className="flex gap-1 flex-wrap">
          {["", ...ESTADOS].map((e) => (
            <Button key={e || "all"} variant={estado === e ? "default" : "outline"} size="sm"
              onClick={() => { setEstado(e); setOffset(0); }}>{e || "Todos"}</Button>
          ))}
        </div>

        {/* Secondary filters */}
        <div className="flex gap-2 flex-wrap items-center">
          <div className="flex gap-1">
            {LEAD_TAGS.map((t) => (
              <Button key={t} variant={leadTag === t ? "secondary" : "ghost"} size="sm"
                onClick={() => { setLeadTag(leadTag === t ? "" : t); setOffset(0); }}>{t}</Button>
            ))}
          </div>

          <Select value={pack} onValueChange={(v) => { setPack(v === "_all" ? "" : v); setOffset(0); }}>
            <SelectTrigger className="w-40 h-8 text-xs">
              <SelectValue placeholder="Pack" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="_all">Todos los packs</SelectItem>
              {PACKS.map((p) => <SelectItem key={p} value={p}>{p}</SelectItem>)}
            </SelectContent>
          </Select>

          <Select value={prioridad} onValueChange={(v) => { setPrioridad(v === "_all" ? "" : v); setOffset(0); }}>
            <SelectTrigger className="w-36 h-8 text-xs">
              <SelectValue placeholder="Prioridad" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="_all">Toda prioridad</SelectItem>
              {PRIORIDADES.map((p) => <SelectItem key={p} value={p}>{p}</SelectItem>)}
            </SelectContent>
          </Select>

          <Select value={urgencia} onValueChange={(v) => { setUrgencia(v === "_all" ? "" : v); setOffset(0); }}>
            <SelectTrigger className="w-48 h-8 text-xs">
              <SelectValue placeholder="Urgencia" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="_all">Toda urgencia</SelectItem>
              {URGENCIAS.map((u) => <SelectItem key={u} value={u}>{u}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Data table */}
      <DataTable
        columns={columns}
        data={data?.items ?? []}
        total={data?.total}
        limit={data?.limit ?? 50}
        offset={offset}
        onPageChange={setOffset}
        onRowClick={(row) => { setSelectedId(row.id as string); setShowEdit(false); }}
        loading={isLoading}
      />

      {/* ─── DETAIL DIALOG ─────────────────────────────────── */}
      <Dialog open={!!selectedId && !showEdit} onOpenChange={(o) => { if (!o) setSelectedId(null); }}>
        <DialogContent className="max-w-3xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center justify-between gap-2">
              <span className="flex items-center gap-2">
                <Eye size={18} className="text-muted-foreground" />
                {op?.deal_name ? String(op.deal_name) : "Oportunidad"}
              </span>
              <div className="flex items-center gap-2">
                <Button size="sm" variant="outline" onClick={openEdit}>
                  <Pencil size={14} className="mr-1" /> Editar
                </Button>
              </div>
            </DialogTitle>
          </DialogHeader>

          {snapLoading ? (
            <div className="flex justify-center py-12"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
          ) : op ? (
            <div className="space-y-5">
              {/* Summary grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <FieldCard label="Estado" value={<StatusBadge value={op.estado as string} />} />
                <FieldCard label="Lead Tag" value={<StatusBadge value={op.lead_tag as string} />} />
                <FieldCard label="Prioridad" value={<StatusBadge value={op.prioridad as string} type="priority" />} />
                <FieldCard label="Probabilidad" value={op.probabilidad != null ? `${op.probabilidad}%` : null} />
                <FieldCard label="Valor" value={op.deal_value != null ? formatCurrency(op.deal_value, op.currency) : null} />
                <FieldCard label="Pack" value={op.pack !== "NO_ASIGNADO" ? op.pack : null} />
                <FieldCard label="Owner" value={op.owner} />
                <FieldCard label="Team" value={op.team} />
                <FieldCard label="Urgencia" value={op.urgencia} />
                <FieldCard label="Próxima acción" value={<StatusBadge value={op.next_action as string} />} />
                <FieldCard label="Fecha acción" value={formatDate(op.next_action_date)} />
                <FieldCard label="Cierre esperado" value={formatDate(op.expected_close_date)} />
                {op.estado === "Ganado" && <FieldCard label="Ganado el" value={formatDate(op.won_at)} />}
                {op.estado === "Perdido" && (
                  <>
                    <FieldCard label="Perdido el" value={formatDate(op.lost_at)} />
                    <FieldCard label="Razón pérdida" value={op.lost_reason} />
                  </>
                )}
              </div>

              {/* Tags */}
              {Array.isArray(op.tags) && op.tags.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-muted-foreground mb-1">TAGS</h4>
                  <div className="flex gap-1 flex-wrap">
                    {(op.tags as string[]).map((t) => <Badge key={t} variant="secondary">{t}</Badge>)}
                  </div>
                </div>
              )}

              {/* Notas internas */}
              {op.notas_internas && (
                <div>
                  <h4 className="text-xs font-semibold text-muted-foreground mb-1">NOTAS INTERNAS</h4>
                  <p className="text-sm whitespace-pre-wrap bg-muted/30 rounded p-2">{String(op.notas_internas)}</p>
                </div>
              )}

              {/* Contacto */}
              {contacto && (
                <div className="border rounded-lg p-3">
                  <h4 className="text-xs font-semibold text-muted-foreground mb-2">CONTACTO</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
                    <span className="flex items-center gap-1.5"><User size={14} className="text-muted-foreground" /> <strong>{String(contacto.nombre ?? "—")}</strong></span>
                    <span className="flex items-center gap-1.5"><Mail size={14} className="text-muted-foreground" /> {String(contacto.email ?? "—")}</span>
                    <span className="flex items-center gap-1.5"><Phone size={14} className="text-muted-foreground" /> {String(contacto.telefono ?? "—")}</span>
                    <span className="flex items-center gap-1.5"><Building2 size={14} className="text-muted-foreground" /> {String(contacto.company_name ?? "—")}</span>
                  </div>
                </div>
              )}

              {/* Pendientes (tareas) */}
              <div className="border rounded-lg p-3">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-xs font-semibold text-muted-foreground flex items-center gap-1">
                    <CalendarPlus size={14} /> PENDIENTES ({sortedPendientes.length})
                  </h4>
                  <Button size="sm" variant="outline" className="h-7 text-xs" onClick={openCreateTask}>
                    <Plus size={12} className="mr-1" /> Crear tarea
                  </Button>
                </div>
                {sortedPendientes.length === 0 ? (
                  <div className="text-center py-6">
                    <p className="text-sm text-muted-foreground mb-2">Sin tareas todavía</p>
                    <Button size="sm" variant="outline" onClick={openCreateTask}>
                      <Plus size={12} className="mr-1" /> Crear primera tarea
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-2 max-h-80 overflow-y-auto">
                    {sortedPendientes.map((t, i) => {
                      const dateClass = getTaskDateClass(t);
                      const isDone = dateClass === "done";
                      const rowBg = dateClass === "overdue" ? "bg-destructive/5 border-destructive/30" :
                        dateClass === "today" ? "bg-warning/5 border-warning/30" :
                        dateClass === "tomorrow" ? "bg-orange-50 border-orange-200 dark:bg-orange-950/20 dark:border-orange-800/30" :
                        isDone ? "bg-muted/20 border-border/30" : "bg-muted/30 border-border/50";
                      return (
                        <div key={i} className={`text-sm p-2.5 rounded border ${rowBg}`}>
                          <div className="flex items-start justify-between gap-2">
                            <div className="min-w-0 flex-1 space-y-1">
                              <div className="flex items-center gap-1.5 flex-wrap">
                                <span className={isDone ? "line-through text-muted-foreground" : "font-medium"}>{String(t.title ?? "—")}</span>
                                {dateClass === "overdue" && <Badge variant="destructive" className="text-[10px] px-1.5 py-0">Vencida</Badge>}
                                {dateClass === "today" && <Badge className="bg-warning text-warning-foreground text-[10px] px-1.5 py-0">Hoy</Badge>}
                                {dateClass === "tomorrow" && <Badge className="bg-orange-500 text-white text-[10px] px-1.5 py-0">Mañana</Badge>}
                                {isDone && <Badge variant="secondary" className="text-[10px] px-1.5 py-0">DONE</Badge>}
                              </div>
                              <div className="flex items-center gap-3 text-xs text-muted-foreground flex-wrap">
                                <StatusBadge value={String(t.status ?? "")} />
                                <StatusBadge value={String(t.priority ?? "")} type="priority" />
                                {t.assigned_to && <span>👤 {String(t.assigned_to)}</span>}
                                {t.due_date && <span>📅 {formatDate(t.due_date)}{t.due_time ? ` ${String(t.due_time).substring(0, 5)}` : ""}</span>}
                                {t.reminder_enabled && t.reminder_datetime && <span>🔔 {formatDate(t.reminder_datetime)}</span>}
                                <span>{relativeTime(t.updated_at)}</span>
                              </div>
                            </div>
                            <div className="flex gap-1 shrink-0">
                              {!isDone && (
                                <>
                                  <Button variant="ghost" size="sm" className="h-6 w-6 p-0" title="Marcar DONE"
                                    onClick={() => quickTaskDone(t.id as string)} disabled={patchPendiente.isPending}>
                                    <Check className="h-3 w-3 text-success" />
                                  </Button>
                                  <Button variant="ghost" size="sm" className="h-6 w-6 p-0" title="Posponer +1 día"
                                    onClick={() => quickTaskSnooze(t.id as string, t.due_date)} disabled={patchPendiente.isPending}>
                                    <Clock className="h-3 w-3 text-warning" />
                                  </Button>
                                </>
                              )}
                              <Button variant="ghost" size="sm" className="h-6 w-6 p-0" title="Editar tarea"
                                onClick={() => setEditingTask({
                                  _id: t.id,
                                  title: t.title ?? "",
                                  description: t.description ?? "",
                                  status: t.status ?? "TODO",
                                  priority: t.priority ?? "",
                                  assigned_to: t.assigned_to ?? "",
                                  due_date: t.due_date ? String(t.due_date).substring(0, 10) : "",
                                  due_time: t.due_time ? String(t.due_time).substring(0, 5) : "",
                                  reminder_enabled: !!t.reminder_enabled,
                                  reminder_datetime: t.reminder_datetime ? String(t.reminder_datetime).substring(0, 16) : "",
                                })}>
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

              {/* Presupuestos */}
              {op && (
                <PresupuestosBlock
                  presupuestos={presupuestosData}
                  oportunidad={op}
                  contacto={contacto}
                />
              )}

              {/* Historial */}
              {Array.isArray(historial) && historial.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-muted-foreground mb-2 flex items-center gap-1">
                    <Clock size={14} /> HISTORIAL ({historial.length})
                  </h4>
                  <div className="space-y-2 max-h-72 overflow-y-auto">
                    {historial.map((h, i) => (
                      <div key={i} className="text-sm p-2 rounded bg-muted/30 border border-border/50">
                        <div className="flex items-center gap-2 mb-0.5">
                          <span className="text-xs text-muted-foreground">{relativeTime(h.activity_date || h.created_at)}</span>
                          <span className="font-medium">{String(h.subject ?? "")}</span>
                        </div>
                        {h.notes && (
                          <pre className="text-xs text-muted-foreground whitespace-pre-wrap break-all mt-1">{String(h.notes)}</pre>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Metadata */}
              <div className="text-xs text-muted-foreground flex gap-4 pt-2 border-t">
                <span>Creado: {formatDate(op.created_at)}</span>
                <span>Actualizado: {relativeTime(op.updated_at)}</span>
              </div>
            </div>
          ) : null}
        </DialogContent>
      </Dialog>

      {/* ─── EDIT DIALOG ───────────────────────────────────── */}
      <Dialog open={showEdit} onOpenChange={(o) => { if (!o) setShowEdit(false); }}>
        <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Pencil size={18} className="text-muted-foreground" />
              Editar oportunidad
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            {/* Deal name */}
            <div className="space-y-1">
              <Label>Deal Name</Label>
              <Input value={String(editData.deal_name ?? "")}
                onChange={(e) => setField("deal_name", e.target.value)} />
            </div>

            <div className="grid grid-cols-2 gap-3">
              {/* Estado */}
              <EditSelect label="Estado" value={currentEstado} options={[...ESTADOS]}
                onChange={(v) => setField("estado", v)} />

              {/* Lead Tag */}
              <EditSelect label="Lead Tag" value={editData.lead_tag as string} options={[...LEAD_TAGS]}
                onChange={(v) => setField("lead_tag", v)} />

              {/* Prioridad */}
              <EditSelect label="Prioridad" value={editData.prioridad as string} options={[...PRIORIDADES]}
                onChange={(v) => setField("prioridad", v)} />

              {/* Pack */}
              <EditSelect label="Pack" value={editData.pack as string} options={[...PACKS]}
                onChange={(v) => setField("pack", v)} />

              {/* Urgencia */}
              <EditSelect label="Urgencia" value={editData.urgencia as string} options={[...URGENCIAS]}
                onChange={(v) => setField("urgencia", v)} nullable />

              {/* Next Action */}
              <EditSelect label="Próxima acción" value={editData.next_action as string} options={[...NEXT_ACTIONS]}
                onChange={(v) => setField("next_action", v)} />

              {/* Next Action Date */}
              <div className="space-y-1">
                <Label>Fecha próxima acción</Label>
                <Input type="date" value={String(editData.next_action_date ?? "")}
                  onChange={(e) => setField("next_action_date", e.target.value)} />
              </div>

              {/* Currency */}
              <EditSelect label="Moneda" value={editData.currency as string} options={[...CURRENCIES]}
                onChange={(v) => setField("currency", v)} />

              {/* Deal Value */}
              <div className="space-y-1">
                <Label>Valor del deal</Label>
                <Input type="number" step="0.01" value={String(editData.deal_value ?? "")}
                  onChange={(e) => setField("deal_value", e.target.value)} />
              </div>

              {/* Probabilidad */}
              <div className="space-y-1">
                <Label>Probabilidad (0-100)</Label>
                <Input type="number" min={0} max={100} value={String(editData.probabilidad ?? 0)}
                  onChange={(e) => setField("probabilidad", e.target.value)} />
              </div>

              {/* Expected close date */}
              <div className="space-y-1">
                <Label>Cierre esperado</Label>
                <Input type="date" value={String(editData.expected_close_date ?? "")}
                  onChange={(e) => setField("expected_close_date", e.target.value)} />
              </div>

              {/* Owner */}
              <div className="space-y-1">
                <Label>Owner</Label>
                <Input value={String(editData.owner ?? "")}
                  onChange={(e) => setField("owner", e.target.value)} />
              </div>

              {/* Team */}
              <div className="space-y-1">
                <Label>Team</Label>
                <Input value={String(editData.team ?? "")}
                  onChange={(e) => setField("team", e.target.value)} />
              </div>
            </div>

            {/* Won date (only if Ganado) */}
            {currentEstado === "Ganado" && (
              <div className="space-y-1">
                <Label>Fecha ganado (won_at)</Label>
                <Input type="datetime-local" value={String(editData.won_at ?? "").slice(0, 16)}
                  onChange={(e) => setField("won_at", e.target.value ? new Date(e.target.value).toISOString() : "")} />
              </div>
            )}

            {/* Lost fields (only if Perdido) */}
            {currentEstado === "Perdido" && (
              <div className="space-y-3 border rounded-lg p-3 bg-destructive/5">
                <div className="space-y-1">
                  <Label>Fecha perdido (lost_at)</Label>
                  <Input type="datetime-local" value={String(editData.lost_at ?? "").slice(0, 16)}
                    onChange={(e) => setField("lost_at", e.target.value ? new Date(e.target.value).toISOString() : "")} />
                </div>
                <EditSelect label="Razón pérdida" value={editData.lost_reason as string} options={[...LOST_REASONS]}
                  onChange={(v) => setField("lost_reason", v)} />
                <div className="space-y-1">
                  <Label>Notas razón pérdida</Label>
                  <Textarea value={String(editData.lost_reason_notes ?? "")}
                    onChange={(e) => setField("lost_reason_notes", e.target.value)} rows={2} />
                </div>
              </div>
            )}

            {/* Notas internas */}
            <div className="space-y-1">
              <Label>Notas internas</Label>
              <Textarea value={String(editData.notas_internas ?? "")}
                onChange={(e) => setField("notas_internas", e.target.value)} rows={3} />
            </div>

            {/* Tags */}
            <div className="space-y-1">
              <Label>Tags</Label>
              <div className="flex gap-1 flex-wrap mb-1">
                {currentTags.map((t) => (
                  <Badge key={t} variant="secondary" className="gap-1">
                    {t}
                    <button onClick={() => removeTag(t)} className="hover:text-destructive"><X size={12} /></button>
                  </Badge>
                ))}
              </div>
              <div className="flex gap-1">
                <Input placeholder="Añadir tag..." value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addTag(); } }}
                  className="h-8 text-sm" />
                <Button size="sm" variant="outline" onClick={addTag} className="h-8"><Plus size={14} /></Button>
              </div>
            </div>

            {/* Save */}
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setShowEdit(false)}>Cancelar</Button>
              <Button onClick={handleSave} disabled={patchMutation.isPending}>
                {patchMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}
                Guardar cambios
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* ─── CREATE TASK MODAL ─────────────────────────────── */}
      <Dialog open={showCreateTask} onOpenChange={(o) => { if (!o) { setShowCreateTask(false); setShowDupConfirm(false); } }}>
        <DialogContent className="max-w-lg max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <CalendarPlus size={18} className="text-success" /> Nueva tarea
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="rounded-lg border bg-muted/20 p-3 space-y-1 text-sm">
              <div className="flex gap-2"><span className="text-muted-foreground">Oportunidad:</span> <span className="font-medium">{String(op?.deal_name ?? "—")}</span></div>
              <div className="flex gap-2"><span className="text-muted-foreground">Contacto:</span> <span className="font-medium">{String(op?.contacto_nombre ?? contacto?.nombre ?? "—")}</span></div>
            </div>
            <div className="space-y-1">
              <Label>Título *</Label>
              <Input value={String(taskData.title ?? "")} onChange={(e) => setTaskData((p) => ({ ...p, title: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label>Descripción</Label>
              <Textarea rows={3} value={String(taskData.description ?? "")} onChange={(e) => setTaskData((p) => ({ ...p, description: e.target.value }))} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label>Estado</Label>
                <Select value={String(taskData.status ?? "TODO")} onValueChange={(v) => setTaskData((p) => ({ ...p, status: v }))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>{(allowedValues?.status ?? ["TODO", "IN_PROGRESS", "DONE", "CANCELLED"]).map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label>Prioridad</Label>
                <Select value={String(taskData.priority ?? "")} onValueChange={(v) => setTaskData((p) => ({ ...p, priority: v }))}>
                  <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
                  <SelectContent>{(allowedValues?.priority ?? ["HIGH", "MEDIUM", "LOW"]).map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label>Asignado a</Label>
                <Input value={String(taskData.assigned_to ?? "")} onChange={(e) => setTaskData((p) => ({ ...p, assigned_to: e.target.value }))} />
              </div>
              <div className="space-y-1">
                <Label>Fecha límite</Label>
                <Input type="date" value={String(taskData.due_date ?? "")} onChange={(e) => setTaskData((p) => ({ ...p, due_date: e.target.value || null }))} />
              </div>
              <div className="space-y-1">
                <Label>Hora</Label>
                <Input type="time" value={String(taskData.due_time ?? "").substring(0, 5)} onChange={(e) => setTaskData((p) => ({ ...p, due_time: e.target.value ? e.target.value + ":00" : null }))} />
                <div className="flex gap-1 mt-1">
                  {["09:00", "10:00", "14:00"].map((t) => (
                    <Button
                      key={t}
                      type="button"
                      variant="outline"
                      size="sm"
                      className="h-6 px-2 text-[10px] text-muted-foreground"
                      onClick={() => setTaskData((p) => ({ ...p, due_time: t + ":00" }))}
                    >
                      {t}
                    </Button>
                  ))}
                </div>
              </div>
              <div className="space-y-1 flex items-end">
                <div className="flex items-center gap-2">
                  <Switch checked={!!taskData.reminder_enabled} onCheckedChange={(v) => setTaskData((p) => ({ ...p, reminder_enabled: v }))} />
                  <Label className="text-sm">Recordatorio</Label>
                </div>
              </div>
            </div>
            {taskData.reminder_enabled && (
              <div className="space-y-1">
                <Label>Fecha/hora recordatorio</Label>
                <Input type="datetime-local" value={String(taskData.reminder_datetime ?? "").substring(0, 16)} onChange={(e) => setTaskData((p) => ({ ...p, reminder_datetime: e.target.value ? new Date(e.target.value).toISOString() : null }))} />
              </div>
            )}
            {showDupConfirm && (
              <div className="flex items-start gap-2 rounded-lg border border-warning bg-warning/10 p-3">
                <AlertTriangle className="h-5 w-5 text-warning shrink-0 mt-0.5" />
                <div className="space-y-2">
                  <p className="text-sm font-medium">Ya existe una tarea similar abierta. ¿Crear otra?</p>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" onClick={() => setShowDupConfirm(false)}>No</Button>
                    <Button size="sm" onClick={doCreateTask} disabled={createPendiente.isPending}>Sí, crear</Button>
                  </div>
                </div>
              </div>
            )}
            {!showDupConfirm && (
              <Button onClick={handleCreateTask} disabled={createPendiente.isPending || !String(taskData.title ?? "").trim()} className="w-full bg-success hover:bg-success/90 text-success-foreground">
                {createPendiente.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Crear tarea"}
              </Button>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* ─── EDIT TASK MODAL ───────────────────────────────── */}
      <Dialog open={!!editingTask} onOpenChange={(o) => { if (!o) setEditingTask(null); }}>
        <DialogContent className="max-w-lg max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Pencil size={18} className="text-muted-foreground" /> Editar tarea
            </DialogTitle>
          </DialogHeader>
          {editingTask && (
            <div className="space-y-4">
              <div className="space-y-1">
                <Label>Título *</Label>
                <Input value={String(editingTask.title ?? "")} onChange={(e) => setEditingTask((p) => p ? { ...p, title: e.target.value } : p)} />
              </div>
              <div className="space-y-1">
                <Label>Descripción</Label>
                <Textarea rows={3} value={String(editingTask.description ?? "")} onChange={(e) => setEditingTask((p) => p ? { ...p, description: e.target.value } : p)} />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <Label>Estado</Label>
                  <Select value={String(editingTask.status ?? "TODO")} onValueChange={(v) => setEditingTask((p) => p ? { ...p, status: v } : p)}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>{(allowedValues?.status ?? ["TODO", "IN_PROGRESS", "DONE", "CANCELLED"]).map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <Label>Prioridad</Label>
                  <Select value={String(editingTask.priority ?? "")} onValueChange={(v) => setEditingTask((p) => p ? { ...p, priority: v } : p)}>
                    <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
                    <SelectContent>{(allowedValues?.priority ?? ["HIGH", "MEDIUM", "LOW"]).map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <Label>Asignado a</Label>
                  <Input value={String(editingTask.assigned_to ?? "")} onChange={(e) => setEditingTask((p) => p ? { ...p, assigned_to: e.target.value } : p)} />
                </div>
                <div className="space-y-1">
                  <Label>Fecha límite</Label>
                  <Input type="date" value={String(editingTask.due_date ?? "")} onChange={(e) => setEditingTask((p) => p ? { ...p, due_date: e.target.value } : p)} />
                </div>
                <div className="space-y-1">
                  <Label>Hora</Label>
                  <Input type="time" value={String(editingTask.due_time ?? "").substring(0, 5)} onChange={(e) => setEditingTask((p) => p ? { ...p, due_time: e.target.value } : p)} />
                  <div className="flex gap-1 mt-1">
                    {["09:00", "10:00", "14:00"].map((t) => (
                      <Button
                        key={t}
                        type="button"
                        variant="outline"
                        size="sm"
                        className="h-6 px-2 text-[10px] text-muted-foreground"
                        onClick={() => setEditingTask((p) => p ? { ...p, due_time: t } : p)}
                      >
                        {t}
                      </Button>
                    ))}
                  </div>
                </div>
                <div className="space-y-1 flex items-end">
                  <div className="flex items-center gap-2">
                    <Switch checked={!!editingTask.reminder_enabled} onCheckedChange={(v) => setEditingTask((p) => p ? { ...p, reminder_enabled: v } : p)} />
                    <Label className="text-sm">Recordatorio</Label>
                  </div>
                </div>
              </div>
              {editingTask.reminder_enabled && (
                <div className="space-y-1">
                  <Label>Fecha/hora recordatorio</Label>
                  <Input type="datetime-local" value={String(editingTask.reminder_datetime ?? "")} onChange={(e) => setEditingTask((p) => p ? { ...p, reminder_datetime: e.target.value } : p)} />
                </div>
              )}
              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" onClick={() => setEditingTask(null)}>Cancelar</Button>
                <Button onClick={handleEditTask} disabled={patchPendiente.isPending || !String(editingTask.title ?? "").trim()}>
                  {patchPendiente.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}
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

// ─── Sub-components ─────────────────────────────────────────────

function FieldCard({ label, value }: { label: string; value: unknown }) {
  const display = value != null && value !== "" && value !== "—" ? (
    typeof value === "object" ? value as React.ReactNode : String(value)
  ) : <span className="text-muted-foreground">—</span>;
  return (
    <div className="rounded-md border bg-muted/20 px-3 py-2">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="text-sm font-medium">{display}</div>
    </div>
  );
}

function EditSelect({ label, value, options, onChange, nullable }: {
  label: string; value: string; options: string[];
  onChange: (v: string) => void; nullable?: boolean;
}) {
  return (
    <div className="space-y-1">
      <Label>{label}</Label>
      <Select value={value || "_empty"} onValueChange={(v) => onChange(v === "_empty" ? "" : v)}>
        <SelectTrigger><SelectValue /></SelectTrigger>
        <SelectContent>
          {nullable && <SelectItem value="_empty">— Sin valor —</SelectItem>}
          {options.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
        </SelectContent>
      </Select>
    </div>
  );
}

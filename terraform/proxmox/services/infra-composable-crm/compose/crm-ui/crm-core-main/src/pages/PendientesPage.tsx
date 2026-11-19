import { useState, useMemo } from "react";
import { usePendientes, usePatchPendiente, useCreatePendiente } from "@/hooks/use-api";
import { DataTable, Column } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Loader2, AlertTriangle, CalendarClock, CheckCircle2, ListTodo, Eye, Pencil, Check, Clock, Plus } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useQuery } from "@tanstack/react-query";
import * as api from "@/lib/api";

// ── helpers ──

function formatDate(v: unknown) {
  if (!v) return "—";
  try {
    return new Date(String(v)).toLocaleDateString("es-ES", { day: "2-digit", month: "short", year: "numeric" });
  } catch {
    return "—";
  }
}

function formatRelative(v: unknown) {
  if (!v) return "—";
  try {
    const d = new Date(String(v));
    const diff = Date.now() - d.getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return "ahora";
    if (mins < 60) return `hace ${mins}m`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `hace ${hrs}h`;
    const days = Math.floor(hrs / 24);
    if (days < 30) return `hace ${days}d`;
    return formatDate(v);
  } catch {
    return "—";
  }
}

function isToday(dateStr: string) {
  const d = new Date(dateStr);
  const now = new Date();
  return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth() && d.getDate() === now.getDate();
}

function isOverdue(dateStr: string) {
  const d = new Date(dateStr);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return d < today;
}

function formatDueDate(row: Record<string, unknown>) {
  const due = row.due_date as string | null;
  if (!due) return <span className="text-muted-foreground">—</span>;
  const time = row.due_time as string | null;
  const status = row.status as string;
  const overdue = status !== "DONE" && isOverdue(due);
  const today = isToday(due);
  const label = formatDate(due) + (time ? ` ${String(time).substring(0, 5)}` : "");
  if (overdue) return <span className="text-destructive font-medium">{label}</span>;
  if (today) return <span className="text-warning font-medium">{label}</span>;
  return <span>{label}</span>;
}

// ── columns ──

const columns: Column[] = [
  {
    key: "title",
    label: "Tarea",
    render: (v, row) => {
      const status = row.status as string;
      return (
        <span className={status === "DONE" ? "line-through text-muted-foreground" : "font-medium"}>
          {String(v ?? "—")}
        </span>
      );
    },
  },
  { key: "contacto_nombre", label: "Contacto", render: (v) => String(v ?? "—") },
  { key: "status", label: "Estado", render: (v) => <StatusBadge value={v as string} /> },
  { key: "priority", label: "Prioridad", render: (v) => <StatusBadge value={v as string} type="priority" /> },
  { key: "assigned_to", label: "Asignado", render: (v) => String(v ?? "—") },
  {
    key: "due_date",
    label: "Fecha límite",
    render: (_v, row) => formatDueDate(row),
  },
  {
    key: "reminder_enabled",
    label: "Recordatorio",
    render: (v, row) => {
      if (!v) return <span className="text-muted-foreground">—</span>;
      const dt = row.reminder_datetime as string | null;
      return <span className="text-xs">{dt ? formatDate(dt) : "Sí"}</span>;
    },
  },
  { key: "updated_at", label: "Actualizado", render: (v) => formatRelative(v) },
];

// ── KPI Card ──

function KpiCard({ icon: Icon, label, value, color }: { icon: React.ElementType; label: string; value: number; color: string }) {
  return (
    <div className="flex items-center gap-3 rounded-lg border bg-card p-4">
      <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${color}`}>
        <Icon className="h-5 w-5" />
      </div>
      <div>
        <p className="text-2xl font-bold">{value}</p>
        <p className="text-xs text-muted-foreground">{label}</p>
      </div>
    </div>
  );
}

// ── Main ──

export default function PendientesPage() {
  const { toast } = useToast();
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const [statusFilter, setStatusFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [assignedFilter, setAssignedFilter] = useState("");

  // detail drawer
  const [detailId, setDetailId] = useState<string | null>(null);
  // edit modal
  const [editRow, setEditRow] = useState<Record<string, unknown> | null>(null);
  const [editData, setEditData] = useState<Record<string, unknown>>({});
  // create modal
  const [createOpen, setCreateOpen] = useState(false);
  const [createData, setCreateData] = useState<Record<string, unknown>>({ status: "TODO" });

  const { data, isLoading } = usePendientes({
    q: search || undefined,
    status: statusFilter || undefined,
    priority: priorityFilter || undefined,
    assigned_to: assignedFilter || undefined,
    offset,
    limit: 50,
  });

  const { data: detail, isLoading: detailLoading } = useQuery({
    queryKey: ["pendiente-detail", detailId],
    queryFn: () => api.pendientes.get(detailId!),
    enabled: !!detailId,
  });

  const patchMutation = usePatchPendiente();
  const createMutation = useCreatePendiente();

  // Fetch allowed values from backend
  const { data: allowedValues } = useQuery({
    queryKey: ["pendientes-allowed-values"],
    queryFn: () => api.pendientes.allowedValues(),
    staleTime: 5 * 60 * 1000,
  });

  // ── derive dynamic filter options from items ──
  const items = data?.items ?? [];
  const statusOptions = useMemo(() => {
    const set = new Set<string>();
    items.forEach((r) => r.status && set.add(String(r.status)));
    return Array.from(set);
  }, [items]);

  const priorityOptions = useMemo(() => {
    const set = new Set<string>();
    items.forEach((r) => r.priority && set.add(String(r.priority)));
    return Array.from(set);
  }, [items]);

  const assignedOptions = useMemo(() => {
    const set = new Set<string>();
    items.forEach((r) => r.assigned_to && set.add(String(r.assigned_to)));
    return Array.from(set);
  }, [items]);

  // ── KPIs (computed from current page data) ──
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  const kpis = useMemo(() => {
    let overdue = 0, dueToday = 0, open = 0, done = 0;
    const sevenDaysAgo = Date.now() - 7 * 86400000;
    items.forEach((r) => {
      const st = String(r.status ?? "");
      if (st === "DONE") {
        const ca = r.completed_at || r.updated_at;
        if (ca && new Date(String(ca)).getTime() > sevenDaysAgo) done++;
        return;
      }
      open++;
      const dd = r.due_date as string | null;
      if (dd) {
        if (isToday(dd)) dueToday++;
        else if (isOverdue(dd)) overdue++;
      }
    });
    return { overdue, dueToday, open, done };
  }, [items]);

  // ── quick actions ──
  const quickDone = async (id: string) => {
    try {
      await patchMutation.mutateAsync({ id, data: { status: "DONE" } });
      toast({ title: "✓ Tarea completada" });
    } catch (e) {
      toast({ title: "Error", description: String(e), variant: "destructive" });
    }
  };

  const quickSnooze = async (id: string, currentDue: string | null) => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const newDue = tomorrow.toISOString().substring(0, 10);
    try {
      await patchMutation.mutateAsync({ id, data: { due_date: newDue } });
      toast({ title: "Pospuesto a mañana" });
    } catch (e) {
      toast({ title: "Error", description: String(e), variant: "destructive" });
    }
  };

  // ── save edit ──
  const handleSave = async () => {
    if (!editRow?.id) return;
    try {
      await patchMutation.mutateAsync({ id: editRow.id as string, data: editData });
      toast({ title: "Actualizado", description: "Tarea guardada" });
      setEditRow(null);
      setEditData({});
    } catch (e: unknown) {
      const msg = String(e);
      if (msg.includes("400") || msg.includes("422")) {
        toast({ title: "Valor inválido", description: "Usa valores canónicos del sistema.", variant: "destructive" });
      } else {
        toast({ title: "Error", description: msg, variant: "destructive" });
      }
    }
  };

  // ── create task ──
  const handleCreate = async () => {
    const title = String(createData.title ?? "").trim();
    if (!title) {
      toast({ title: "Título requerido", variant: "destructive" });
      return;
    }
    const payload: Record<string, unknown> = { ...createData, title };
    // Clean empty strings
    Object.keys(payload).forEach((k) => {
      if (payload[k] === "") payload[k] = undefined;
    });
    try {
      await createMutation.mutateAsync(payload);
      toast({ title: "✓ Tarea creada" });
      setCreateOpen(false);
      setCreateData({ status: "TODO" });
    } catch (e: unknown) {
      const msg = String(e);
      if (msg.includes("400") || msg.includes("422")) {
        toast({ title: "Valor inválido", description: "Usa valores canónicos del sistema.", variant: "destructive" });
      } else {
        toast({ title: "Error", description: msg, variant: "destructive" });
      }
    }
  };

  // ── augmented columns with actions ──
  const allColumns: Column[] = [
    ...columns,
    {
      key: "_actions",
      label: "",
      render: (_v, row) => (
        <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
          {String(row.status) !== "DONE" && (
            <>
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0" title="Marcar DONE"
                onClick={() => quickDone(row.id as string)} disabled={patchMutation.isPending}>
                <Check className="h-3.5 w-3.5 text-success" />
              </Button>
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0" title="Posponer 1 día"
                onClick={() => quickSnooze(row.id as string, row.due_date as string | null)} disabled={patchMutation.isPending}>
                <Clock className="h-3.5 w-3.5 text-warning" />
              </Button>
            </>
          )}
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0" title="Ver detalle"
            onClick={() => setDetailId(row.id as string)}>
            <Eye className="h-3.5 w-3.5" />
          </Button>
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0" title="Editar"
            onClick={() => { setEditRow(row); setEditData({}); }}>
            <Pencil className="h-3.5 w-3.5" />
          </Button>
        </div>
      ),
    },
  ];

  const d = editRow; // for edit modal defaults

  return (
    <>
      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <KpiCard icon={AlertTriangle} label="Vencidas" value={kpis.overdue} color="bg-destructive/15 text-destructive" />
        <KpiCard icon={CalendarClock} label="Hoy" value={kpis.dueToday} color="bg-warning/15 text-warning" />
        <KpiCard icon={ListTodo} label="Abiertas" value={kpis.open} color="bg-info/15 text-info" />
        <KpiCard icon={CheckCircle2} label="Done (7d)" value={kpis.done} color="bg-success/15 text-success" />
      </div>

      <PageHeader
        title="Pendientes"
        subtitle={data ? `${data.total} tareas` : undefined}
        searchValue={search}
        onSearch={(q) => { setSearch(q); setOffset(0); }}
        searchPlaceholder="Buscar tareas..."
        actions={
          <div className="flex gap-2 flex-wrap items-center">
            <Button size="sm" className="bg-success hover:bg-success/90 text-success-foreground" onClick={() => { setCreateOpen(true); setCreateData({ status: "TODO" }); }}>
              <Plus className="h-4 w-4 mr-1" /> Nueva tarea
            </Button>
            {/* Status chips */}
            <div className="flex gap-1">
              <Button variant={statusFilter === "" ? "default" : "outline"} size="sm"
                onClick={() => { setStatusFilter(""); setOffset(0); }}>Todos</Button>
              {statusOptions.map((s) => (
                <Button key={s} variant={statusFilter === s ? "default" : "outline"} size="sm"
                  onClick={() => { setStatusFilter(s); setOffset(0); }}>{s}</Button>
              ))}
            </div>
            {/* Priority chips */}
            {priorityOptions.length > 0 && (
              <div className="flex gap-1">
                {priorityOptions.map((p) => (
                  <Button key={p} variant={priorityFilter === p ? "default" : "outline"} size="sm"
                    onClick={() => { setPriorityFilter(priorityFilter === p ? "" : p); setOffset(0); }}>{p}</Button>
                ))}
              </div>
            )}
            {/* Assigned dropdown */}
            {assignedOptions.length > 0 && (
              <Select value={assignedFilter} onValueChange={(v) => { setAssignedFilter(v === "__all__" ? "" : v); setOffset(0); }}>
                <SelectTrigger className="w-[140px] h-8 text-xs">
                  <SelectValue placeholder="Asignado" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="__all__">Todos</SelectItem>
                  {assignedOptions.map((a) => <SelectItem key={a} value={a}>{a}</SelectItem>)}
                </SelectContent>
              </Select>
            )}
          </div>
        }
      />

      <DataTable
        columns={allColumns}
        data={items}
        total={data?.total}
        limit={data?.limit ?? 50}
        offset={offset}
        onPageChange={setOffset}
        loading={isLoading}
      />

      {/* ── Drawer Detalle ── */}
      <Sheet open={!!detailId} onOpenChange={(o) => !o && setDetailId(null)}>
        <SheetContent className="sm:max-w-lg overflow-y-auto">
          <SheetHeader>
            <SheetTitle>Detalle de tarea</SheetTitle>
          </SheetHeader>
          {detailLoading ? (
            <div className="flex justify-center py-12"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
          ) : detail ? (
            <div className="space-y-6 mt-4">
              <div>
                <h3 className="text-lg font-semibold">{String(detail.title ?? "—")}</h3>
                {detail.description && <p className="text-sm text-muted-foreground mt-1">{String(detail.description)}</p>}
              </div>

              <div className="grid grid-cols-2 gap-3 text-sm">
                <div><span className="text-muted-foreground">Estado:</span> <StatusBadge value={detail.status as string} /></div>
                <div><span className="text-muted-foreground">Prioridad:</span> <StatusBadge value={detail.priority as string} type="priority" /></div>
                <div><span className="text-muted-foreground">Asignado:</span> {String(detail.assigned_to ?? "—")}</div>
                <div><span className="text-muted-foreground">Contacto:</span> {String(detail.contacto_nombre ?? "—")}</div>
                <div><span className="text-muted-foreground">Fecha límite:</span> {formatDate(detail.due_date)} {detail.due_time ? String(detail.due_time).substring(0, 5) : ""}</div>
                <div><span className="text-muted-foreground">Completada:</span> {formatDate(detail.completed_at)}</div>
                <div><span className="text-muted-foreground">Recordatorio:</span> {detail.reminder_enabled ? (detail.reminder_datetime ? formatDate(detail.reminder_datetime) : "Sí") : "No"}</div>
                <div><span className="text-muted-foreground">Creado por:</span> {String(detail.created_by ?? "—")}</div>
                <div><span className="text-muted-foreground">Creado:</span> {formatDate(detail.created_at)}</div>
                <div><span className="text-muted-foreground">Actualizado:</span> {formatRelative(detail.updated_at)}</div>
              </div>

              {(detail.contacto_id || detail.oportunidad_id) && (
                <div className="text-xs text-muted-foreground space-y-1 border-t pt-3">
                  {detail.contacto_id && <p>contacto_id: {String(detail.contacto_id)}</p>}
                  {detail.oportunidad_id && <p>oportunidad_id: {String(detail.oportunidad_id)}</p>}
                  {detail.linkedin_lead_id && <p>linkedin_lead_id: {String(detail.linkedin_lead_id)}</p>}
                </div>
              )}

              <div className="flex gap-2 pt-2">
                {String(detail.status) !== "DONE" && (
                  <Button variant="default" size="sm" onClick={() => quickDone(detail.id as string)} disabled={patchMutation.isPending}>
                    <Check className="h-4 w-4 mr-1" /> Marcar DONE
                  </Button>
                )}
                <Button variant="outline" size="sm" onClick={() => { setDetailId(null); setEditRow(detail); setEditData({}); }}>
                  <Pencil className="h-4 w-4 mr-1" /> Editar
                </Button>
              </div>
            </div>
          ) : null}
        </SheetContent>
      </Sheet>

      {/* ── Modal Edición ── */}
      <Dialog open={!!editRow} onOpenChange={(o) => !o && setEditRow(null)}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Editar tarea</DialogTitle>
          </DialogHeader>
          {d ? (
            <div className="space-y-4">
              <div className="space-y-1">
                <Label>Título</Label>
                <Input defaultValue={String(d.title ?? "")}
                  onChange={(e) => setEditData((p) => ({ ...p, title: e.target.value }))} />
              </div>
              <div className="space-y-1">
                <Label>Descripción</Label>
                <Textarea defaultValue={String(d.description ?? "")} rows={3}
                  onChange={(e) => setEditData((p) => ({ ...p, description: e.target.value }))} />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <Label>Estado</Label>
                  <Select defaultValue={String(d.status ?? "")}
                    onValueChange={(v) => setEditData((p) => ({ ...p, status: v }))}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                    {(allowedValues?.status ?? ["TODO", "IN_PROGRESS", "DONE", "CANCELLED"]).map((s) =>
                      <SelectItem key={s} value={s}>{s}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label>Prioridad</Label>
                <Select defaultValue={String(d.priority ?? "")}
                  onValueChange={(v) => setEditData((p) => ({ ...p, priority: v }))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {(allowedValues?.priority ?? ["HIGH", "MEDIUM", "LOW"]).map((s) =>
                      <SelectItem key={s} value={s}>{s}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <Label>Asignado a</Label>
                  <Input defaultValue={String(d.assigned_to ?? "")}
                    onChange={(e) => setEditData((p) => ({ ...p, assigned_to: e.target.value }))} />
                </div>
                <div className="space-y-1">
                  <Label>Fecha límite</Label>
                  <Input type="date" defaultValue={d.due_date ? String(d.due_date).substring(0, 10) : ""}
                    onChange={(e) => setEditData((p) => ({ ...p, due_date: e.target.value || null }))} />
                </div>
                <div className="space-y-1">
                  <Label>Hora</Label>
                  <Input
                    type="time"
                    key={String(editData.due_time ?? d.due_time ?? "")}
                    defaultValue={String(editData.due_time ?? d.due_time ?? "").substring(0, 5)}
                    onChange={(e) => setEditData((p) => ({ ...p, due_time: e.target.value || null }))}
                  />
                  <div className="flex gap-1 mt-1">
                    {["09:00", "10:00", "14:00"].map((t) => (
                      <Button
                        key={t}
                        type="button"
                        variant="outline"
                        size="sm"
                        className="h-6 px-2 text-[10px] text-muted-foreground"
                        onClick={() => setEditData((p) => ({ ...p, due_time: t }))}
                      >
                        {t}
                      </Button>
                    ))}
                  </div>
                </div>
                <div className="space-y-1 flex items-end gap-2">
                  <div className="flex items-center gap-2">
                    <Switch
                      defaultChecked={!!d.reminder_enabled}
                      onCheckedChange={(v) => setEditData((p) => ({ ...p, reminder_enabled: v }))}
                    />
                    <Label className="text-sm">Recordatorio</Label>
                  </div>
                </div>
              </div>
              {(editData.reminder_enabled ?? d.reminder_enabled) && (
                <div className="space-y-1">
                  <Label>Fecha/hora recordatorio</Label>
                  <Input type="datetime-local"
                    defaultValue={d.reminder_datetime ? String(d.reminder_datetime).substring(0, 16) : ""}
                    onChange={(e) => setEditData((p) => ({ ...p, reminder_datetime: e.target.value ? new Date(e.target.value).toISOString() : null }))} />
                </div>
              )}
              <Button onClick={handleSave} disabled={patchMutation.isPending || Object.keys(editData).length === 0} className="w-full">
                {patchMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Guardar cambios"}
              </Button>
            </div>
          ) : null}
        </DialogContent>
      </Dialog>

      {/* ── Modal Nueva Tarea ── */}
      <Dialog open={createOpen} onOpenChange={(o) => { if (!o) { setCreateOpen(false); setCreateData({ status: "TODO" }); } }}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Nueva tarea</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-1">
              <Label>Título *</Label>
              <Input placeholder="Ej: Llamar al cliente" value={String(createData.title ?? "")}
                onChange={(e) => setCreateData((p) => ({ ...p, title: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label>Descripción</Label>
              <Textarea placeholder="Detalles opcionales..." rows={3}
                value={String(createData.description ?? "")}
                onChange={(e) => setCreateData((p) => ({ ...p, description: e.target.value }))} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label>Estado</Label>
                <Select value={String(createData.status ?? "TODO")}
                  onValueChange={(v) => setCreateData((p) => ({ ...p, status: v }))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {(allowedValues?.status ?? ["TODO", "IN_PROGRESS", "DONE", "CANCELLED"]).map((s) =>
                      <SelectItem key={s} value={s}>{s}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label>Prioridad</Label>
                <Select value={String(createData.priority ?? "")}
                  onValueChange={(v) => setCreateData((p) => ({ ...p, priority: v }))}>
                  <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
                  <SelectContent>
                    {(allowedValues?.priority ?? ["HIGH", "MEDIUM", "LOW"]).map((s) =>
                      <SelectItem key={s} value={s}>{s}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label>Asignado a</Label>
                <Input placeholder="Nombre" value={String(createData.assigned_to ?? "")}
                  onChange={(e) => setCreateData((p) => ({ ...p, assigned_to: e.target.value }))} />
              </div>
              <div className="space-y-1">
                <Label>Fecha límite</Label>
                <Input type="date" value={String(createData.due_date ?? "")}
                  onChange={(e) => setCreateData((p) => ({ ...p, due_date: e.target.value || null }))} />
              </div>
              <div className="space-y-1">
                <Label>Hora</Label>
                <Input type="time" value={String(createData.due_time ?? "").substring(0, 5)}
                  onChange={(e) => setCreateData((p) => ({ ...p, due_time: e.target.value ? e.target.value + ":00" : null }))} />
                <div className="flex gap-1 mt-1">
                  {["09:00", "10:00", "14:00"].map((t) => (
                    <Button
                      key={t}
                      type="button"
                      variant="outline"
                      size="sm"
                      className="h-6 px-2 text-[10px] text-muted-foreground"
                      onClick={() => setCreateData((p) => ({ ...p, due_time: t + ":00" }))}
                    >
                      {t}
                    </Button>
                  ))}
                </div>
              </div>
              <div className="space-y-1">
                <Label>Contacto ID</Label>
                <Input placeholder="UUID (opcional)" value={String(createData.contacto_id ?? "")}
                  onChange={(e) => setCreateData((p) => ({ ...p, contacto_id: e.target.value || null }))} />
              </div>
              <div className="space-y-1">
                <Label>Oportunidad ID</Label>
                <Input placeholder="UUID (opcional)" value={String(createData.oportunidad_id ?? "")}
                  onChange={(e) => setCreateData((p) => ({ ...p, oportunidad_id: e.target.value || null }))} />
              </div>
              <div className="space-y-1 flex items-end gap-2">
                <div className="flex items-center gap-2">
                  <Switch
                    checked={!!createData.reminder_enabled}
                    onCheckedChange={(v) => setCreateData((p) => ({ ...p, reminder_enabled: v }))}
                  />
                  <Label className="text-sm">Recordatorio</Label>
                </div>
              </div>
            </div>
            {createData.reminder_enabled && (
              <div className="space-y-1">
                <Label>Fecha/hora recordatorio</Label>
                <Input type="datetime-local" value={String(createData.reminder_datetime ?? "").substring(0, 16)}
                  onChange={(e) => setCreateData((p) => ({ ...p, reminder_datetime: e.target.value ? new Date(e.target.value).toISOString() : null }))} />
              </div>
            )}
            <Button onClick={handleCreate} disabled={createMutation.isPending || !String(createData.title ?? "").trim()} className="w-full">
              {createMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Crear tarea"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}

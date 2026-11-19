import { useState, useEffect } from "react";
import { useProveedores, useCreateProveedor, usePatchProveedor } from "@/hooks/use-api";
import { useGastos } from "@/hooks/use-api";
import { DataTable, Column } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, Loader2, Filter, ExternalLink, Mail, Phone, Globe, FileText, Pencil } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";

const TIPOS = [
  "TECNOLOGIA", "MARKETING", "SERVICIOS", "OFICINA", "FORMACION",
  "LEGAL", "FINANCIERO", "TELECOMUNICACIONES", "TRANSPORTE",
  "MANTENIMIENTO", "HOSTING", "SOFTWARE", "HARDWARE", "OTRO",
];

function formatDate(v: unknown) {
  if (!v) return "—";
  try { return new Date(String(v)).toLocaleDateString("es-ES", { day: "2-digit", month: "short", year: "numeric" }); }
  catch { return "—"; }
}

function formatCurrency(v: unknown) {
  if (v == null) return "€0,00";
  return new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" }).format(Number(v));
}

const columns: Column[] = [
  { key: "nombre", label: "Nombre", render: (v) => <span className="font-medium">{String(v ?? "—")}</span> },
  { key: "cif", label: "CIF" },
  { key: "tipo", label: "Tipo", render: (v) => <StatusBadge value={v as string} /> },
  { key: "email", label: "Email", render: (v) => v ? <span className="text-sm">{String(v)}</span> : "—" },
  { key: "telefono", label: "Teléfono" },
  {
    key: "website", label: "Web", render: (v) => v
      ? <a href={String(v)} target="_blank" rel="noreferrer" className="text-primary underline text-sm inline-flex items-center gap-1">
          <Globe size={12} /> Visitar
        </a>
      : "—",
  },
  { key: "created_at", label: "Creado", render: formatDate },
];

// ─── Detail Modal ────────────────────────────────────────────
function ProveedorDetail({ proveedor, onClose, onEdit }: {
  proveedor: Record<string, unknown>;
  onClose: () => void;
  onEdit: () => void;
}) {
  const { data: gastosData } = useGastos({ proveedor_id: String(proveedor.id), limit: 100 });

  const totalGastado = gastosData?.items?.reduce((sum, g) => sum + Number(g.total ?? 0), 0) ?? 0;

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>{String(proveedor.nombre)}</span>
            <Button size="sm" variant="outline" className="gap-1" onClick={onEdit}>
              <Pencil size={14} /> Editar
            </Button>
          </DialogTitle>
          <DialogDescription>Detalles del proveedor</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Info General */}
          <div>
            <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">📋 Información General</h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div><span className="text-muted-foreground">Tipo:</span> <StatusBadge value={proveedor.tipo as string} /></div>
              <div><span className="text-muted-foreground">CIF:</span> {String(proveedor.cif ?? "—")}</div>
              <div><span className="text-muted-foreground">Creado:</span> {formatDate(proveedor.created_at)}</div>
              <div><span className="text-muted-foreground">Actualizado:</span> {formatDate(proveedor.updated_at)}</div>
            </div>
          </div>

          {/* Contacto */}
          <div>
            <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">📞 Contacto</h4>
            <div className="space-y-1 text-sm">
              {proveedor.email && (
                <div className="flex items-center gap-2">
                  <Mail size={14} className="text-muted-foreground" />
                  <a href={`mailto:${proveedor.email}`} className="text-primary underline">{String(proveedor.email)}</a>
                </div>
              )}
              {proveedor.telefono && (
                <div className="flex items-center gap-2">
                  <Phone size={14} className="text-muted-foreground" />
                  <span>{String(proveedor.telefono)}</span>
                </div>
              )}
              {proveedor.website && (
                <div className="flex items-center gap-2">
                  <Globe size={14} className="text-muted-foreground" />
                  <a href={String(proveedor.website)} target="_blank" rel="noreferrer" className="text-primary underline inline-flex items-center gap-1">
                    {String(proveedor.website)} <ExternalLink size={12} />
                  </a>
                </div>
              )}
              {!proveedor.email && !proveedor.telefono && !proveedor.website && (
                <p className="text-muted-foreground italic">Sin datos de contacto</p>
              )}
            </div>
          </div>

          {/* Notas */}
          {proveedor.notas && (
            <div>
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">📝 Notas</h4>
              <p className="text-sm whitespace-pre-wrap">{String(proveedor.notas)}</p>
            </div>
          )}

          {/* Gastos Relacionados */}
          <div>
            <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">💰 Gastos Relacionados</h4>
            <div className="grid grid-cols-2 gap-3">
              <Card>
                <CardHeader className="pb-1 pt-3 px-3">
                  <CardTitle className="text-xs text-muted-foreground">Total gastado</CardTitle>
                </CardHeader>
                <CardContent className="px-3 pb-3">
                  <span className="text-lg font-bold">{formatCurrency(totalGastado)}</span>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-1 pt-3 px-3">
                  <CardTitle className="text-xs text-muted-foreground">Facturas</CardTitle>
                </CardHeader>
                <CardContent className="px-3 pb-3">
                  <span className="text-lg font-bold">{gastosData?.total ?? 0}</span>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

// ─── Form Dialog ─────────────────────────────────────────────
function ProveedorFormDialog({ open, onOpenChange, editing }: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  editing?: Record<string, unknown> | null;
}) {
  const { toast } = useToast();
  const createMutation = useCreateProveedor();
  const patchMutation = usePatchProveedor();
  const isEditing = !!editing;

  const [form, setForm] = useState<Record<string, string>>({});

  useEffect(() => {
    if (open) {
      if (editing) {
        const f: Record<string, string> = {};
        for (const [k, v] of Object.entries(editing)) {
          if (v != null) f[k] = String(v);
        }
        setForm(f);
      } else {
        setForm({ tipo: "OTRO" });
      }
    }
  }, [open, editing]);

  const setField = (key: string, value: string) => setForm((f) => ({ ...f, [key]: value }));

  const handleSubmit = async () => {
    if (!form.nombre?.trim()) {
      toast({ title: "Error", description: "El nombre es requerido", variant: "destructive" });
      return;
    }
    const { id, created_at, updated_at, ...payload } = form;
    try {
      if (isEditing) {
        await patchMutation.mutateAsync({ id: String(editing!.id), data: payload });
        toast({ title: "Actualizado", description: "Proveedor actualizado" });
      } else {
        await createMutation.mutateAsync(payload);
        toast({ title: "Creado", description: "Proveedor creado correctamente" });
      }
      onOpenChange(false);
    } catch (e: unknown) {
      toast({ title: "Error", description: String(e), variant: "destructive" });
    }
  };

  const isPending = createMutation.isPending || patchMutation.isPending;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>{isEditing ? "Editar proveedor" : "Nuevo proveedor"}</DialogTitle>
          <DialogDescription>{isEditing ? "Modifica los datos del proveedor" : "Registra un nuevo proveedor"}</DialogDescription>
        </DialogHeader>
        <div className="space-y-3">
          {/* Info básica */}
          <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Información Básica</h4>
          <div className="space-y-1">
            <Label>Nombre *</Label>
            <Input placeholder="Ej: Amazon Web Services" value={form.nombre ?? ""} onChange={(e) => setField("nombre", e.target.value)} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>CIF/NIF</Label>
              <Input placeholder="B12345678" value={form.cif ?? ""} onChange={(e) => setField("cif", e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label>Tipo</Label>
              <Select value={form.tipo ?? "OTRO"} onValueChange={(v) => setField("tipo", v)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {TIPOS.map((t) => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Contacto */}
          <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Datos de Contacto</h4>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Email</Label>
              <Input type="email" placeholder="contacto@proveedor.com" value={form.email ?? ""} onChange={(e) => setField("email", e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label>Teléfono</Label>
              <Input placeholder="+34 900 123 456" value={form.telefono ?? ""} onChange={(e) => setField("telefono", e.target.value)} />
            </div>
          </div>
          <div className="space-y-1">
            <Label>Website</Label>
            <Input placeholder="https://www.proveedor.com" value={form.website ?? ""} onChange={(e) => setField("website", e.target.value)} />
          </div>

          {/* Notas */}
          <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Notas</h4>
          <div className="space-y-1">
            <Label>Notas adicionales</Label>
            <Textarea rows={3} placeholder="Información adicional sobre el proveedor" value={form.notas ?? ""} onChange={(e) => setField("notas", e.target.value)} />
          </div>

          <Button onClick={handleSubmit} disabled={isPending} className="w-full">
            {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : isEditing ? "Guardar cambios" : "Crear proveedor"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

// ─── Main Page ───────────────────────────────────────────────
export default function ProveedoresPage() {
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const [tipo, setTipo] = useState("");
  const [showFilter, setShowFilter] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Record<string, unknown> | null>(null);
  const [viewing, setViewing] = useState<Record<string, unknown> | null>(null);

  const { data, isLoading } = useProveedores({
    q: search || undefined,
    offset,
    limit: 50,
    tipo: tipo || undefined,
  });

  return (
    <>
      <PageHeader
        title="Proveedores"
        subtitle={data ? `${data.total} proveedores` : undefined}
        searchValue={search}
        onSearch={(q) => { setSearch(q); setOffset(0); }}
        searchPlaceholder="Buscar por nombre o CIF..."
        actions={
          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={() => setShowFilter(!showFilter)} className={cn("gap-1", tipo && "border-primary text-primary")}>
              <Filter size={14} /> Tipo {tipo && "•"}
            </Button>
            <Button size="sm" onClick={() => { setEditing(null); setShowForm(true); }} className="gap-1">
              <Plus size={16} /> Añadir proveedor
            </Button>
          </div>
        }
      />

      {/* Filter bar */}
      {showFilter && (
        <div className="flex items-end gap-3 mb-4 p-3 rounded-lg border bg-card">
          <div className="space-y-1">
            <label className="text-xs text-muted-foreground">Tipo de proveedor</label>
            <Select value={tipo || "__all__"} onValueChange={(v) => { setTipo(v === "__all__" ? "" : v); setOffset(0); }}>
              <SelectTrigger className="w-[180px] h-8 text-xs"><SelectValue placeholder="Todos" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="__all__">Todos</SelectItem>
                {TIPOS.map((t) => <SelectItem key={t} value={t}>{t}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          {tipo && (
            <Button size="sm" variant="ghost" className="h-8 text-xs" onClick={() => { setTipo(""); setOffset(0); }}>Limpiar</Button>
          )}
        </div>
      )}

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        total={data?.total}
        limit={data?.limit ?? 50}
        offset={offset}
        onPageChange={setOffset}
        onRowClick={(row) => setViewing(row)}
        loading={isLoading}
      />

      {/* Detail modal */}
      {viewing && (
        <ProveedorDetail
          proveedor={viewing}
          onClose={() => setViewing(null)}
          onEdit={() => { setEditing(viewing); setViewing(null); setShowForm(true); }}
        />
      )}

      {/* Form dialog */}
      <ProveedorFormDialog
        open={showForm}
        onOpenChange={setShowForm}
        editing={editing}
      />
    </>
  );
}

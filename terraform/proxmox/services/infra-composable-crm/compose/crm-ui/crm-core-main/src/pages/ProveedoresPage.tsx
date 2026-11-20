import { useState } from "react";
import { useProveedores } from "@/hooks/use-api";
import { useQuery } from "@tanstack/react-query";
import { proveedores } from "@/lib/api";
import { DataTable, Column } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Filter, ExternalLink, Mail, Phone, Globe } from "lucide-react";
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

function formatCurrency(v: unknown, currency: "EUR" | "USD") {
  return new Intl.NumberFormat("es-ES", { style: "currency", currency }).format(Number(v));
}

function safeWebsite(value: unknown) {
  const url = String(value ?? "");
  return /^https?:\/\//i.test(url) ? url : null;
}

const columns: Column[] = [
  { key: "nombre", label: "Nombre", render: (v) => <span className="font-medium">{String(v ?? "—")}</span> },
  { key: "cif", label: "CIF" },
  { key: "tipo", label: "Tipo", render: (v) => <StatusBadge value={v as string} /> },
  { key: "email", label: "Email", render: (v) => v ? <span className="text-sm">{String(v)}</span> : "—" },
  { key: "telefono", label: "Teléfono" },
  {
    key: "website", label: "Web", render: (v) => safeWebsite(v)
      ? <a href={safeWebsite(v) ?? undefined} target="_blank" rel="noreferrer" className="text-primary underline text-sm inline-flex items-center gap-1">
          <Globe size={12} /> Visitar
        </a>
      : "—",
  },
  { key: "created_at", label: "Creado", render: formatDate },
];

// ─── Detail Modal ────────────────────────────────────────────
function ProveedorDetail({ proveedor, onClose }: {
  proveedor: Record<string, unknown>;
  onClose: () => void;
}) {
  const expenses = useQuery({
    queryKey: ["supplier-expenses", proveedor.id],
    queryFn: () => proveedores.expenseSummary(String(proveedor.id)),
  });

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>{String(proveedor.nombre)}</span>
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
                  <span>{String(proveedor.email)}</span>
                </div>
              )}
              {proveedor.telefono && (
                <div className="flex items-center gap-2">
                  <Phone size={14} className="text-muted-foreground" />
                  <span>{String(proveedor.telefono)}</span>
                </div>
              )}
              {safeWebsite(proveedor.website) && (
                <div className="flex items-center gap-2">
                  <Globe size={14} className="text-muted-foreground" />
                  <a href={safeWebsite(proveedor.website) ?? undefined} target="_blank" rel="noreferrer" className="text-primary underline inline-flex items-center gap-1">
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
                  {expenses.isPending ? "Cargando…" : expenses.isError ? "Resumen no disponible" :
                    expenses.data.items.length ? expenses.data.items.map(item => (
                      <div key={item.currency} className="text-lg font-bold">{formatCurrency(item.total, item.currency)}</div>
                    )) : "Sin gastos"}
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-1 pt-3 px-3">
                  <CardTitle className="text-xs text-muted-foreground">Gastos</CardTitle>
                </CardHeader>
                <CardContent className="px-3 pb-3">
                  <span className="text-lg font-bold">{expenses.data?.items.reduce((total, item) => total + item.count, 0) ?? "—"}</span>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

export default function ProveedoresPage() {
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const [tipo, setTipo] = useState("");
  const [showFilter, setShowFilter] = useState(false);
  const [viewing, setViewing] = useState<Record<string, unknown> | null>(null);

  const { data, isLoading, isError } = useProveedores({
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

      {isError ? <p role="alert" className="text-destructive">No se pudieron cargar los proveedores.</p> : <DataTable
        columns={columns}
        data={data?.items ?? []}
        total={data?.total}
        limit={data?.limit ?? 50}
        offset={offset}
        onPageChange={setOffset}
        onRowClick={(row) => setViewing(row)}
        loading={isLoading}
      />}

      {/* Detail modal */}
      {viewing && (
        <ProveedorDetail
          proveedor={viewing}
          onClose={() => setViewing(null)}
        />
      )}

    </>
  );
}

import { useState } from "react";
import { useGastos } from "@/hooks/use-api";
import { DataTable, Column } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Download, Filter } from "lucide-react";
import { cn } from "@/lib/utils";
import * as api from "@/lib/api";

function formatDate(v: unknown) {
  if (!v) return "—";
  try { return new Date(String(v)).toLocaleDateString("es-ES", { day: "2-digit", month: "short", year: "numeric" }); }
  catch { return "—"; }
}

function formatCurrency(v: unknown) {
  if (v == null) return "—";
  return new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" }).format(Number(v));
}

function getEstadoBadge(row: Record<string, unknown>) {
  const estado = String(row.estado ?? "");
  const fechaVenc = row.fecha_vencimiento ? new Date(String(row.fecha_vencimiento)) : null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  if (estado === "PENDIENTE" && fechaVenc && fechaVenc < today) {
    return { text: "VENCIDO", cls: "bg-destructive/15 text-destructive", urgent: true };
  }
  const map: Record<string, { text: string; cls: string }> = {
    PENDIENTE: { text: "Pendiente", cls: "bg-warning/15 text-warning" },
    PAGADO: { text: "Pagado", cls: "bg-success/15 text-success" },
    ANULADO: { text: "Anulado", cls: "bg-muted text-muted-foreground line-through" },
    VENCIDO: { text: "Vencido", cls: "bg-destructive/15 text-destructive" },
  };
  return map[estado] ?? { text: estado, cls: "bg-muted text-muted-foreground" };
}

const CATEGORIAS = ["", "TECNOLOGIA", "MARKETING", "PERSONAL", "OFICINA", "SERVICIOS", "FORMACION", "LEGAL", "OTRO"];
const ESTADOS = ["", "PENDIENTE", "PAGADO", "ANULADO", "VENCIDO"];
const PROYECTOS = ["", "Nucleo_tecnologico", "Mailerblend", "SHARED"];

export default function GastosLista() {
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const [categoria, setCategoria] = useState("");
  const [estado, setEstado] = useState("");
  const [projectKey, setProjectKey] = useState("");
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [showFilters, setShowFilters] = useState(false);

  const { data, isLoading, isError } = useGastos({
    q: search || undefined,
    offset,
    limit: 50,
    categoria: categoria || undefined,
    estado: estado || undefined,
    project_key: projectKey || undefined,
    from: from || undefined,
    to: to || undefined,
  });

  const columns: Column[] = [
    { key: "fecha_gasto", label: "Fecha", render: formatDate },
    { key: "concepto", label: "Concepto", render: (v) => <span className="font-medium max-w-[200px] truncate block">{String(v ?? "—")}</span> },
    { key: "proveedor_nombre", label: "Proveedor" },
    { key: "categoria", label: "Categoría" },
    { key: "project_key", label: "Proyecto" },
    {
      key: "estado",
      label: "Estado",
      render: (_v, row) => {
        const badge = getEstadoBadge(row);
        return (
          <span className={cn("inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium whitespace-nowrap", badge.cls)}>
            {badge.text}
          </span>
        );
      },
    },
    { key: "base_imponible", label: "Base", render: formatCurrency, className: "text-right" },
    { key: "iva_porcentaje", label: "IVA %", render: (v) => v != null ? `${v}%` : "—", className: "text-right" },
    { key: "total", label: "Total", render: formatCurrency, className: "text-right font-medium" },
    { key: "metodo_pago", label: "Pago" },
  ];

  const csvFilters = {
    categoria: categoria || undefined,
    estado: estado || undefined,
    project_key: projectKey || undefined,
    from: from || undefined,
    to: to || undefined,
  };

  const downloadCsv = async () => {
    try {
      const url = URL.createObjectURL(await api.gastos.exportCsv(csvFilters));
      const link = document.createElement("a");
      link.href = url;
      link.download = "gastos.csv";
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 30_000);
    } catch {
      window.alert("No se pudo exportar el CSV.");
    }
  };

  const resetFilters = () => {
    setCategoria("");
    setEstado("");
    setProjectKey("");
    setFrom("");
    setTo("");
    setOffset(0);
  };

  const hasFilters = !!(categoria || estado || projectKey || from || to);

  return (
    <>
      <PageHeader
        title="Gastos"
        subtitle={data ? `${data.total} gastos` : undefined}
        searchValue={search}
        onSearch={(q) => { setSearch(q); setOffset(0); }}
        searchPlaceholder="Buscar gastos..."
        actions={
          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={() => setShowFilters(!showFilters)} className={cn("gap-1", hasFilters && "border-primary text-primary")}>
              <Filter size={14} /> Filtros {hasFilters && "•"}
            </Button>
            <Button size="sm" variant="outline" className="gap-1" onClick={() => void downloadCsv()}>
              <Download size={14} /> CSV
            </Button>
          </div>
        }
      />

      {/* Filter bar */}
      {showFilters && (
        <div className="flex flex-wrap items-end gap-3 mb-4 p-3 rounded-lg border bg-card">
          <div className="space-y-1">
            <label className="text-xs text-muted-foreground">Categoría</label>
            <Select value={categoria || "__all__"} onValueChange={(v) => { setCategoria(v === "__all__" ? "" : v); setOffset(0); }}>
              <SelectTrigger className="w-[140px] h-8 text-xs"><SelectValue placeholder="Todas" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="__all__">Todas</SelectItem>
                {CATEGORIAS.filter(Boolean).map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1">
            <label className="text-xs text-muted-foreground">Estado</label>
            <Select value={estado || "__all__"} onValueChange={(v) => { setEstado(v === "__all__" ? "" : v); setOffset(0); }}>
              <SelectTrigger className="w-[130px] h-8 text-xs"><SelectValue placeholder="Todos" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="__all__">Todos</SelectItem>
                {ESTADOS.filter(Boolean).map((e) => <SelectItem key={e} value={e}>{e}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1">
            <label className="text-xs text-muted-foreground">Proyecto</label>
            <Select value={projectKey || "__all__"} onValueChange={(v) => { setProjectKey(v === "__all__" ? "" : v); setOffset(0); }}>
              <SelectTrigger className="w-[150px] h-8 text-xs"><SelectValue placeholder="Todos" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="__all__">Todos</SelectItem>
                {PROYECTOS.filter(Boolean).map((p) => <SelectItem key={p} value={p}>{p}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1">
            <label className="text-xs text-muted-foreground">Desde</label>
            <Input type="date" className="h-8 text-xs w-[140px]" value={from} onChange={(e) => { setFrom(e.target.value); setOffset(0); }} />
          </div>
          <div className="space-y-1">
            <label className="text-xs text-muted-foreground">Hasta</label>
            <Input type="date" className="h-8 text-xs w-[140px]" value={to} onChange={(e) => { setTo(e.target.value); setOffset(0); }} />
          </div>
          {hasFilters && (
            <Button size="sm" variant="ghost" className="h-8 text-xs" onClick={resetFilters}>Limpiar</Button>
          )}
        </div>
      )}

      {isError ? <p role="alert" className="text-destructive">No se pudieron cargar los gastos.</p> : <DataTable
        columns={columns}
        data={data?.items ?? []}
        total={data?.total}
        limit={data?.limit ?? 50}
        offset={offset}
        onPageChange={setOffset}
        loading={isLoading}
      />}

    </>
  );
}

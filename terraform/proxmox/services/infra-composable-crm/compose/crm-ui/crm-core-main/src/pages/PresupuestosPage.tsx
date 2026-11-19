import { useState } from "react";
import { usePresupuestos } from "@/hooks/use-api";
import { DataTable, Column } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { Button } from "@/components/ui/button";

function formatDate(v: unknown) {
  if (!v) return "—";
  try { return new Date(String(v)).toLocaleDateString("es-ES", { day: "2-digit", month: "short", year: "numeric" }); }
  catch { return "—"; }
}

function formatCurrency(v: unknown) {
  if (v == null) return "—";
  return new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" }).format(Number(v));
}

const statusOptions = ["", "Draft", "Sent", "Accepted", "Rejected", "Expired"];

const columns: Column[] = [
  { key: "quote_number", label: "Nº", render: (v) => <span className="font-mono text-sm">{String(v ?? "—")}</span> },
  { key: "title", label: "Título", render: (v) => <span className="font-medium">{String(v ?? "—")}</span> },
  { key: "contacto_nombre", label: "Contacto" },
  { key: "status", label: "Estado", render: (v) => <StatusBadge value={v as string} /> },
  { key: "version", label: "V.", render: (v) => v != null ? `v${v}` : "—" },
  { key: "quote_value", label: "Valor", render: formatCurrency, className: "text-right" },
  { key: "sent_at", label: "Enviado", render: formatDate },
  { key: "valid_until", label: "Válido hasta", render: formatDate },
  { key: "accepted_at", label: "Aceptado", render: formatDate },
  { key: "updated_at", label: "Actualizado", render: formatDate },
];

export default function PresupuestosPage() {
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const [status, setStatus] = useState("");

  const { data, isLoading } = usePresupuestos({
    q: search || undefined,
    status: status || undefined,
    offset,
    limit: 50,
  });

  return (
    <>
      <PageHeader
        title="Presupuestos"
        subtitle={data ? `${data.total} presupuestos` : undefined}
        searchValue={search}
        onSearch={(q) => { setSearch(q); setOffset(0); }}
        searchPlaceholder="Buscar presupuestos..."
        actions={
          <div className="flex gap-1 flex-wrap">
            {statusOptions.map((s) => (
              <Button key={s || "all"} variant={status === s ? "default" : "outline"} size="sm"
                onClick={() => { setStatus(s); setOffset(0); }}>{s || "Todos"}</Button>
            ))}
          </div>
        }
      />
      <DataTable
        columns={columns}
        data={data?.items ?? []}
        total={data?.total}
        limit={data?.limit ?? 50}
        offset={offset}
        onPageChange={setOffset}
        loading={isLoading}
      />
    </>
  );
}

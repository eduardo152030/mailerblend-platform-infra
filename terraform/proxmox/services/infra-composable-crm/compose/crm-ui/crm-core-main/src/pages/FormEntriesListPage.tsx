import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { DataTable, type Column } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { formEntries } from "@/lib/api";

const screens = {
  "formulario-web": { title: "Formularios web", columns: [
    { key: "contacto_nombre", label: "Contacto" },
    { key: "servicio_relacionado", label: "Servicio" },
    { key: "mensaje", label: "Mensaje", className: "whitespace-pre-wrap min-w-48" },
    { key: "submitted_at", label: "Recibido" },
  ]},
  facturas: { title: "Facturas", columns: [
    { key: "invoice_number", label: "Número" },
    { key: "invoice_value", label: "Importe", render: (value, row) => value == null ? "—" : `${value} ${row.currency ?? ""}` },
    { key: "status", label: "Estado" },
    { key: "issue_date", label: "Fecha de emisión" },
    { key: "due_date", label: "Vencimiento" },
  ]},
  historial: { title: "Historial", columns: [
    { key: "type", label: "Tipo" },
    { key: "subject", label: "Actividad" },
    { key: "occurred_at", label: "Fecha" },
  ]},
} satisfies Record<string, { title: string; columns: Column[] }>;

export default function FormEntriesListPage({ screen }: { screen: keyof typeof screens }) {
  const [offset, setOffset] = useState(0);
  const limit = 50;
  const config = screens[screen];
  const query = useQuery({
    queryKey: ["form-entries-list", screen, offset],
    queryFn: () => formEntries.list(screen, { limit, offset }),
  });

  return (
    <>
      <PageHeader title={config.title} />
      {query.isError ? (
        <p role="alert" className="text-destructive">No se pudo cargar el listado.</p>
      ) : (
        <DataTable columns={config.columns} data={query.data?.items ?? []}
          total={query.data?.total} limit={limit} offset={offset}
          onPageChange={setOffset} loading={query.isPending} />
      )}
    </>
  );
}

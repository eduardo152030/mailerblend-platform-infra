import { useState } from "react";
import { useConversionesOffline } from "@/hooks/use-api";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2, Eye, AlertTriangle } from "lucide-react";
import { StatusBadge } from "@/components/StatusBadge";
import ConversionDetailModal from "./ConversionDetailModal";

export default function ConversionesCola() {
  const [statusFilter, setStatusFilter] = useState("PENDING");
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const { data, isLoading } = useConversionesOffline({
    sync_status: statusFilter === "__all__" ? undefined : statusFilter,
    limit: 50,
  });

  const items = data?.items ?? [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[160px] h-8 text-xs"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="__all__">Todos</SelectItem>
              <SelectItem value="PENDING">Pendientes</SelectItem>
              <SelectItem value="FAILED">Fallidas</SelectItem>
              <SelectItem value="SENT">Enviadas</SelectItem>
            </SelectContent>
          </Select>
          <span className="text-sm text-muted-foreground">{data?.total ?? 0} registros</span>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
      ) : items.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-sm text-muted-foreground">
            No hay conversiones con el filtro seleccionado
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {items.map((item) => {
            const status = String(item.sync_status ?? "PENDING");
            const isFailed = status === "FAILED";
            return (
              <Card key={String(item.id)} className={isFailed ? "border-destructive/30" : ""}>
                <CardContent className="py-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1.5 flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <StatusBadge value={String(item.event_name ?? "")} />
                        <span className="text-xs text-muted-foreground">→</span>
                        <StatusBadge value={String(item.platform ?? "")} />
                        <StatusBadge value={status} />
                      </div>
                      <p className="text-xs text-muted-foreground">
                        Click ID: <span className="font-mono">{String(item.click_id ?? "—").substring(0, 30)}...</span>
                      </p>
                      <div className="flex items-center gap-3 text-xs text-muted-foreground">
                        {item.conversion_value && <span>Valor: €{Number(item.conversion_value).toLocaleString("es-ES")}</span>}
                        <span>Creada: {item.created_at ? new Date(String(item.created_at)).toLocaleString("es-ES") : "—"}</span>
                        <span>Reintentos: {String(item.retry_count ?? 0)}</span>
                      </div>
                      {isFailed && item.error_message && (
                        <div className="flex items-start gap-1.5 mt-1">
                          <AlertTriangle className="h-3.5 w-3.5 text-destructive mt-0.5 shrink-0" />
                          <p className="text-xs text-destructive">{String(item.error_message)}</p>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <Button variant="ghost" size="sm" aria-label="Ver detalle de conversión" onClick={() => setSelectedId(String(item.id))}>
                        <Eye className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      <ConversionDetailModal
        id={selectedId}
        open={!!selectedId}
        onClose={() => setSelectedId(null)}
      />
    </div>
  );
}

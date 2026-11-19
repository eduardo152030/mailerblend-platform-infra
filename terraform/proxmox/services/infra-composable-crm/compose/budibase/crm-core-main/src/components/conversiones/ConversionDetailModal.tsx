import { useConversionOfflineDetail } from "@/hooks/use-api";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Loader2, RefreshCw } from "lucide-react";
import { StatusBadge } from "@/components/StatusBadge";
import { Separator } from "@/components/ui/separator";

interface Props {
  id: string | null;
  open: boolean;
  onClose: () => void;
  onRetry?: (id: string) => void;
}

export default function ConversionDetailModal({ id, open, onClose, onRetry }: Props) {
  const { data, isLoading } = useConversionOfflineDetail(id);

  if (!open) return null;

  const fmt = (v: unknown) => (v ? String(v) : "—");
  const fmtDate = (v: unknown) => v ? new Date(String(v)).toLocaleString("es-ES") : "—";

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="text-base">Detalles de Conversión Offline</DialogTitle>
        </DialogHeader>

        {isLoading ? (
          <div className="flex justify-center py-8"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
        ) : !data ? (
          <p className="text-sm text-muted-foreground text-center py-8">No se encontró la conversión</p>
        ) : (
          <div className="space-y-4 text-sm">
            {/* General info */}
            <div>
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">📋 Información General</h4>
              <div className="grid grid-cols-2 gap-y-1.5 gap-x-4">
                <span className="text-muted-foreground">ID</span>
                <span className="font-mono text-xs truncate">{fmt(data.id)}</span>
                <span className="text-muted-foreground">Estado</span>
                <span><StatusBadge value={fmt(data.sync_status)} /></span>
                <span className="text-muted-foreground">Creada</span>
                <span>{fmtDate(data.created_at)}</span>
                <span className="text-muted-foreground">Enviada</span>
                <span>{fmtDate(data.sent_at)}</span>
              </div>
            </div>

            <Separator />

            {/* Event */}
            <div>
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">🎯 Evento</h4>
              <div className="grid grid-cols-2 gap-y-1.5 gap-x-4">
                <span className="text-muted-foreground">Tipo</span>
                <span><StatusBadge value={fmt(data.event_name)} /></span>
                <span className="text-muted-foreground">Valor</span>
                <span className="font-medium">
                  {data.conversion_value ? `€${Number(data.conversion_value).toLocaleString("es-ES")} ${fmt(data.currency)}` : "—"}
                </span>
                <span className="text-muted-foreground">Fecha conversión</span>
                <span>{fmtDate(data.conversion_time)}</span>
              </div>
            </div>

            <Separator />

            {/* Platform */}
            <div>
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">📢 Plataforma</h4>
              <div className="grid grid-cols-2 gap-y-1.5 gap-x-4">
                <span className="text-muted-foreground">Plataforma</span>
                <span><StatusBadge value={fmt(data.platform)} /></span>
                <span className="text-muted-foreground">Click ID</span>
                <span className="font-mono text-xs break-all">{fmt(data.click_id)}</span>
              </div>
            </div>

            <Separator />

            {/* References */}
            <div>
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">🔗 Referencias</h4>
              <div className="grid grid-cols-2 gap-y-1.5 gap-x-4">
                <span className="text-muted-foreground">Oportunidad ID</span>
                <span className="font-mono text-xs truncate">{fmt(data.oportunidad_id)}</span>
                <span className="text-muted-foreground">UTM ID</span>
                <span className="font-mono text-xs truncate">{fmt(data.parametros_utm_id)}</span>
              </div>
            </div>

            <Separator />

            {/* Sync status */}
            <div>
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">📊 Estado de Sincronización</h4>
              <div className="grid grid-cols-2 gap-y-1.5 gap-x-4">
                <span className="text-muted-foreground">Estado</span>
                <span><StatusBadge value={fmt(data.sync_status)} /></span>
                <span className="text-muted-foreground">Reintentos</span>
                <span>{String(data.retry_count ?? 0)}</span>
                {data.error_message && (
                  <>
                    <span className="text-muted-foreground">Error</span>
                    <span className="text-destructive text-xs">{fmt(data.error_message)}</span>
                  </>
                )}
              </div>
            </div>

            {/* Actions */}
            {String(data.sync_status) !== "SYNCED" && onRetry && (
              <div className="flex gap-2 pt-2">
                <Button variant="outline" size="sm" onClick={() => onRetry(String(data.id))}>
                  <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
                  Reintentar envío
                </Button>
              </div>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

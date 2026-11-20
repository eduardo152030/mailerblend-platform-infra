import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useLSSCooldownStatus, useLSSCooldowns } from "@/hooks/use-api";
import { AlertTriangle, CheckCircle, Pause } from "lucide-react";

export default function CooldownsSection() {
  const { data: statusData, isLoading: loadingStatus , isError } = useLSSCooldownStatus();
  const { data: historyData, isLoading: loadingHistory } = useLSSCooldowns({ limit: 10 });


  const status = statusData as any;
  const history = (historyData as any)?.items ?? [];

  if (isError) return <p role="alert" className="text-destructive">No se pudo cargar esta configuración.</p>;

  return (
    <div className="space-y-6">
      {/* Status */}
      <div>
        <h3 className="text-sm font-medium mb-3">🔴 Estado Actual</h3>
        {loadingStatus ? <Skeleton className="h-20" /> : status?.cooldown_active ? (
          <Card className="border-destructive/50 bg-destructive/5">
            <CardContent className="pt-4 space-y-1">
              <div className="flex items-center gap-2 text-destructive font-medium text-sm">
                <Pause size={16} /> COOLDOWN ACTIVO
              </div>
              <p className="text-xs text-muted-foreground">Razón: {status.trigger_reason}</p>
              <p className="text-xs text-muted-foreground">
                Termina en: {Math.round(status.remaining_hours ?? 0)}h
                {status.cooldown_end && ` (${new Date(status.cooldown_end).toLocaleString("es-ES")})`}
              </p>
            </CardContent>
          </Card>
        ) : (
          <Card className="border-emerald-500/30 bg-emerald-50/50 dark:bg-emerald-950/20">
            <CardContent className="pt-4 flex items-center gap-2">
              <CheckCircle size={16} className="text-emerald-600" />
              <div>
                <p className="text-sm font-medium">Sin cooldown activo</p>
                <p className="text-xs text-muted-foreground">El sistema puede enviar invites y mensajes</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* History */}
      <div>
        <h3 className="text-sm font-medium mb-3">📜 Historial de Cooldowns</h3>
        {loadingHistory ? (
          <div className="space-y-3">{Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-16" />)}</div>
        ) : history.length === 0 ? (
          <p className="text-sm text-muted-foreground">Sin historial de cooldowns.</p>
        ) : (
          <div className="space-y-3">
            {history.map((cd: any) => {
              const isActive = cd.is_active && cd.cooldown_end && new Date(cd.cooldown_end) > new Date();
              const durationH = cd.cooldown_start && cd.cooldown_end
                ? Math.round((new Date(cd.cooldown_end).getTime() - new Date(cd.cooldown_start).getTime()) / 3600000)
                : null;
              return (
                <Card key={cd.id} className={isActive ? "border-destructive/30" : ""}>
                  <CardContent className="pt-3 pb-3 space-y-1">
                    <div className="flex items-center gap-2">
                      {isActive ? <AlertTriangle size={14} className="text-destructive" /> : <CheckCircle size={14} className="text-emerald-600" />}
                      <span className="text-sm font-medium">{cd.trigger_reason}</span>
                      <Badge variant={isActive ? "destructive" : "secondary"} className="text-[10px] ml-auto">
                        {isActive ? "Activo" : "Completado"}
                      </Badge>
                    </div>
                    <div className="text-xs text-muted-foreground space-y-0.5">
                      <p>Inicio: {cd.cooldown_start ? new Date(cd.cooldown_start).toLocaleString("es-ES") : "—"}</p>
                      <p>Fin: {cd.cooldown_end ? new Date(cd.cooldown_end).toLocaleString("es-ES") : "—"}{durationH ? ` (${durationH}h)` : ""}</p>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

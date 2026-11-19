import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { useLSSRateLimitStatus, useLSSRateLimits, useLSSPatchRateLimit } from "@/hooks/use-api";
import { toast } from "@/hooks/use-toast";
import { AlertTriangle, Check, Send, MessageSquare } from "lucide-react";

function StatusCard({ icon: Icon, title, sent, cap, remaining, canSend }: {
  icon: React.ElementType; title: string; sent: number; cap: number; remaining: number; canSend: boolean;
}) {
  const pct = cap > 0 ? (sent / cap) * 100 : 0;
  return (
    <Card>
      <CardContent className="pt-4 space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Icon size={16} className="text-muted-foreground" />
            <span className="text-sm font-medium">{title}</span>
          </div>
          <Badge variant={canSend ? "secondary" : "destructive"} className="text-[10px]">
            {canSend ? "✅ Disponible" : "❌ Límite"}
          </Badge>
        </div>
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>Enviadas: {sent}/{cap}</span>
          <span>Restantes: {remaining}</span>
        </div>
        <Progress value={pct} className="h-2" />
      </CardContent>
    </Card>
  );
}

function LimitConfigCard({ limit, onUpdate }: { limit: Record<string, any>; onUpdate: (v: number) => void }) {
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(String(limit.limit_value));

  const handleSave = () => {
    const n = parseInt(value);
    if (isNaN(n) || n < 1) return;
    onUpdate(n);
    setEditing(false);
  };

  return (
    <Card>
      <CardContent className="pt-4 space-y-2">
        <p className="text-sm font-medium">{limit.limit_type}</p>
        <p className="text-xs text-muted-foreground">{limit.description}</p>
        <div className="flex items-center gap-2">
          {editing ? (
            <>
              <Input type="number" value={value} onChange={(e) => setValue(e.target.value)} className="h-8 w-24 text-xs" min={1} max={200} />
              <Button size="sm" variant="default" className="h-8 text-xs" onClick={handleSave}><Check size={12} className="mr-1" /> Guardar</Button>
              <Button size="sm" variant="ghost" className="h-8 text-xs" onClick={() => setEditing(false)}>Cancelar</Button>
            </>
          ) : (
            <>
              <span className="text-sm font-bold">{limit.limit_value}</span>
              <Button size="sm" variant="outline" className="h-7 text-xs ml-auto" onClick={() => { setValue(String(limit.limit_value)); setEditing(true); }}>Editar</Button>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default function RateLimitsSection() {
  const { data: statusData, isLoading: loadingStatus } = useLSSRateLimitStatus();
  const { data: limitsData, isLoading: loadingLimits } = useLSSRateLimits();
  const patchLimit = useLSSPatchRateLimit();

  const status = statusData as any;
  const limits = (limitsData as any)?.items ?? [];

  const handleUpdate = (limitType: string, newValue: number) => {
    patchLimit.mutate({ limitType, data: { limit_value: newValue } }, {
      onSuccess: () => toast({ title: "Límite actualizado", description: `${limitType} → ${newValue}` }),
      onError: () => toast({ title: "Error", description: "No se pudo actualizar", variant: "destructive" }),
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-sm font-medium mb-3">📊 Estado Actual (Hoy)</h3>
        {loadingStatus ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3"><Skeleton className="h-24" /><Skeleton className="h-24" /></div>
        ) : status ? (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <StatusCard icon={Send} title="Invitaciones" sent={status.invites?.sent_today ?? 0} cap={status.invites?.cap ?? 0} remaining={status.invites?.remaining ?? 0} canSend={status.invites?.can_send ?? true} />
              <StatusCard icon={MessageSquare} title="Mensajes" sent={status.messages?.sent_today ?? 0} cap={status.messages?.cap ?? 0} remaining={status.messages?.remaining ?? 0} canSend={status.messages?.can_send ?? true} />
            </div>
            {status.cooldown_active && (
              <div className="mt-3 flex items-center gap-2 p-3 rounded-lg bg-destructive/10 text-destructive text-sm">
                <AlertTriangle size={16} /> COOLDOWN ACTIVO — No se pueden enviar invites/mensajes
              </div>
            )}
          </>
        ) : (
          <p className="text-sm text-muted-foreground">Sin datos de rate limits.</p>
        )}
      </div>

      <div>
        <h3 className="text-sm font-medium mb-3">⚙️ Límites Configurables</h3>
        {loadingLimits ? (
          <div className="space-y-3"><Skeleton className="h-20" /><Skeleton className="h-20" /></div>
        ) : limits.length === 0 ? (
          <p className="text-sm text-muted-foreground">No hay límites configurados.</p>
        ) : (
          <div className="space-y-3">
            {limits.map((limit: any) => (
              <LimitConfigCard key={limit.limit_type} limit={limit} onUpdate={(v) => handleUpdate(limit.limit_type, v)} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

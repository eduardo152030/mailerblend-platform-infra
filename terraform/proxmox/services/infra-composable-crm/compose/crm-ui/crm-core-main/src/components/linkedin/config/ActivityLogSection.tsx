import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useLSSActivityStatsToday, useLSSActivityStatsDaily, useLSSActivityLog } from "@/hooks/use-api";
import { Send, MessageSquare, Eye, Activity } from "lucide-react";

const TYPE_META: Record<string, { icon: React.ElementType; label: string; emoji: string }> = {
  INVITE: { icon: Send, label: "Invites", emoji: "📤" },
  MESSAGE: { icon: MessageSquare, label: "Mensajes", emoji: "💬" },
  PROFILE_VIEW: { icon: Eye, label: "Profile Views", emoji: "👁️" },
  SEARCH: { icon: Activity, label: "Búsquedas", emoji: "🔍" },
};

export default function ActivityLogSection() {
  const { data: todayData, isLoading: loadingToday } = useLSSActivityStatsToday();
  const { data: weeklyData, isLoading: loadingWeekly } = useLSSActivityStatsDaily({ days: 7 });
  const { data: recentData, isLoading: loadingRecent } = useLSSActivityLog({ hours: 24, limit: 20 });

  const today = todayData as any;
  const weekly = (weeklyData as any)?.stats ?? {};
  const recent = (recentData as any)?.items ?? [];

  return (
    <div className="space-y-6">
      {/* Stats de hoy */}
      <div>
        <h3 className="text-sm font-medium mb-3">📈 Estadísticas de Hoy</h3>
        {loadingToday ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">{Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-16" />)}</div>
        ) : today ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {Object.entries(TYPE_META).map(([key, meta]) => (
              <Card key={key}>
                <CardContent className="pt-3 pb-3 flex items-center gap-3">
                  <span className="text-lg">{meta.emoji}</span>
                  <div>
                    <p className="text-lg font-bold">{today.stats?.[key] ?? 0}</p>
                    <p className="text-[10px] text-muted-foreground">{meta.label}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">Sin datos de actividad.</p>
        )}
      </div>

      {/* Weekly */}
      <div>
        <h3 className="text-sm font-medium mb-3">📅 Últimos 7 días</h3>
        {loadingWeekly ? (
          <Skeleton className="h-32 w-full" />
        ) : Object.keys(weekly).length === 0 ? (
          <p className="text-sm text-muted-foreground">Sin datos semanales.</p>
        ) : (
          <Card>
            <CardContent className="pt-4 overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-muted-foreground">
                    <th className="text-left py-1 pr-3">Tipo</th>
                    {Object.keys(weekly).sort().map((date) => (
                      <th key={date} className="text-center py-1 px-2 whitespace-nowrap">
                        {new Date(date).toLocaleDateString("es-ES", { weekday: "short", day: "numeric" })}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {["INVITE", "MESSAGE", "PROFILE_VIEW"].map((type) => (
                    <tr key={type} className="border-t border-border/50">
                      <td className="py-1.5 pr-3 font-medium">{TYPE_META[type]?.emoji} {TYPE_META[type]?.label}</td>
                      {Object.keys(weekly).sort().map((date) => (
                        <td key={date} className="text-center py-1.5 px-2">{(weekly[date] as any)?.[type] ?? 0}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Recent activity */}
      <div>
        <h3 className="text-sm font-medium mb-3">📋 Actividad Reciente (últimas 24h)</h3>
        {loadingRecent ? (
          <div className="space-y-2">{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-8" />)}</div>
        ) : recent.length === 0 ? (
          <p className="text-sm text-muted-foreground">Sin actividad reciente.</p>
        ) : (
          <Card>
            <CardContent className="pt-4 space-y-1">
              {recent.map((act: any) => {
                const time = act.executed_at ? new Date(act.executed_at).toLocaleTimeString("es-ES", { hour: "2-digit", minute: "2-digit" }) : "";
                const meta = TYPE_META[act.activity_type] || { emoji: "📊", label: act.activity_type };
                const md = act.metadata || {};
                return (
                  <div key={act.id} className="flex items-center gap-2 text-xs py-1 border-b border-border/30 last:border-0">
                    <span className="text-muted-foreground w-12 shrink-0">[{time}]</span>
                    <span>{meta.emoji}</span>
                    <Badge variant="outline" className="text-[10px]">{act.activity_type}</Badge>
                    {md.lead_name && <span className="text-muted-foreground">→ {md.lead_name}</span>}
                    {md.segment && <span className="text-muted-foreground/60">({md.segment})</span>}
                  </div>
                );
              })}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

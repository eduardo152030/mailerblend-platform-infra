import { useState, useMemo } from "react";
import { useConversionesOffline, useConversionesOfflineStats } from "@/hooks/use-api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2, Activity, CheckCircle2, Clock, AlertTriangle } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, Legend } from "recharts";
import { StatusBadge } from "@/components/StatusBadge";

const now = new Date();
const defaultFrom = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-01`;
const defaultTo = now.toISOString().split("T")[0];

const PLATFORM_COLORS: Record<string, string> = {
  GOOGLE: "hsl(var(--info))",
  FACEBOOK: "hsl(var(--primary))",
  LINKEDIN: "hsl(var(--info))",
  BING: "hsl(var(--warning))",
};

const EVENT_COLORS: Record<string, string> = {
  Lead_Submitted: "hsl(var(--muted-foreground))",
  Lead_Qualified: "hsl(var(--info))",
  Lead_Won: "hsl(var(--success))",
  Purchase: "hsl(var(--primary))",
  Custom: "hsl(var(--warning))",
};

export default function ConversionesDashboard() {
  const [from, setFrom] = useState(defaultFrom);
  const [to, setTo] = useState(defaultTo);

  const { data: statsData, isLoading: loadingStats } = useConversionesOfflineStats({ from, to });
  const { data: recentData, isLoading: loadingRecent } = useConversionesOffline({ limit: 10 });

  const kpis = useMemo(() => {
    const items = statsData?.items ?? [];
    let total = 0, synced = 0, pending = 0, failed = 0, totalValue = 0;
    items.forEach((i) => {
      const count = Number(i.count ?? 0);
      total += count;
      totalValue += Number(i.total_value ?? 0);
      const status = String(i.sync_status ?? "");
      if (status === "SYNCED") synced += count;
      else if (status === "PENDING") pending += count;
      else if (status === "FAILED") failed += count;
    });
    const successRate = total > 0 ? ((synced / total) * 100).toFixed(1) : "0.0";
    return { total, synced, pending, failed, successRate, totalValue };
  }, [statsData]);

  // Aggregate by platform from stats
  const platformChart = useMemo(() => {
    const items = statsData?.items ?? [];
    const map: Record<string, { synced: number; pending: number; failed: number }> = {};
    items.forEach((i) => {
      const p = String(i.platform ?? "—");
      if (!map[p]) map[p] = { synced: 0, pending: 0, failed: 0 };
      const count = Number(i.count ?? 0);
      const status = String(i.sync_status ?? "");
      if (status === "SYNCED") map[p].synced += count;
      else if (status === "PENDING") map[p].pending += count;
      else if (status === "FAILED") map[p].failed += count;
    });
    return Object.entries(map).map(([name, v]) => ({ name, ...v, total: v.synced + v.pending + v.failed }))
      .sort((a, b) => b.total - a.total);
  }, [statsData]);

  // Aggregate by event_name
  const eventChart = useMemo(() => {
    const items = statsData?.items ?? [];
    const map: Record<string, number> = {};
    items.forEach((i) => {
      const e = String(i.event_name ?? "—");
      map[e] = (map[e] ?? 0) + Number(i.count ?? 0);
    });
    return Object.entries(map).map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count);
  }, [statsData]);

  return (
    <div className="space-y-6">
      {/* Date filters */}
      <div className="flex flex-wrap items-end gap-3 p-3 rounded-lg border bg-card">
        <div className="space-y-1">
          <Label className="text-xs">Desde</Label>
          <Input type="date" value={from} onChange={(e) => setFrom(e.target.value)} className="w-[160px] h-8 text-xs" />
        </div>
        <div className="space-y-1">
          <Label className="text-xs">Hasta</Label>
          <Input type="date" value={to} onChange={(e) => setTo(e.target.value)} className="w-[160px] h-8 text-xs" />
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Conversiones</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.total.toLocaleString("es-ES")}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Enviadas</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-success" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {kpis.synced.toLocaleString("es-ES")}
              <span className="text-sm font-normal text-muted-foreground ml-1">({kpis.successRate}%)</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Pendientes</CardTitle>
            <Clock className="h-4 w-4 text-warning" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.pending.toLocaleString("es-ES")}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Fallidas</CardTitle>
            <AlertTriangle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.failed.toLocaleString("es-ES")}</div>
          </CardContent>
        </Card>
      </div>

      {/* Chart: Platform stacked bar */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Conversiones por Plataforma</CardTitle>
        </CardHeader>
        <CardContent>
          {loadingStats ? (
            <div className="flex justify-center py-8"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
          ) : platformChart.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">Sin datos para el período</p>
          ) : (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={platformChart} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis type="number" tick={{ fontSize: 12 }} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 12 }} width={80} />
                <Tooltip />
                <Legend />
                <Bar dataKey="synced" name="Enviadas" stackId="a" fill="hsl(var(--success))" radius={[0, 0, 0, 0]} />
                <Bar dataKey="pending" name="Pendientes" stackId="a" fill="hsl(var(--warning))" />
                <Bar dataKey="failed" name="Fallidas" stackId="a" fill="hsl(var(--destructive))" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      {/* Chart: Events */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Conversiones por Evento</CardTitle>
        </CardHeader>
        <CardContent>
          {loadingStats ? (
            <div className="flex justify-center py-8"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
          ) : eventChart.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">Sin datos para el período</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={eventChart}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="count" name="Conversiones" radius={[4, 4, 0, 0]}>
                  {eventChart.map((entry, idx) => (
                    <Cell key={idx} fill={EVENT_COLORS[entry.name] ?? "hsl(var(--accent))"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      {/* Recent activity */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Actividad Reciente</CardTitle>
        </CardHeader>
        <CardContent>
          {loadingRecent ? (
            <div className="flex justify-center py-8"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
          ) : (recentData?.items ?? []).length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">Sin conversiones recientes</p>
          ) : (
            <div className="space-y-2">
              {(recentData?.items ?? []).map((item, idx) => {
                const status = String(item.sync_status ?? "PENDING");
                const icon = status === "SYNCED" ? "✓" : status === "FAILED" ? "✗" : "⏳";
                const time = item.created_at ? new Date(String(item.created_at)).toLocaleTimeString("es-ES", { hour: "2-digit", minute: "2-digit" }) : "";
                return (
                  <div key={idx} className="flex items-center gap-3 text-sm py-1.5 px-2 rounded hover:bg-muted/50">
                    <span className={`text-xs font-mono ${status === "SYNCED" ? "text-success" : status === "FAILED" ? "text-destructive" : "text-warning"}`}>
                      {icon}
                    </span>
                    <span className="text-xs text-muted-foreground w-12">{time}</span>
                    <StatusBadge value={String(item.event_name ?? "")} />
                    <span className="text-xs">→</span>
                    <StatusBadge value={String(item.platform ?? "")} />
                    {item.conversion_value && (
                      <span className="text-xs font-medium">€{Number(item.conversion_value).toLocaleString("es-ES")}</span>
                    )}
                    <StatusBadge value={status} />
                    {status === "FAILED" && item.error_message && (
                      <span className="text-xs text-destructive truncate max-w-[200px]">{String(item.error_message)}</span>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

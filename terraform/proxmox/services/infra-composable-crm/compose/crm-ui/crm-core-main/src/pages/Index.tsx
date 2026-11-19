import { useState, useMemo } from "react";
import { useContacts, useOportunidades, usePendientes, usePresupuestos, useGastos, useGastosTimeseries, useLSSDashboard } from "@/hooks/use-api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { Users, Target, CheckSquare, FileText, Receipt, Loader2, TrendingUp, TrendingDown, ArrowRight, Calendar, Linkedin, CalendarCheck, Zap, MessageSquare } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, LineChart, Line, PieChart, Pie, Cell } from "recharts";
import { format, subDays, subMonths, startOfDay, startOfWeek, startOfMonth, startOfYear, endOfDay } from "date-fns";
import { es } from "date-fns/locale";

type TimeRange = "today" | "week" | "month" | "year";

function getDateRange(range: TimeRange) {
  const now = new Date();
  const rangeMap: Record<TimeRange, { from: Date; to: Date; prevFrom: Date; prevTo: Date }> = {
    today: {
      from: startOfDay(now),
      to: endOfDay(now),
      prevFrom: startOfDay(subDays(now, 1)),
      prevTo: endOfDay(subDays(now, 1)),
    },
    week: {
      from: startOfWeek(now, { weekStartsOn: 1 }),
      to: now,
      prevFrom: subDays(startOfWeek(now, { weekStartsOn: 1 }), 7),
      prevTo: subDays(startOfWeek(now, { weekStartsOn: 1 }), 1),
    },
    month: {
      from: startOfMonth(now),
      to: now,
      prevFrom: startOfMonth(subMonths(now, 1)),
      prevTo: subDays(startOfMonth(now), 1),
    },
    year: {
      from: startOfYear(now),
      to: now,
      prevFrom: startOfYear(subMonths(now, 12)),
      prevTo: subDays(startOfYear(now), 1),
    },
  };
  return rangeMap[range];
}

function fmt(d: Date) {
  return format(d, "yyyy-MM-dd");
}

function TrendBadge({ current, previous }: { current: number; previous: number }) {
  if (previous === 0 && current === 0) return null;
  const pct = previous === 0 ? (current > 0 ? 100 : 0) : Math.round(((current - previous) / previous) * 100);
  const isUp = pct >= 0;
  return (
    <span className={`inline-flex items-center gap-0.5 text-xs font-medium ${isUp ? "text-success" : "text-destructive"}`}>
      {isUp ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
      {pct > 0 ? "+" : ""}{pct}%
    </span>
  );
}

function StatCard({ title, value, prevValue, icon: Icon, href, loading, accent }: {
  title: string; value: number; prevValue?: number; icon: any; href: string; loading?: boolean; accent?: string;
}) {
  return (
    <Link to={href}>
      <Card className="hover:shadow-md transition-shadow cursor-pointer group">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
          <div className={`p-1.5 rounded-md ${accent ?? "bg-muted"}`}>
            <Icon className="h-4 w-4 text-primary-foreground" />
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          ) : (
            <div className="flex items-end justify-between">
              <div className="text-2xl font-bold">{value}</div>
              {prevValue !== undefined && <TrendBadge current={value} previous={prevValue} />}
            </div>
          )}
          <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1 group-hover:text-foreground transition-colors">
            Ver detalle <ArrowRight size={10} />
          </p>
        </CardContent>
      </Card>
    </Link>
  );
}

const DONUT_COLORS = [
  "hsl(160, 84%, 39%)",  // primary/success
  "hsl(38, 92%, 50%)",   // warning
  "hsl(210, 90%, 55%)",  // info
  "hsl(0, 72%, 51%)",    // destructive
  "hsl(280, 60%, 50%)",  // purple
];

const ESTADO_LABELS: Record<string, string> = {
  Nuevo: "Nuevo",
  "En contacto": "En contacto",
  Negociación: "Negociación",
  Ganado: "Ganado",
  Perdido: "Perdido",
};

function LinkedInSourcingCard() {
  const { data, isLoading } = useLSSDashboard({ days: 30 });
  const d = (data ?? {}) as Record<string, any>;
  const byStatus = (d.by_status ?? {}) as Record<string, number>;
  const converted = byStatus["CONVERTED"] ?? 0;
  const booked = d.booked_calls ?? 0;
  const totalLeads = d.total_leads ?? 0;

  return (
    <Link to="/linkedin-sourcing">
      <Card className="hover:shadow-md transition-shadow cursor-pointer group h-full">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Linkedin size={16} className="text-blue-500" />
            LinkedIn Sourcing
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          ) : (
            <>
              <div className="flex items-center gap-4 mb-1">
                <div>
                  <div className="text-2xl font-bold">{totalLeads}</div>
                  <p className="text-[10px] text-muted-foreground">Leads</p>
                </div>
                <div>
                  <div className="text-2xl font-bold text-primary">{booked}</div>
                  <p className="text-[10px] text-muted-foreground">Booked</p>
                </div>
                <div>
                  <div className="text-2xl font-bold text-amber-500">{converted}</div>
                  <p className="text-[10px] text-muted-foreground">Convertidos</p>
                </div>
              </div>
              <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1 group-hover:text-foreground transition-colors">
                Ver dashboard <ArrowRight size={10} />
              </p>
            </>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}

export default function DashboardPage() {
  const [range, setRange] = useState<TimeRange>("month");
  const { from, to, prevFrom, prevTo } = useMemo(() => getDateRange(range), [range]);
  const fromStr = fmt(from);
  const toStr = fmt(to);
  const prevFromStr = fmt(prevFrom);
  const prevToStr = fmt(prevTo);

  // Current period queries
  const contacts = useContacts({ limit: 1 });
  const oportunidades = useOportunidades({ limit: 1 });
  const pendientes = usePendientes({ limit: 1 });
  const presupuestos = usePresupuestos({ limit: 1 });
  const gastos = useGastos({ limit: 1 });

  // Filtered counts for comparison (using created dates where possible)
  const pendientesActivas = usePendientes({ limit: 1, status: "TODO" });
  const opNuevas = useOportunidades({ limit: 1, estado: "Nuevo" });

  // Oportunidades by estado for donut chart
  const opAll = useOportunidades({ limit: 200 });

  // Gastos timeseries for line chart
  const gastosTs = useGastosTimeseries({ bucket: "month", from: fmt(startOfYear(new Date())), to: toStr });

  // Oportunidades distribution
  const estadoDist = useMemo(() => {
    if (!opAll.data?.items) return [];
    const counts: Record<string, number> = {};
    (opAll.data.items as any[]).forEach((op) => {
      const e = op.estado ?? "Otro";
      counts[e] = (counts[e] ?? 0) + 1;
    });
    return Object.entries(counts).map(([name, value]) => ({
      name: ESTADO_LABELS[name] ?? name,
      value,
    }));
  }, [opAll.data]);

  // Pendientes by status for bar chart
  const pendAll = usePendientes({ limit: 200 });
  const pendDist = useMemo(() => {
    if (!pendAll.data?.items) return [];
    const counts: Record<string, number> = {};
    (pendAll.data.items as any[]).forEach((p) => {
      const s = p.status ?? "Otro";
      counts[s] = (counts[s] ?? 0) + 1;
    });
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [pendAll.data]);

  // Gastos timeseries data
  const gastosChartData = useMemo(() => {
    if (!gastosTs.data?.items) return [];
    return (gastosTs.data.items as any[]).map((item) => ({
      month: item.bucket_start ? format(new Date(item.bucket_start as string), "MMM", { locale: es }) : "",
      total: Number(item.sum_total ?? 0),
      count: Number(item.count ?? 0),
    }));
  }, [gastosTs.data]);

  const timeRanges: { key: TimeRange; label: string }[] = [
    { key: "today", label: "Hoy" },
    { key: "week", label: "Semana" },
    { key: "month", label: "Mes" },
    { key: "year", label: "Año" },
  ];

  const chartConfig = {
    total: { label: "Total €", color: "hsl(160, 84%, 39%)" },
    count: { label: "Cantidad", color: "hsl(210, 90%, 55%)" },
    value: { label: "Cantidad", color: "hsl(160, 84%, 39%)" },
  };

  return (
    <div>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Resumen de tu CRM · {format(from, "d MMM", { locale: es })} – {format(to, "d MMM yyyy", { locale: es })}
          </p>
        </div>
        <div className="flex items-center gap-1 bg-muted p-1 rounded-lg">
          {timeRanges.map((t) => (
            <Button
              key={t.key}
              size="sm"
              variant={range === t.key ? "default" : "ghost"}
              className="h-7 text-xs px-3"
              onClick={() => setRange(t.key)}
            >
              {t.label}
            </Button>
          ))}
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 mb-6">
        <StatCard
          title="Contactos"
          value={contacts.data?.total ?? 0}
          icon={Users}
          href="/contactos"
          loading={contacts.isLoading}
          accent="bg-info"
        />
        <StatCard
          title="Oportunidades"
          value={oportunidades.data?.total ?? 0}
          icon={Target}
          href="/oportunidades"
          loading={oportunidades.isLoading}
          accent="bg-success"
        />
        <StatCard
          title="Pendientes"
          value={pendientes.data?.total ?? 0}
          icon={CheckSquare}
          href="/pendientes"
          loading={pendientes.isLoading}
          accent="bg-warning"
        />
        <StatCard
          title="Presupuestos"
          value={presupuestos.data?.total ?? 0}
          icon={FileText}
          href="/presupuestos"
          loading={presupuestos.isLoading}
          accent="bg-primary"
        />
        <StatCard
          title="Gastos"
          value={gastos.data?.total ?? 0}
          icon={Receipt}
          href="/gastos"
          loading={gastos.isLoading}
          accent="bg-destructive"
        />
      </div>

      {/* Highlight cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingUp size={16} className="text-success" />
              Oportunidades nuevas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-success">{opNuevas.data?.total ?? 0}</div>
            <p className="text-xs text-muted-foreground mt-1">Pendientes de contactar</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <CheckSquare size={16} className="text-warning" />
              Tareas TODO
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-warning">{pendientesActivas.data?.total ?? 0}</div>
            <p className="text-xs text-muted-foreground mt-1">Requieren acción</p>
          </CardContent>
        </Card>
        <LinkedInSourcingCard />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Gastos evolution - Line chart */}
        <Card className="lg:col-span-2">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Evolución de Gastos ({new Date().getFullYear()})</CardTitle>
          </CardHeader>
          <CardContent>
            {gastosChartData.length > 0 ? (
              <ChartContainer config={chartConfig} className="h-[250px] w-full">
                <LineChart data={gastosChartData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis dataKey="month" className="text-xs" />
                  <YAxis className="text-xs" />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Line
                    type="monotone"
                    dataKey="total"
                    stroke="hsl(160, 84%, 39%)"
                    strokeWidth={2}
                    dot={{ fill: "hsl(160, 84%, 39%)", r: 3 }}
                  />
                </LineChart>
              </ChartContainer>
            ) : (
              <div className="h-[250px] flex items-center justify-center text-muted-foreground text-sm">
                <Loader2 className="h-5 w-5 animate-spin mr-2" /> Cargando datos…
              </div>
            )}
          </CardContent>
        </Card>

        {/* Oportunidades donut */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Oportunidades por Estado</CardTitle>
          </CardHeader>
          <CardContent>
            {estadoDist.length > 0 ? (
              <div className="h-[250px] flex flex-col items-center justify-center">
                <ChartContainer config={chartConfig} className="h-[180px] w-full">
                  <PieChart>
                    <Pie
                      data={estadoDist}
                      cx="50%"
                      cy="50%"
                      innerRadius={45}
                      outerRadius={75}
                      dataKey="value"
                      paddingAngle={2}
                    >
                      {estadoDist.map((_, i) => (
                        <Cell key={i} fill={DONUT_COLORS[i % DONUT_COLORS.length]} />
                      ))}
                    </Pie>
                    <ChartTooltip content={<ChartTooltipContent />} />
                  </PieChart>
                </ChartContainer>
                <div className="flex flex-wrap gap-3 justify-center mt-2">
                  {estadoDist.map((e, i) => (
                    <div key={e.name} className="flex items-center gap-1.5 text-xs">
                      <span
                        className="w-2.5 h-2.5 rounded-full shrink-0"
                        style={{ background: DONUT_COLORS[i % DONUT_COLORS.length] }}
                      />
                      <span className="text-muted-foreground">{e.name}</span>
                      <span className="font-semibold">{e.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="h-[250px] flex items-center justify-center text-muted-foreground text-sm">
                <Loader2 className="h-5 w-5 animate-spin mr-2" /> Cargando…
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Bar chart - Pendientes by status */}
      <div className="grid grid-cols-1 mt-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Tareas por Estado</CardTitle>
          </CardHeader>
          <CardContent>
            {pendDist.length > 0 ? (
              <ChartContainer config={chartConfig} className="h-[200px] w-full">
                <BarChart data={pendDist} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis dataKey="name" className="text-xs" />
                  <YAxis className="text-xs" allowDecimals={false} />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                    {pendDist.map((_, i) => (
                      <Cell key={i} fill={DONUT_COLORS[i % DONUT_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ChartContainer>
            ) : (
              <div className="h-[200px] flex items-center justify-center text-muted-foreground text-sm">
                <Loader2 className="h-5 w-5 animate-spin mr-2" /> Cargando…
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

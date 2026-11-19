import { useState, useMemo } from "react";
import {
  useGastosStats, useGastosStats2, useGastosTimeseries,
  useGastosTaxSummary, useGastosPnlSummary,
} from "@/hooks/use-api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2, TrendingUp, Clock, Receipt, Percent, DollarSign, PieChart } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, Legend,
} from "recharts";

function formatCurrency(v: unknown) {
  if (v == null) return "€0,00";
  return new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" }).format(Number(v));
}

const now = new Date();
const defaultFrom = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-01`;
const defaultTo = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate()).padStart(2, "0")}`;

export default function GastosDashboard() {
  const [from, setFrom] = useState(defaultFrom);
  const [to, setTo] = useState(defaultTo);
  const [projectKey, setProjectKey] = useState("__all__");

  const projectFilter = projectKey === "__all__" ? undefined : projectKey;

  // Stats by category (for KPIs + bar chart)
  const { data: statsByCategoria, isLoading: catLoading } = useGastosStats({
    group_by: "categoria", from, to, project_key: projectFilter,
  });

  // Stats by estado
  const { data: statsByEstado } = useGastosStats({
    group_by: "estado", from, to, project_key: projectFilter,
  });

  // Stats2 by project_categoria (for "Por Proyecto" KPI)
  const { data: statsByProject } = useGastosStats2({
    group_by: "project_categoria", from, to,
  });

  // Stats2 by project_month (for project evolution)
  const { data: statsByProjectMonth } = useGastosStats2({
    group_by: "project_month", from, to,
  });

  // Timeseries
  const sixMonthsAgo = new Date(now);
  sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 5);
  const tsFrom = `${sixMonthsAgo.getFullYear()}-${String(sixMonthsAgo.getMonth() + 1).padStart(2, "0")}-01`;

  const { data: timeseries, isLoading: tsLoading } = useGastosTimeseries({
    bucket: "month", from: tsFrom, to, project_key: projectFilter,
  });

  // Tax summary
  const { data: taxData } = useGastosTaxSummary({ from, to });

  // PnL summary
  const { data: pnlData } = useGastosPnlSummary({ from, to });

  // === KPIs ===
  const kpis = useMemo(() => {
    const catItems = statsByCategoria?.items ?? [];
    const total = catItems.reduce((s, i) => s + Number(i.sum_total ?? 0), 0);
    const base = catItems.reduce((s, i) => s + Number(i.sum_base ?? 0), 0);
    const iva = catItems.reduce((s, i) => s + Number(i.sum_iva ?? 0), 0);
    const numGastos = catItems.reduce((s, i) => s + Number(i.count ?? 0), 0);

    const projItems = statsByProject?.items ?? [];
    const projectTotals: Record<string, number> = {};
    projItems.forEach((i) => {
      const proj = String(i.project_key ?? "").toLowerCase();
      projectTotals[proj] = (projectTotals[proj] ?? 0) + Number(i.sum_total ?? 0);
    });
    const findProject = (key: string) => {
      const entry = Object.entries(projectTotals).find(([k]) => k.includes(key.toLowerCase()));
      return entry ? entry[1] : 0;
    };

    return {
      total, base, iva, numGastos,
      nucleo: findProject("nucleo"),
      mailerblend: findProject("mailerblend"),
      shared: findProject("shared"),
    };
  }, [statsByCategoria, statsByProject]);

  // === Estado breakdown ===
  const estadoBreakdown = useMemo(() => {
    const items = statsByEstado?.items ?? [];
    return items.map((i) => ({
      name: String(i.key ?? "—"),
      total: Number(i.sum_total ?? 0),
      count: Number(i.count ?? 0),
    }));
  }, [statsByEstado]);

  // === Bar chart data ===
  const barData = useMemo(() => {
    if (!statsByCategoria?.items) return [];
    return statsByCategoria.items.map((item) => ({
      name: String(item.key ?? "—"),
      total: Number(item.sum_total ?? 0),
      count: Number(item.count ?? 0),
    })).sort((a, b) => b.total - a.total);
  }, [statsByCategoria]);

  // === Line chart data ===
  const lineData = useMemo(() => {
    if (!timeseries?.items) return [];
    return timeseries.items.map((item) => {
      const d = new Date(String(item.bucket));
      return {
        name: d.toLocaleDateString("es-ES", { month: "short", year: "2-digit" }),
        total: Number(item.sum_total ?? 0),
        base: Number(item.sum_base ?? 0),
        iva: Number(item.sum_iva ?? 0),
      };
    });
  }, [timeseries]);

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-3 rounded-lg border bg-card">
        <div className="space-y-1">
          <Label className="text-xs">Desde</Label>
          <Input type="date" value={from} onChange={(e) => setFrom(e.target.value)} className="h-8 text-xs" />
        </div>
        <div className="space-y-1">
          <Label className="text-xs">Hasta</Label>
          <Input type="date" value={to} onChange={(e) => setTo(e.target.value)} className="h-8 text-xs" />
        </div>
        <div className="space-y-1">
          <Label className="text-xs">Proyecto</Label>
          <Select value={projectKey} onValueChange={setProjectKey}>
            <SelectTrigger className="h-8 text-xs"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="__all__">Todos</SelectItem>
              <SelectItem value="Nucleo_tecnologico">Núcleo Tecnológico</SelectItem>
              <SelectItem value="Mailerblend">Mailerblend</SelectItem>
              <SelectItem value="SHARED">Shared</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs text-muted-foreground uppercase tracking-wide">Total</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(kpis.total)}</div>
            <p className="text-xs text-muted-foreground">{kpis.numGastos} gastos</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs text-muted-foreground uppercase tracking-wide">Base Imponible</CardTitle>
            <Receipt className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(kpis.base)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs text-muted-foreground uppercase tracking-wide">IVA Total</CardTitle>
            <Percent className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(kpis.iva)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs text-muted-foreground uppercase tracking-wide">Por Proyecto</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between"><span className="text-muted-foreground">Núcleo</span> <span className="font-medium">{formatCurrency(kpis.nucleo)}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Mailerblend</span> <span className="font-medium">{formatCurrency(kpis.mailerblend)}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Shared</span> <span className="font-medium">{formatCurrency(kpis.shared)}</span></div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs text-muted-foreground uppercase tracking-wide">Por Estado</CardTitle>
            <PieChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="space-y-1 text-sm">
              {estadoBreakdown.length === 0 ? (
                <span className="text-muted-foreground text-xs">Sin datos</span>
              ) : estadoBreakdown.map((e) => (
                <div key={e.name} className="flex justify-between">
                  <span className="text-muted-foreground">{e.name}</span>
                  <span className="font-medium">{formatCurrency(e.total)}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tax + PnL summary row */}
      {(taxData || pnlData) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {taxData && (
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm">Resumen Fiscal</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-y-2 text-sm">
                  <span className="text-muted-foreground">Base total</span>
                  <span className="font-medium text-right">{formatCurrency(taxData.sum_base)}</span>
                  <span className="text-muted-foreground">IVA soportado</span>
                  <span className="font-medium text-right">{formatCurrency(taxData.sum_iva)}</span>
                  <span className="text-muted-foreground">Total con IVA</span>
                  <span className="font-medium text-right">{formatCurrency(taxData.sum_total)}</span>
                  <span className="text-muted-foreground">Nº facturas</span>
                  <span className="font-medium text-right">{String(taxData.count ?? 0)}</span>
                </div>
              </CardContent>
            </Card>
          )}
          {pnlData && (
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm">P&L Resumen</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-y-2 text-sm">
                  {Object.entries(pnlData).map(([key, val]) => (
                    <div key={key} className="contents">
                      <span className="text-muted-foreground">{key.replace(/_/g, " ")}</span>
                      <span className="font-medium text-right">
                        {typeof val === "number" || (typeof val === "string" && !isNaN(Number(val)))
                          ? formatCurrency(val)
                          : String(val ?? "—")}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar chart by category */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Gastos por Categoría</CardTitle>
          </CardHeader>
          <CardContent>
            {catLoading ? (
              <div className="flex justify-center py-12"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
            ) : barData.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-12">Sin datos</p>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={barData} layout="vertical" margin={{ left: 20, right: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis type="number" tickFormatter={(v) => `€${v.toLocaleString("es-ES")}`} stroke="hsl(var(--muted-foreground))" fontSize={11} />
                  <YAxis type="category" dataKey="name" width={100} stroke="hsl(var(--muted-foreground))" fontSize={11} />
                  <Tooltip formatter={(v: number) => formatCurrency(v)} contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }} />
                  <Bar dataKey="total" fill="hsl(var(--primary))" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Line chart timeseries */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Evolución de Gastos (Últimos 6 meses)</CardTitle>
          </CardHeader>
          <CardContent>
            {tsLoading ? (
              <div className="flex justify-center py-12"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
            ) : lineData.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-12">Sin datos</p>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={lineData} margin={{ left: 10, right: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={11} />
                  <YAxis tickFormatter={(v) => `€${v.toLocaleString("es-ES")}`} stroke="hsl(var(--muted-foreground))" fontSize={11} />
                  <Tooltip formatter={(v: number) => formatCurrency(v)} contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }} />
                  <Legend />
                  <Line type="monotone" dataKey="total" name="Total" stroke="hsl(var(--primary))" strokeWidth={2} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="base" name="Base" stroke="hsl(var(--info))" strokeWidth={1.5} strokeDasharray="4 4" dot={false} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

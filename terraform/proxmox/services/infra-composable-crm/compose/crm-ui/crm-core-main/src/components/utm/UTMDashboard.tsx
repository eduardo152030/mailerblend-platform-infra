import { useState, useMemo } from "react";
import { useUtmStats, useUtmStats2, useUtmStatsConversions } from "@/hooks/use-api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2, Users, MousePointerClick, TrendingUp, Megaphone } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

const now = new Date();
const defaultFrom = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-01`;
const defaultTo = now.toISOString().split("T")[0];

const GROUP_BY_OPTIONS = [
  { value: "source", label: "Fuente" },
  { value: "campaign", label: "Campaña" },
  { value: "medium", label: "Medio" },
  { value: "device", label: "Dispositivo" },
  { value: "platform", label: "Plataforma" },
];

const GROUP_BY_2D_OPTIONS = [
  { value: "campaign_device", label: "Campaña × Dispositivo" },
  { value: "campaign_platform", label: "Campaña × Plataforma" },
  { value: "source_medium", label: "Fuente × Medio" },
  { value: "campaign_source", label: "Campaña × Fuente" },
];

const CONV_GROUP_BY_OPTIONS = [
  { value: "campaign", label: "Campaña" },
  { value: "source", label: "Fuente" },
  { value: "medium", label: "Medio" },
  { value: "platform", label: "Plataforma" },
];

const BAR_COLORS = [
  "hsl(var(--primary))",
  "hsl(var(--info))",
  "hsl(var(--warning))",
  "hsl(var(--success))",
  "hsl(var(--destructive))",
  "hsl(var(--accent))",
];

export default function UTMDashboard() {
  const [from, setFrom] = useState(defaultFrom);
  const [to, setTo] = useState(defaultTo);
  const [groupBy, setGroupBy] = useState("source");
  const [groupBy2d, setGroupBy2d] = useState("campaign_device");
  const [convGroupBy, setConvGroupBy] = useState("campaign");

  const { data: statsData, isLoading: loadingStats } = useUtmStats({
    group_by: groupBy,
    created_from: from,
    created_to: to,
  });

  const { data: stats2Data, isLoading: loading2d } = useUtmStats2({
    group_by: groupBy2d,
    created_from: from,
    created_to: to,
  });

  const { data: convData, isLoading: loadingConv } = useUtmStatsConversions({
    group_by: convGroupBy,
    created_from: from,
    created_to: to,
  });

  // KPIs from stats by source
  const { data: kpiData } = useUtmStats({ group_by: "source", created_from: from, created_to: to });

  const kpis = useMemo(() => {
    const items = kpiData?.items ?? [];
    const totalLeads = items.reduce((s, i) => s + Number(i.leads ?? 0), 0);
    const withClickId = items.reduce(
      (s, i) => s + Number(i.with_gclid ?? 0) + Number(i.with_fbclid ?? 0) + Number(i.with_li_fat_id ?? 0) + Number(i.with_msclkid ?? 0),
      0
    );
    const topSource = items.length > 0
      ? items.reduce((a, b) => (Number(a.leads ?? 0) >= Number(b.leads ?? 0) ? a : b))
      : null;
    return { totalLeads, withClickId, topSource };
  }, [kpiData]);

  // Pivot data for stats2
  const pivotData = useMemo(() => {
    const items = stats2Data?.items ?? [];
    if (items.length === 0) return { rows: [] as string[], cols: [] as string[], matrix: {} as Record<string, Record<string, number>> };
    const rowSet = new Set<string>();
    const colSet = new Set<string>();
    const matrix: Record<string, Record<string, number>> = {};
    items.forEach((item) => {
      const r = String(item.key1 ?? "—");
      const c = String(item.key2 ?? "—");
      rowSet.add(r);
      colSet.add(c);
      if (!matrix[r]) matrix[r] = {};
      matrix[r][c] = Number(item.leads ?? 0);
    });
    return { rows: Array.from(rowSet), cols: Array.from(colSet), matrix };
  }, [stats2Data]);

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
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Leads</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.totalLeads.toLocaleString("es-ES")}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Con Click ID</CardTitle>
            <MousePointerClick className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {kpis.withClickId.toLocaleString("es-ES")}
              {kpis.totalLeads > 0 && (
                <span className="text-sm font-normal text-muted-foreground ml-1">
                  ({Math.round((kpis.withClickId / kpis.totalLeads) * 100)}%)
                </span>
              )}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Top Fuente</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.topSource ? String(kpis.topSource.key ?? "—") : "—"}</div>
            {kpis.topSource && (
              <p className="text-xs text-muted-foreground">{Number(kpis.topSource.leads ?? 0)} leads</p>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Conversiones</CardTitle>
            <Megaphone className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(convData?.items ?? []).reduce((s, i) => s + Number(i.conversions ?? 0), 0).toLocaleString("es-ES")}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Chart 1: Leads by group */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">Leads por {GROUP_BY_OPTIONS.find((g) => g.value === groupBy)?.label}</CardTitle>
          <Select value={groupBy} onValueChange={setGroupBy}>
            <SelectTrigger className="w-[150px] h-8 text-xs"><SelectValue /></SelectTrigger>
            <SelectContent>
              {GROUP_BY_OPTIONS.map((o) => <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>)}
            </SelectContent>
          </Select>
        </CardHeader>
        <CardContent>
          {loadingStats ? (
            <div className="flex justify-center py-8"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={(statsData?.items ?? []).map((i) => ({ name: String(i.key ?? "—"), leads: Number(i.leads ?? 0) }))}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="leads" radius={[4, 4, 0, 0]}>
                  {(statsData?.items ?? []).map((_, idx) => (
                    <Cell key={idx} fill={BAR_COLORS[idx % BAR_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      {/* Chart 2: Pivot table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">{GROUP_BY_2D_OPTIONS.find((g) => g.value === groupBy2d)?.label}</CardTitle>
          <Select value={groupBy2d} onValueChange={setGroupBy2d}>
            <SelectTrigger className="w-[200px] h-8 text-xs"><SelectValue /></SelectTrigger>
            <SelectContent>
              {GROUP_BY_2D_OPTIONS.map((o) => <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>)}
            </SelectContent>
          </Select>
        </CardHeader>
        <CardContent>
          {loading2d ? (
            <div className="flex justify-center py-8"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
          ) : pivotData.rows.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">Sin datos para el período seleccionado</p>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-xs">—</TableHead>
                    {pivotData.cols.map((c) => <TableHead key={c} className="text-xs text-center">{c}</TableHead>)}
                    <TableHead className="text-xs text-center font-bold">Total</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {pivotData.rows.map((r) => {
                    const rowTotal = pivotData.cols.reduce((s, c) => s + (pivotData.matrix[r]?.[c] ?? 0), 0);
                    return (
                      <TableRow key={r}>
                        <TableCell className="text-xs font-medium">{r}</TableCell>
                        {pivotData.cols.map((c) => (
                          <TableCell key={c} className="text-xs text-center">{pivotData.matrix[r]?.[c] ?? 0}</TableCell>
                        ))}
                        <TableCell className="text-xs text-center font-bold">{rowTotal}</TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Chart 3: Conversions */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">Conversiones Offline por {CONV_GROUP_BY_OPTIONS.find((g) => g.value === convGroupBy)?.label}</CardTitle>
          <Select value={convGroupBy} onValueChange={setConvGroupBy}>
            <SelectTrigger className="w-[150px] h-8 text-xs"><SelectValue /></SelectTrigger>
            <SelectContent>
              {CONV_GROUP_BY_OPTIONS.map((o) => <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>)}
            </SelectContent>
          </Select>
        </CardHeader>
        <CardContent>
          {loadingConv ? (
            <div className="flex justify-center py-8"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
          ) : (convData?.items ?? []).length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">Sin datos de conversiones para el período</p>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-xs">{CONV_GROUP_BY_OPTIONS.find((g) => g.value === convGroupBy)?.label}</TableHead>
                    <TableHead className="text-xs text-center">Leads</TableHead>
                    <TableHead className="text-xs text-center">Conversiones</TableHead>
                    <TableHead className="text-xs text-center">Tasa Conv.</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {(convData?.items ?? []).map((item, idx) => {
                    const leads = Number(item.utm_rows ?? 0);
                    const conv = Number(item.conversions ?? 0);
                    const rate = leads > 0 ? ((conv / leads) * 100).toFixed(1) : "0.0";
                    return (
                      <TableRow key={idx}>
                        <TableCell className="text-xs font-medium">{String(item.key ?? "—")}</TableCell>
                        <TableCell className="text-xs text-center">{leads}</TableCell>
                        <TableCell className="text-xs text-center">{conv}</TableCell>
                        <TableCell className="text-xs text-center font-medium">{rate}%</TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
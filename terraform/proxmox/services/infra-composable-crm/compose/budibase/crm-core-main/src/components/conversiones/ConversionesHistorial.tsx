import { useState } from "react";
import { useConversionesOffline } from "@/hooks/use-api";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Loader2 } from "lucide-react";
import { StatusBadge } from "@/components/StatusBadge";
import ConversionDetailModal from "./ConversionDetailModal";

const now = new Date();
const defaultFrom = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-01`;
const defaultTo = now.toISOString().split("T")[0];

export default function ConversionesHistorial() {
  const [from, setFrom] = useState(defaultFrom);
  const [to, setTo] = useState(defaultTo);
  const [statusFilter, setStatusFilter] = useState("__all__");
  const [platformFilter, setPlatformFilter] = useState("__all__");
  const [eventFilter, setEventFilter] = useState("__all__");
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const { data, isLoading } = useConversionesOffline({
    sync_status: statusFilter === "__all__" ? undefined : statusFilter,
    platform: platformFilter === "__all__" ? undefined : platformFilter,
    event_name: eventFilter === "__all__" ? undefined : eventFilter,
    from,
    to,
    limit: 50,
  });

  const items = data?.items ?? [];

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap items-end gap-3 p-3 rounded-lg border bg-card">
        <div className="space-y-1">
          <Label className="text-xs">Desde</Label>
          <Input type="date" value={from} onChange={(e) => setFrom(e.target.value)} className="w-[140px] h-8 text-xs" />
        </div>
        <div className="space-y-1">
          <Label className="text-xs">Hasta</Label>
          <Input type="date" value={to} onChange={(e) => setTo(e.target.value)} className="w-[140px] h-8 text-xs" />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[130px] h-8 text-xs"><SelectValue placeholder="Estado" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="__all__">Todos</SelectItem>
            <SelectItem value="PENDING">Pendiente</SelectItem>
            <SelectItem value="SYNCED">Enviada</SelectItem>
            <SelectItem value="FAILED">Fallida</SelectItem>
          </SelectContent>
        </Select>
        <Select value={platformFilter} onValueChange={setPlatformFilter}>
          <SelectTrigger className="w-[130px] h-8 text-xs"><SelectValue placeholder="Plataforma" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="__all__">Todas</SelectItem>
            <SelectItem value="GOOGLE">Google</SelectItem>
            <SelectItem value="FACEBOOK">Meta</SelectItem>
            <SelectItem value="LINKEDIN">LinkedIn</SelectItem>
            <SelectItem value="BING">Bing</SelectItem>
          </SelectContent>
        </Select>
        <Select value={eventFilter} onValueChange={setEventFilter}>
          <SelectTrigger className="w-[150px] h-8 text-xs"><SelectValue placeholder="Evento" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="__all__">Todos</SelectItem>
            <SelectItem value="Lead_Submitted">Lead_Submitted</SelectItem>
            <SelectItem value="Lead_Qualified">Lead_Qualified</SelectItem>
            <SelectItem value="Lead_Won">Lead_Won</SelectItem>
            <SelectItem value="Purchase">Purchase</SelectItem>
            <SelectItem value="Custom">Custom</SelectItem>
          </SelectContent>
        </Select>
        <span className="text-xs text-muted-foreground">{data?.total ?? 0} registros</span>
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="flex justify-center py-12"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
      ) : items.length === 0 ? (
        <p className="text-sm text-muted-foreground text-center py-12">Sin conversiones para los filtros seleccionados</p>
      ) : (
        <div className="rounded-lg border overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="text-xs">Fecha</TableHead>
                <TableHead className="text-xs">Evento</TableHead>
                <TableHead className="text-xs">Plataforma</TableHead>
                <TableHead className="text-xs text-right">Valor</TableHead>
                <TableHead className="text-xs">Click ID</TableHead>
                <TableHead className="text-xs">Estado</TableHead>
                <TableHead className="text-xs text-center">Reintentos</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((item) => (
                <TableRow
                  key={String(item.id)}
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => setSelectedId(String(item.id))}
                >
                  <TableCell className="text-xs">
                    {item.created_at ? new Date(String(item.created_at)).toLocaleString("es-ES", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }) : "—"}
                  </TableCell>
                  <TableCell><StatusBadge value={String(item.event_name ?? "")} /></TableCell>
                  <TableCell><StatusBadge value={String(item.platform ?? "")} /></TableCell>
                  <TableCell className="text-xs text-right font-medium">
                    {item.conversion_value ? `€${Number(item.conversion_value).toLocaleString("es-ES")}` : "—"}
                  </TableCell>
                  <TableCell className="text-xs font-mono truncate max-w-[120px]">{String(item.click_id ?? "—").substring(0, 20)}</TableCell>
                  <TableCell><StatusBadge value={String(item.sync_status ?? "")} /></TableCell>
                  <TableCell className="text-xs text-center">{String(item.retry_count ?? 0)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
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

import { useState } from "react";
import { useUtm, useUtmDetail } from "@/hooks/use-api";
import { DataTable, Column } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Filter, ExternalLink, User, Clock, Megaphone, Target, Key, Globe } from "lucide-react";
import { cn } from "@/lib/utils";

const PLATFORMS = ["GOOGLE", "BING", "LINKEDIN", "FACEBOOK"];
const DEVICES = ["desktop", "mobile", "tablet"];

function formatDate(v: unknown) {
  if (!v) return "—";
  try {
    return new Date(String(v)).toLocaleDateString("es-ES", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" });
  } catch { return "—"; }
}

function formatDateShort(v: unknown) {
  if (!v) return "—";
  try {
    return new Date(String(v)).toLocaleDateString("es-ES", { day: "2-digit", month: "short", year: "numeric" });
  } catch { return "—"; }
}

function ClickIdIndicator({ record }: { record: Record<string, unknown> }) {
  const ids = [];
  if (record.gclid) ids.push("G");
  if (record.fbclid) ids.push("F");
  if (record.li_fat_id) ids.push("L");
  if (record.msclkid) ids.push("B");
  if (ids.length === 0) return <span className="text-muted-foreground text-xs">—</span>;
  return (
    <div className="flex gap-0.5">
      {ids.map((id) => (
        <span key={id} className="inline-flex items-center justify-center w-5 h-5 rounded text-[10px] font-bold bg-primary/15 text-primary">
          {id}
        </span>
      ))}
    </div>
  );
}

const columns: Column[] = [
  { key: "created_at", label: "Fecha", render: (v) => <span className="text-xs">{formatDateShort(v)}</span> },
  { key: "contacto_nombre", label: "Contacto", render: (v) => <span className="font-medium">{String(v ?? "—")}</span> },
  { key: "utm_campaign", label: "Campaña", render: (v) => v ? <span className="text-xs font-mono">{String(v)}</span> : "—" },
  { key: "utm_source", label: "Fuente", render: (v) => v ? <StatusBadge value={String(v)} /> : "—" },
  { key: "utm_medium", label: "Medio", render: (v) => v ? <span className="text-xs">{String(v)}</span> : "—" },
  { key: "device", label: "Device", render: (v) => v ? <span className="text-xs capitalize">{String(v)}</span> : "—" },
  { key: "ads_platform", label: "Plataforma", render: (v) => v ? <StatusBadge value={String(v)} /> : "—" },
  {
    key: "id", label: "Click IDs", render: (_, row) => <ClickIdIndicator record={row!} />,
  },
];

// ─── Detail Modal ────────────────────────────────────────────
function UTMDetail({ utmId, onClose }: { utmId: string; onClose: () => void }) {
  const { data, isLoading } = useUtmDetail(utmId);

  if (isLoading) return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-lg">
        <div className="flex justify-center py-12"><div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" /></div>
      </DialogContent>
    </Dialog>
  );

  const d = data ?? {};

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-lg max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Detalles de Tracking</DialogTitle>
          <DialogDescription>Registro UTM completo</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Contacto */}
          <Section icon={<User size={14} />} title="Contacto">
            <p className="font-medium">{String(d.contacto_nombre ?? "—")}</p>
          </Section>

          {/* Temporal */}
          <Section icon={<Clock size={14} />} title="Información Temporal">
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div><span className="text-muted-foreground">Primera visita:</span> {formatDate(d.first_visit_at)}</div>
              <div><span className="text-muted-foreground">Creado:</span> {formatDate(d.created_at)}</div>
            </div>
          </Section>

          {/* UTM Params */}
          <Section icon={<Megaphone size={14} />} title="Parámetros UTM">
            <div className="grid grid-cols-2 gap-2 text-sm">
              <Field label="Campaña" value={d.utm_campaign} />
              <Field label="Fuente" value={d.utm_source} />
              <Field label="Medio" value={d.utm_medium} />
              <Field label="Contenido" value={d.utm_content} />
              <Field label="Término" value={d.utm_term} />
            </div>
          </Section>

          {/* Ad Info */}
          <Section icon={<Target size={14} />} title="Información Publicitaria">
            <div className="grid grid-cols-2 gap-2 text-sm">
              <Field label="Plataforma" value={d.ads_platform} badge />
              <Field label="Grupo Anuncios" value={d.adgroup} />
              <Field label="Palabra Clave" value={d.keyword} />
              <Field label="Creativo" value={d.creative} />
              <Field label="Ubicación" value={d.placement} />
              <Field label="Dispositivo" value={d.device} />
            </div>
          </Section>

          {/* Click IDs */}
          <Section icon={<Key size={14} />} title="Click IDs (Conversiones Offline)">
            <div className="space-y-1 text-sm">
              <ClickIdField label="Google (gclid)" value={d.gclid} platform="Google Ads" />
              <ClickIdField label="Meta (fbclid)" value={d.fbclid} platform="Meta Ads" />
              <ClickIdField label="LinkedIn (li_fat_id)" value={d.li_fat_id} platform="LinkedIn Ads" />
              <ClickIdField label="Bing (msclkid)" value={d.msclkid} platform="Bing Ads" />
              {!d.gclid && !d.fbclid && !d.li_fat_id && !d.msclkid && (
                <p className="text-muted-foreground italic text-xs">Sin click IDs — no se pueden enviar conversiones offline</p>
              )}
            </div>
          </Section>

          {/* URLs */}
          <Section icon={<Globe size={14} />} title="URLs">
            <div className="space-y-2 text-sm">
              {d.landing_url && (
                <div>
                  <span className="text-xs text-muted-foreground">Landing:</span>
                  <a href={String(d.landing_url)} target="_blank" rel="noreferrer" className="block text-xs text-primary underline truncate">
                    {String(d.landing_url)} <ExternalLink size={10} className="inline" />
                  </a>
                </div>
              )}
              {d.referrer_url && (
                <div>
                  <span className="text-xs text-muted-foreground">Referrer:</span>
                  <a href={String(d.referrer_url)} target="_blank" rel="noreferrer" className="block text-xs text-primary underline truncate">
                    {String(d.referrer_url)} <ExternalLink size={10} className="inline" />
                  </a>
                </div>
              )}
              {!d.landing_url && !d.referrer_url && (
                <p className="text-muted-foreground italic text-xs">Sin URLs registradas</p>
              )}
            </div>
          </Section>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function Section({ icon, title, children }: { icon: React.ReactNode; title: string; children: React.ReactNode }) {
  return (
    <div>
      <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2 flex items-center gap-1.5">
        {icon} {title}
      </h4>
      {children}
    </div>
  );
}

function Field({ label, value, badge }: { label: string; value: unknown; badge?: boolean }) {
  return (
    <div>
      <span className="text-muted-foreground">{label}:</span>{" "}
      {value ? (badge ? <StatusBadge value={String(value)} /> : <span>{String(value)}</span>) : <span className="text-muted-foreground">—</span>}
    </div>
  );
}

function ClickIdField({ label, value, platform }: { label: string; value: unknown; platform: string }) {
  if (!value) return null;
  return (
    <div className="flex items-start gap-2">
      <span className="text-muted-foreground whitespace-nowrap">{label}:</span>
      <div>
        <span className="font-mono text-xs break-all">{String(value)}</span>
        <p className="text-[10px] text-muted-foreground">Rastreable en {platform}</p>
      </div>
    </div>
  );
}

// ─── Main List ───────────────────────────────────────────────
export default function UTMLista() {
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const [showFilter, setShowFilter] = useState(false);
  const [campaign, setCampaign] = useState("");
  const [source, setSource] = useState("");
  const [medium, setMedium] = useState("");
  const [platform, setPlatform] = useState("");
  const [device, setDevice] = useState("");
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [viewingId, setViewingId] = useState<string | null>(null);

  const hasFilters = !!(campaign || source || medium || platform || device || from || to);

  const { data, isLoading } = useUtm({
    q: search || undefined,
    offset,
    limit: 50,
    utm_campaign: campaign || undefined,
    utm_source: source || undefined,
    utm_medium: medium || undefined,
    ads_platform: platform || undefined,
    device: device || undefined,
    created_from: from || undefined,
    created_to: to || undefined,
  });

  const clearFilters = () => {
    setCampaign(""); setSource(""); setMedium(""); setPlatform(""); setDevice(""); setFrom(""); setTo("");
    setOffset(0);
  };

  return (
    <>
      <PageHeader
        title="Registros UTM"
        subtitle={data ? `${data.total} registros` : undefined}
        searchValue={search}
        onSearch={(q) => { setSearch(q); setOffset(0); }}
        searchPlaceholder="Buscar por source, campaign, gclid, landing..."
        actions={
          <Button size="sm" variant="outline" onClick={() => setShowFilter(!showFilter)} className={cn("gap-1", hasFilters && "border-primary text-primary")}>
            <Filter size={14} /> Filtros {hasFilters && "•"}
          </Button>
        }
      />

      {/* Filters */}
      {showFilter && (
        <div className="flex flex-wrap items-end gap-3 mb-4 p-3 rounded-lg border bg-card">
          <div className="space-y-1">
            <Label className="text-xs">Campaña</Label>
            <Input placeholder="spring_sale..." value={campaign} onChange={(e) => { setCampaign(e.target.value); setOffset(0); }} className="w-[160px] h-8 text-xs" />
          </div>
          <div className="space-y-1">
            <Label className="text-xs">Fuente</Label>
            <Input placeholder="google..." value={source} onChange={(e) => { setSource(e.target.value); setOffset(0); }} className="w-[130px] h-8 text-xs" />
          </div>
          <div className="space-y-1">
            <Label className="text-xs">Medio</Label>
            <Input placeholder="cpc..." value={medium} onChange={(e) => { setMedium(e.target.value); setOffset(0); }} className="w-[100px] h-8 text-xs" />
          </div>
          <div className="space-y-1">
            <Label className="text-xs">Plataforma</Label>
            <Select value={platform || "__all__"} onValueChange={(v) => { setPlatform(v === "__all__" ? "" : v); setOffset(0); }}>
              <SelectTrigger className="w-[130px] h-8 text-xs"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="__all__">Todas</SelectItem>
                {PLATFORMS.map((p) => <SelectItem key={p} value={p}>{p}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1">
            <Label className="text-xs">Device</Label>
            <Select value={device || "__all__"} onValueChange={(v) => { setDevice(v === "__all__" ? "" : v); setOffset(0); }}>
              <SelectTrigger className="w-[120px] h-8 text-xs"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="__all__">Todos</SelectItem>
                {DEVICES.map((d) => <SelectItem key={d} value={d}>{d}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1">
            <Label className="text-xs">Desde</Label>
            <Input type="date" value={from} onChange={(e) => { setFrom(e.target.value); setOffset(0); }} className="w-[140px] h-8 text-xs" />
          </div>
          <div className="space-y-1">
            <Label className="text-xs">Hasta</Label>
            <Input type="date" value={to} onChange={(e) => { setTo(e.target.value); setOffset(0); }} className="w-[140px] h-8 text-xs" />
          </div>
          {hasFilters && (
            <Button size="sm" variant="ghost" className="h-8 text-xs" onClick={clearFilters}>Limpiar</Button>
          )}
        </div>
      )}

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        total={data?.total}
        limit={data?.limit ?? 50}
        offset={offset}
        onPageChange={setOffset}
        onRowClick={(row) => setViewingId(String(row.id))}
        loading={isLoading}
      />

      {viewingId && <UTMDetail utmId={viewingId} onClose={() => setViewingId(null)} />}
    </>
  );
}
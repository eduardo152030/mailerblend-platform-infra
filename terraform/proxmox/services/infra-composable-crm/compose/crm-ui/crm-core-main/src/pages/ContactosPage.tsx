import { useState, useEffect, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import { useContacts, useContactSnapshot, useCreateContact } from "@/hooks/use-api";
import { DataTable, Column } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Loader2, Mail, Phone, Building2, MapPin, Globe, FileText, Clock,
  Eye, Pencil, Plus, User, Shield, Zap, ChevronDown, ChevronRight,
  ExternalLink, Tag, Linkedin,
} from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { formatDistanceToNow } from "date-fns";
import { es } from "date-fns/locale";

// ─── Canonical values ───────────────────────────────────────────
const ESTADOS = ["ACTIVO", "INACTIVO", "DESCALIFICADO", "BLOQUEADO"] as const;
const ORIGENES = ["FORMULARIO_WEB", "MANUAL", "LINKEDIN_SOURCING", "IMPORTACION", "REFERIDO", "EVENTO"] as const;
const PACKS = ["GUARDIAN", "MOTOR", "FORTALEZA", "NO_ASIGNADO"] as const;
const TIPOS_EMPRESA = ["Pyme", "Agencia", "Emprendedor", "Startup"] as const;
const COMPANY_SIZES = ["1-10", "11-50", "51-200", "201-500", "501+"] as const;
const PAISES = [
  { code: "ES", label: "España" }, { code: "US", label: "Estados Unidos" },
  { code: "FR", label: "Francia" }, { code: "DE", label: "Alemania" },
  { code: "GB", label: "Reino Unido" }, { code: "IT", label: "Italia" },
  { code: "PT", label: "Portugal" }, { code: "MX", label: "México" },
  { code: "AR", label: "Argentina" }, { code: "CO", label: "Colombia" },
  { code: "CL", label: "Chile" }, { code: "BR", label: "Brasil" },
] as const;

function scoreLabel(score: number | null | undefined) {
  if (score == null) return { stars: "", color: "text-muted-foreground", label: "—" };
  if (score >= 80) return { stars: "⭐⭐⭐", color: "text-emerald-600 dark:text-emerald-400", label: "Hot" };
  if (score >= 60) return { stars: "⭐⭐", color: "text-green-600 dark:text-green-400", label: "Warm" };
  if (score >= 40) return { stars: "⭐", color: "text-yellow-600 dark:text-yellow-400", label: "Cold" };
  return { stars: "⚪", color: "text-muted-foreground", label: "Very Cold" };
}

// ─── Helpers ────────────────────────────────────────────────────
function useDebounce(value: string, delay: number) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

function formatDate(v: unknown) {
  if (!v) return "—";
  try { return new Date(String(v)).toLocaleDateString("es-ES", { day: "2-digit", month: "short", year: "numeric" }); }
  catch { return "—"; }
}

function relativeTime(v: unknown) {
  if (!v) return "—";
  try { return formatDistanceToNow(new Date(String(v)), { addSuffix: true, locale: es }); }
  catch { return "—"; }
}

// ─── Table columns ──────────────────────────────────────────────
const columns: Column[] = [
  { key: "nombre", label: "Nombre", render: (v) => <span className="font-medium">{String(v ?? "—")}</span> },
  { key: "company_name", label: "Empresa" },
  { key: "email", label: "Email" },
  { key: "cargo", label: "Cargo" },
  { key: "estado", label: "Estado", render: (v) => <StatusBadge value={v as string} /> },
  { key: "origen", label: "Origen", render: (v) => v ? <Badge variant="outline" className="text-xs">{String(v)}</Badge> : <span className="text-muted-foreground">—</span> },
  { key: "pack_asignado", label: "Pack" },
  { key: "lead_score", label: "Score", render: (v) => {
    const s = scoreLabel(v as number | null);
    return v != null ? <span className={`font-medium ${s.color}`}>{s.stars} {String(v)}</span> : <span className="text-muted-foreground">—</span>;
  }, className: "text-right" },
  { key: "ciudad", label: "Ciudad" },
  { key: "updated_at", label: "Updated", render: (v) => <span className="text-xs text-muted-foreground">{relativeTime(v)}</span> },
];

// ─── Main page ──────────────────────────────────────────────────
export default function ContactosPage() {
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const [params, setParams] = useSearchParams();
  const linkedContact = params.get("contacto");
  const [snapshotId, setSnapshotId] = useState<string | null>(null);
  const [editContact, setEditContact] = useState<Record<string, unknown> | null>(null);
  const [showCreate, setShowCreate] = useState(false);

  const deepLink = linkedContact && /^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/i.test(linkedContact)
    ? linkedContact
    : null;
  function closeSnapshot() {
    setSnapshotId(null);
    if (linkedContact) {
      const next = new URLSearchParams(params);
      next.delete("contacto");
      setParams(next, { replace: true });
    }
  }

  // Filters
  const [filterEstado, setFilterEstado] = useState("__all__");
  const [filterOrigen, setFilterOrigen] = useState("__all__");
  const [filterPack, setFilterPack] = useState("__all__");
  const [filterTipo, setFilterTipo] = useState("__all__");
  const [filterScoreRange, setFilterScoreRange] = useState("__all__");

  const debouncedQ = useDebounce(search, 400);

  const scoreRanges: Record<string, { min?: number; max?: number }> = {
    "__all__": {},
    "hot": { min: 80 },
    "warm": { min: 60, max: 79 },
    "cold": { min: 40, max: 59 },
    "very_cold": { max: 39 },
  };
  const sr = scoreRanges[filterScoreRange] ?? {};

  const { data, isLoading } = useContacts({
    q: debouncedQ || undefined,
    offset,
    limit: 50,
    estado: filterEstado === "__all__" ? undefined : filterEstado,
    origen: filterOrigen === "__all__" ? undefined : filterOrigen,
    pack_asignado: filterPack === "__all__" ? undefined : filterPack,
    tipo_empresa: filterTipo === "__all__" ? undefined : filterTipo,
    lead_score_min: sr.min,
    lead_score_max: sr.max,
  });

  const resetFilters = () => {
    setFilterEstado("__all__");
    setFilterOrigen("__all__");
    setFilterPack("__all__");
    setFilterTipo("__all__");
    setFilterScoreRange("__all__");
    setOffset(0);
  };

  const hasActiveFilters = [filterEstado, filterOrigen, filterPack, filterTipo, filterScoreRange].some((f) => f !== "__all__");

  return (
    <>
      <PageHeader
        title="Contactos"
        subtitle={data ? `${data.total} contactos` : undefined}
        searchValue={search}
        onSearch={(q) => { setSearch(q); setOffset(0); }}
        searchPlaceholder="Buscar por nombre, email, empresa..."
        actions={
          <Button size="sm" onClick={() => setShowCreate(true)}>
            <Plus className="h-4 w-4 mr-1" /> Nuevo contacto
          </Button>
        }
      />

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2 mb-4">
        <Select value={filterEstado} onValueChange={(v) => { setFilterEstado(v); setOffset(0); }}>
          <SelectTrigger className="w-[130px] h-8 text-xs">
            <SelectValue placeholder="Estado" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="__all__">Todos los estados</SelectItem>
            {ESTADOS.map((e) => <SelectItem key={e} value={e}>{e}</SelectItem>)}
          </SelectContent>
        </Select>

        <Select value={filterOrigen} onValueChange={(v) => { setFilterOrigen(v); setOffset(0); }}>
          <SelectTrigger className="w-[150px] h-8 text-xs">
            <SelectValue placeholder="Origen" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="__all__">Todos los orígenes</SelectItem>
            {ORIGENES.map((o) => <SelectItem key={o} value={o}>{o.replace(/_/g, " ")}</SelectItem>)}
          </SelectContent>
        </Select>

        <Select value={filterPack} onValueChange={(v) => { setFilterPack(v); setOffset(0); }}>
          <SelectTrigger className="w-[130px] h-8 text-xs">
            <SelectValue placeholder="Pack" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="__all__">Todos los packs</SelectItem>
            {PACKS.map((p) => <SelectItem key={p} value={p}>{p}</SelectItem>)}
          </SelectContent>
        </Select>

        <Select value={filterTipo} onValueChange={(v) => { setFilterTipo(v); setOffset(0); }}>
          <SelectTrigger className="w-[140px] h-8 text-xs">
            <SelectValue placeholder="Tipo empresa" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="__all__">Todos los tipos</SelectItem>
            {TIPOS_EMPRESA.map((t) => <SelectItem key={t} value={t}>{t}</SelectItem>)}
          </SelectContent>
        </Select>

        <Select value={filterScoreRange} onValueChange={(v) => { setFilterScoreRange(v); setOffset(0); }}>
          <SelectTrigger className="w-[140px] h-8 text-xs">
            <SelectValue placeholder="Lead Score" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="__all__">Todos los scores</SelectItem>
            <SelectItem value="hot">⭐⭐⭐ Hot (80-100)</SelectItem>
            <SelectItem value="warm">⭐⭐ Warm (60-79)</SelectItem>
            <SelectItem value="cold">⭐ Cold (40-59)</SelectItem>
            <SelectItem value="very_cold">⚪ Very Cold (0-39)</SelectItem>
          </SelectContent>
        </Select>

        {hasActiveFilters && (
          <Button variant="ghost" size="sm" className="h-8 text-xs" onClick={resetFilters}>
            ✕ Limpiar filtros
          </Button>
        )}
      </div>

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        total={data?.total}
        limit={data?.limit ?? 50}
        offset={offset}
        onPageChange={setOffset}
        onRowClick={(row) => setSnapshotId(row.id as string)}
        loading={isLoading}
      />

      {/* Snapshot drawer */}
      <SnapshotDrawer
        contactId={snapshotId ?? deepLink}
        onClose={closeSnapshot}
        onEdit={(c) => { closeSnapshot(); setEditContact(c); }}
      />

      {/* Create / Edit modal */}
      <ContactFormModal
        open={showCreate || !!editContact}
        onClose={() => { setShowCreate(false); setEditContact(null); }}
        initialData={editContact}
      />
    </>
  );
}

// ─── Snapshot Drawer ────────────────────────────────────────────
function SnapshotDrawer({ contactId, onClose, onEdit }: {
  contactId: string | null;
  onClose: () => void;
  onEdit: (c: Record<string, unknown>) => void;
}) {
  const { data: snapshot, isLoading } = useContactSnapshot(contactId);

  const contact = (snapshot as Record<string, unknown>)?.contact as Record<string, unknown> | undefined;
  const related = (snapshot as Record<string, unknown>)?.related as Record<string, unknown> | undefined;
  const utmList = (related?.parametros_utm ?? []) as Record<string, unknown>[];
  const formList = (related?.formulario_web ?? []) as Record<string, unknown>[];
  const opList = (related?.oportunidades ?? []) as Record<string, unknown>[];
  const histList = (related?.historial ?? []) as Record<string, unknown>[];
  const pendList = (related?.pendientes ?? []) as Record<string, unknown>[];
  const presList = (related?.presupuestos ?? []) as Record<string, unknown>[];
  const factList = (related?.facturas ?? []) as Record<string, unknown>[];

  return (
    <Sheet open={!!contactId} onOpenChange={() => onClose()}>
      <SheetContent className="w-full sm:max-w-2xl overflow-y-auto">
        <SheetHeader>
          <div className="flex items-center justify-between">
            <SheetTitle>{contact?.nombre ? String(contact.nombre) : "Contacto"}</SheetTitle>
            {contact && (
              <Button variant="outline" size="sm" onClick={() => onEdit(contact)}>
                <Pencil className="h-3.5 w-3.5 mr-1" /> Editar
              </Button>
            )}
          </div>
          {/* Hero summary bar */}
          {contact && (
            <div className="flex flex-wrap items-center gap-2 mt-2">
              <StatusBadge value={contact.estado as string} />
              {contact.pack_asignado && contact.pack_asignado !== "NO_ASIGNADO" && (
                <Badge variant="outline" className="text-xs">{String(contact.pack_asignado)}</Badge>
              )}
              <LeadScoreBadge score={contact.lead_score as number | null} />
              {contact.places_name && (
                <Badge variant="secondary" className="text-xs gap-1">
                  <MapPin size={10} /> ✓ Google Places
                </Badge>
              )}
              {contact.linkedin_url && (
                <Badge variant="secondary" className="text-xs gap-1">
                  <Linkedin size={10} /> LinkedIn
                </Badge>
              )}
            </div>
          )}
        </SheetHeader>

        {isLoading ? (
          <SnapshotSkeleton />
        ) : contact ? (
          <Tabs defaultValue="perfil" className="mt-4">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="perfil">Perfil</TabsTrigger>
              <TabsTrigger value="deals">Deals {opList.length > 0 && `(${opList.length})`}</TabsTrigger>
              <TabsTrigger value="historial">Historial {histList.length > 0 && `(${histList.length})`}</TabsTrigger>
              <TabsTrigger value="datos">Datos</TabsTrigger>
            </TabsList>

            {/* ── Perfil ─────────────────────── */}
            <TabsContent value="perfil" className="mt-4 space-y-6">
              {/* Contact info */}
              <section>
                <SectionTitle icon={<User size={14} />} title="Información de contacto" />
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-2">
                  <Field icon={<Mail size={13} />} label="Email" value={contact.email} />
                  <Field icon={<Phone size={13} />} label="Teléfono" value={contact.telefono} />
                  <Field icon={<Building2 size={13} />} label="Empresa" value={contact.company_name} />
                  <Field label="Cargo" value={contact.cargo} />
                  <Field label="Tipo empresa" value={contact.tipo_empresa} />
                  <Field label="Tamaño" value={contact.company_size} />
                  <Field label="Industria" value={contact.industry} />
                  <Field icon={<MapPin size={13} />} label="Ciudad" value={contact.ciudad} />
                  <Field label="País" value={contact.pais} />
                  <Field label="Dirección" value={contact.direccion} />
                  {contact.website && <Field icon={<Globe size={13} />} label="Web" value={contact.website} />}
                  {contact.linkedin_url && <Field icon={<ExternalLink size={13} />} label="LinkedIn" value={contact.linkedin_url} />}
                </div>
                <div className="grid grid-cols-3 gap-2 mt-2">
                  <Field label="Estado" value={contact.estado} />
                  <Field label="Origen" value={contact.origen} />
                  <Field label="Pack" value={contact.pack_asignado} />
                  <Field label="Creado" value={formatDate(contact.created_at)} />
                  <Field label="Updated" value={relativeTime(contact.updated_at)} />
                </div>
                {contact.notas && (
                  <div className="mt-2">
                    <Field label="Notas" value={contact.notas} />
                  </div>
                )}
              </section>

              {/* Lead Score */}
              <LeadScoreSection contact={contact} />

              {/* Consent */}
              <section>
                <SectionTitle icon={<Shield size={14} />} title="Consentimientos GDPR" />
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-2">
                  <Field label="GDPR" value={contact.gdpr_consent === true ? "✅ Sí" : "❌ No"} />
                  <Field label="Fecha GDPR" value={formatDate(contact.gdpr_consent_date)} />
                  <Field label="Marketing" value={contact.marketing_consent === true ? "✅ Sí" : "❌ No"} />
                </div>
              </section>

              {/* Enrichment signals */}
              <EnrichmentSection contact={contact} />

              {/* Pendientes */}
              {pendList.length > 0 && (
                <section>
                  <SectionTitle icon={<Tag size={14} />} title={`Pendientes (${pendList.length})`} />
                  <div className="space-y-1 mt-2">
                    {pendList.slice(0, 10).map((p, i) => (
                      <div key={i} className="flex items-center justify-between text-sm p-2 rounded-md bg-muted/30">
                        <span>{String(p.title ?? p.subject ?? "")}</span>
                        <StatusBadge value={p.status as string} />
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* Presupuestos */}
              {presList.length > 0 && (
                <section>
                  <SectionTitle title={`Presupuestos (${presList.length})`} />
                  <div className="space-y-1 mt-2">
                    {presList.map((p, i) => (
                      <div key={i} className="text-sm p-2 rounded-md bg-muted/30 flex justify-between">
                        <span>{String(p.quote_number ?? "")} — {String(p.title ?? p.deal_name ?? "")}</span>
                        <StatusBadge value={p.status as string} />
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* Facturas */}
              {factList.length > 0 && (
                <section>
                  <SectionTitle title={`Facturas (${factList.length})`} />
                  <div className="space-y-1 mt-2">
                    {factList.map((f, i) => (
                      <div key={i} className="text-sm p-2 rounded-md bg-muted/30 flex justify-between">
                        <span>{String(f.numero_factura ?? f.id ?? "")}</span>
                        <StatusBadge value={f.estado as string} />
                      </div>
                    ))}
                  </div>
                </section>
              )}
            </TabsContent>

            {/* ── Deals ──────────────────────── */}
            <TabsContent value="deals" className="mt-4 space-y-2">
              {opList.length > 0 ? opList.map((op, i) => (
                <div key={i} className="flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-lg border bg-muted/20 gap-2">
                  <div>
                    <div className="font-medium text-sm">{String(op.deal_name ?? "—")}</div>
                    <div className="text-xs text-muted-foreground">
                      {String(op.pack ?? "")} · Prob: {op.probabilidad != null ? `${op.probabilidad}%` : "—"} · {relativeTime(op.updated_at)}
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <StatusBadge value={op.prioridad as string} type="priority" />
                    <StatusBadge value={op.lead_tag as string} />
                    <StatusBadge value={op.estado as string} />
                  </div>
                </div>
              )) : <p className="text-sm text-muted-foreground text-center py-8">Sin oportunidades</p>}
            </TabsContent>

            {/* ── Historial ──────────────────── */}
            <TabsContent value="historial" className="mt-4">
              {histList.length > 0 ? (
                <div className="space-y-1 max-h-[60vh] overflow-y-auto">
                  {histList.map((h, i) => (
                    <HistoryItem key={i} item={h} />
                  ))}
                </div>
              ) : <p className="text-sm text-muted-foreground text-center py-8">Sin historial</p>}
            </TabsContent>

            {/* ── Datos (UTM + Formularios) ─── */}
            <TabsContent value="datos" className="mt-4 space-y-4">
              {/* Formularios */}
              <section>
                <SectionTitle icon={<FileText size={14} />} title={`Formularios (${formList.length})`} />
                {formList.length > 0 ? formList.map((f, i) => (
                  <Card key={i} className="mt-2">
                    <CardContent className="pt-4 grid grid-cols-1 sm:grid-cols-2 gap-2">
                      <Field label="Servicio" value={f.servicio_relacionado} />
                      <Field label="Cómo nos conociste" value={f.como_nos_conociste} />
                      <Field label="Tipo solución" value={f.tipo_solucion} />
                      <Field label="Situación infra." value={f.situacion_infraestructura} />
                      <Field label="Problema fiabilidad" value={f.problema_fiabilidad} />
                      <Field label="Parte infra." value={f.parte_infraestructura} />
                      <Field label="Herramientas a conectar" value={f.herramientas_conectar} />
                      <Field label="Tipo soporte" value={f.tipo_soporte} />
                      <Field label="Origen" value={f.origen} />
                      <div className="sm:col-span-2"><Field label="Mensaje" value={f.mensaje} /></div>
                      <Field label="Urgencia" value={f.urgencia} />
                      <Field label="Fecha" value={formatDate(f.submitted_at)} />
                      <Field label="IP" value={f.ip_address} />
                      <div className="sm:col-span-2 text-xs text-muted-foreground truncate">{f.user_agent ? String(f.user_agent) : "—"}</div>
                    </CardContent>
                  </Card>
                )) : <p className="text-sm text-muted-foreground text-center py-4">Sin formularios</p>}
              </section>

              {/* UTM */}
              <section>
                <SectionTitle icon={<Globe size={14} />} title={`UTM (${utmList.length})`} />
                {utmList.length > 0 ? utmList.map((u, i) => (
                  <Card key={i} className="mt-2">
                    <CardContent className="pt-4 grid grid-cols-1 sm:grid-cols-3 gap-2">
                      <Field label="Source" value={u.utm_source} />
                      <Field label="Medium" value={u.utm_medium} />
                      <Field label="Campaign" value={u.utm_campaign} />
                      <Field label="Term" value={u.utm_term} />
                      <Field label="Content" value={u.utm_content} />
                      <Field label="Platform" value={u.ads_platform} />
                      <Field label="Device" value={u.device} />
                      <Field label="GCLID" value={u.gclid} />
                      <Field label="FBCLID" value={u.fbclid} />
                      <div className="sm:col-span-3"><Field label="Landing" value={u.landing_url} /></div>
                      {u.referrer_url && <div className="sm:col-span-3"><Field label="Referrer" value={u.referrer_url} /></div>}
                    </CardContent>
                  </Card>
                )) : <p className="text-sm text-muted-foreground text-center py-4">Sin datos UTM</p>}
              </section>
            </TabsContent>
          </Tabs>
        ) : null}
      </SheetContent>
    </Sheet>
  );
}

// ─── Lead Score Badge ───────────────────────────────────────────
function LeadScoreBadge({ score }: { score: number | null | undefined }) {
  const s = scoreLabel(score);
  if (score == null) return null;
  return (
    <Badge variant="outline" className={`text-xs gap-1 ${s.color}`}>
      {s.stars} {score} pts — {s.label}
    </Badge>
  );
}

// ─── Lead Score Section with breakdown ──────────────────────────
function LeadScoreSection({ contact }: { contact: Record<string, unknown> }) {
  const score = contact.lead_score as number | null;
  const breakdown = contact.score_breakdown as Record<string, number> | null;
  const s = scoreLabel(score);

  return (
    <section>
      <SectionTitle icon={<Zap size={14} />} title={`Lead Scoring${score != null ? ` (${score} puntos)` : ""}`} />
      <div className="mt-2">
        {score != null ? (
          <div className="space-y-3">
            {/* Score bar */}
            <div className="flex items-center gap-3">
              <div className="flex-1 h-3 rounded-full bg-muted overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    score >= 80 ? "bg-emerald-500" :
                    score >= 60 ? "bg-green-500" :
                    score >= 40 ? "bg-yellow-500" :
                    "bg-muted-foreground/40"
                  }`}
                  style={{ width: `${Math.min(score, 100)}%` }}
                />
              </div>
              <span className={`text-sm font-bold ${s.color}`}>{s.stars} {score}</span>
            </div>
            <div className="text-xs text-muted-foreground">
              Categoría: <span className={`font-semibold ${s.color}`}>{s.label}</span>
              {contact.score_calculated_at && (
                <> · Calculado {relativeTime(contact.score_calculated_at)}</>
              )}
            </div>

            {/* Breakdown */}
            {breakdown && Object.keys(breakdown).length > 0 && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                {Object.entries(breakdown).map(([key, val]) => (
                  <div key={key} className="flex items-center justify-between text-xs p-2 rounded-md bg-muted/30">
                    <span className="text-muted-foreground">{key.replace(/_/g, " ")}</span>
                    <span className={`font-semibold ${val > 0 ? "text-emerald-600 dark:text-emerald-400" : "text-muted-foreground"}`}>
                      {val > 0 ? `+${val}` : val}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">Sin score calculado</p>
        )}
      </div>
    </section>
  );
}

// ─── Snapshot Skeleton (loading state) ──────────────────────────
function SnapshotSkeleton() {
  return (
    <div className="mt-6 space-y-6 animate-pulse">
      {/* Tab bar skeleton */}
      <div className="flex gap-2">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-9 w-20 rounded-md bg-muted" />
        ))}
      </div>
      {/* Section skeletons */}
      {[1, 2, 3].map((s) => (
        <div key={s} className="space-y-2">
          <div className="h-4 w-40 rounded bg-muted" />
          <div className="grid grid-cols-2 gap-2">
            {[1, 2, 3, 4].map((f) => (
              <div key={f} className="h-14 rounded-md bg-muted/60" />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── Enrichment signals section ─────────────────────────────────
function EnrichmentSection({ contact }: { contact: Record<string, unknown> }) {
  const [expanded, setExpanded] = useState(false);

  const hasPlaces = contact.places_name || contact.places_rating;
  const hasWeb = contact.web_tech_stack && (contact.web_tech_stack as string[]).length > 0;
  const hasLinkedin = contact.linkedin_profile_data;
  if (!hasPlaces && !hasWeb && !hasLinkedin) return null;

  return (
    <section>
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1 text-xs font-semibold text-muted-foreground uppercase tracking-wider hover:text-foreground transition-colors"
      >
        <Zap size={14} /> Señales (Enrichment)
        {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        <span className="ml-1 normal-case font-normal">
          {[hasPlaces && "Places", hasWeb && "Web", hasLinkedin && "LinkedIn"].filter(Boolean).join(" · ")}
        </span>
      </button>
      {expanded && (
        <div className="mt-2 space-y-3">
          {hasPlaces && (
            <Card className="border-emerald-500/30">
              <CardHeader className="pb-2 pt-3 px-4">
                <CardTitle className="text-xs flex items-center gap-1.5">
                  <MapPin size={13} className="text-emerald-500" /> Google Places
                  <Badge variant="secondary" className="text-[10px] ml-auto">✓ Verificado</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="px-4 pb-3 grid grid-cols-2 gap-2">
                <Field label="Nombre" value={contact.places_name} />
                <Field label="Rating" value={contact.places_rating != null ? `⭐ ${contact.places_rating} (${contact.places_user_ratings_total ?? 0} reviews)` : null} />
                {contact.places_types && (
                  <div className="col-span-2">
                    <div className="text-xs text-muted-foreground mb-1">Tipos de negocio</div>
                    <div className="flex flex-wrap gap-1">
                      {(contact.places_types as string[]).map((t, i) => (
                        <Badge key={i} variant="secondary" className="text-xs">{t}</Badge>
                      ))}
                    </div>
                  </div>
                )}
                <Field label="Web" value={contact.places_website} />
                <Field label="Teléfono" value={contact.places_phone} />
                <div className="col-span-2"><Field label="Dirección" value={contact.places_address} /></div>
                <Field label="Última verificación" value={formatDate(contact.places_last_checked_at)} />
              </CardContent>
            </Card>
          )}
          {hasWeb && (
            <Card>
              <CardHeader className="pb-2 pt-3 px-4">
                <CardTitle className="text-xs flex items-center gap-1.5">
                  <Globe size={13} /> Web Tech Stack
                </CardTitle>
              </CardHeader>
              <CardContent className="px-4 pb-3">
                <div className="flex flex-wrap gap-1">
                  {(contact.web_tech_stack as string[]).map((t, i) => (
                    <Badge key={i} variant="outline" className="text-xs">{t}</Badge>
                  ))}
                </div>
                <div className="mt-2"><Field label="Último scraping" value={formatDate(contact.web_last_scraped_at)} /></div>
              </CardContent>
            </Card>
          )}
          {hasLinkedin && (
            <Card>
              <CardHeader className="pb-2 pt-3 px-4">
                <CardTitle className="text-xs flex items-center gap-1.5">
                  <Linkedin size={13} /> LinkedIn Profile
                </CardTitle>
              </CardHeader>
              <CardContent className="px-4 pb-3">
                <pre className="text-xs bg-muted/30 rounded-md p-2 overflow-x-auto max-h-40">
                  {typeof contact.linkedin_profile_data === "object"
                    ? JSON.stringify(contact.linkedin_profile_data, null, 2)
                    : String(contact.linkedin_profile_data)}
                </pre>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </section>
  );
}

// ─── History item ───────────────────────────────────────────────
function HistoryItem({ item }: { item: Record<string, unknown> }) {
  let parsedNotes: string | null = null;
  if (item.notes) {
    try {
      const obj = typeof item.notes === "string" ? JSON.parse(String(item.notes)) : item.notes;
      if (obj.event && obj.diff) {
        const diffs = Object.entries(obj.diff as Record<string, { before: unknown; after: unknown }>)
          .map(([k, v]) => `${k}: ${v.before ?? "∅"} → ${v.after ?? "∅"}`)
          .join(", ");
        parsedNotes = `${obj.event} — ${diffs}`;
      } else {
        parsedNotes = JSON.stringify(obj, null, 2);
      }
    } catch {
      parsedNotes = String(item.notes);
    }
  }

  return (
    <div className="flex items-start gap-3 text-sm border-l-2 border-primary/30 pl-3 py-1.5">
      <Clock size={14} className="mt-0.5 shrink-0 text-muted-foreground" />
      <div className="min-w-0 flex-1">
        <span className="font-medium">{String(item.subject ?? item.type ?? "")}</span>
        {parsedNotes && (
          <p className="text-xs text-muted-foreground mt-0.5 whitespace-pre-wrap break-all">{parsedNotes}</p>
        )}
        <span className="text-xs text-muted-foreground">{formatDate(item.activity_date || item.created_at)}</span>
      </div>
    </div>
  );
}

// ─── Contact Form Modal (POST idempotent) ───────────────────────
function ContactFormModal({ open, onClose, initialData }: {
  open: boolean;
  onClose: () => void;
  initialData: Record<string, unknown> | null;
}) {
  const isEdit = !!initialData;
  const { toast } = useToast();
  const createContact = useCreateContact();

  const [form, setForm] = useState<Record<string, unknown>>({});

  useEffect(() => {
    if (open) {
      setForm(initialData ? {
        nombre: initialData.nombre ?? "",
        email: initialData.email ?? "",
        telefono: initialData.telefono ?? "",
        company_name: initialData.company_name ?? "",
        cargo: initialData.cargo ?? "",
        tipo_empresa: initialData.tipo_empresa ?? "",
        company_size: initialData.company_size ?? "",
        industry: initialData.industry ?? "",
        website: initialData.website ?? "",
        linkedin_url: initialData.linkedin_url ?? "",
        ciudad: initialData.ciudad ?? "",
        pais: initialData.pais ?? "ES",
        direccion: initialData.direccion ?? "",
        origen: initialData.origen ?? "MANUAL",
        estado: initialData.estado ?? "ACTIVO",
        pack_asignado: initialData.pack_asignado ?? "NO_ASIGNADO",
        gdpr_consent: initialData.gdpr_consent ?? false,
        marketing_consent: initialData.marketing_consent ?? false,
        notas: initialData.notas ?? "",
      } : {
        nombre: "", email: "", telefono: "", company_name: "", cargo: "",
        tipo_empresa: "", company_size: "", industry: "", website: "", linkedin_url: "",
        ciudad: "", pais: "ES", direccion: "",
        origen: "MANUAL", estado: "ACTIVO", pack_asignado: "NO_ASIGNADO",
        gdpr_consent: false, marketing_consent: false, notas: "",
      });
    }
  }, [open, initialData]);

  const set = (k: string, v: unknown) => setForm((prev) => ({ ...prev, [k]: v }));

  const handleSave = () => {
    if (!form.nombre || !form.email) {
      toast({ title: "Error", description: "Nombre y email son obligatorios.", variant: "destructive" });
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(form.email))) {
      toast({ title: "Error", description: "Email inválido.", variant: "destructive" });
      return;
    }
    if (!form.gdpr_consent) {
      toast({ title: "Error", description: "El consentimiento GDPR es obligatorio para crear un contacto.", variant: "destructive" });
      return;
    }
    // Auto-add https:// to URLs if missing
    const payload = { ...form };
    if (payload.website && !/^https?:\/\//.test(String(payload.website))) {
      payload.website = `https://${payload.website}`;
    }
    if (payload.linkedin_url && !/^https?:\/\//.test(String(payload.linkedin_url))) {
      payload.linkedin_url = `https://${payload.linkedin_url}`;
    }

    createContact.mutate(payload, {
      onSuccess: () => {
        toast({ title: isEdit ? "Contacto actualizado" : "Contacto creado" });
        onClose();
      },
      onError: (err) => {
        const msg = err instanceof Error ? err.message : "Error desconocido";
        toast({
          title: "Error",
          description: msg.includes("constraint") ? "Valor inválido. Usa valores canónicos del sistema." : msg,
          variant: "destructive",
        });
      },
    });
  };

  return (
    <Dialog open={open} onOpenChange={() => onClose()}>
      <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEdit ? "Editar contacto" : "Nuevo contacto"}</DialogTitle>
        </DialogHeader>

        <div className="space-y-5 mt-2">
          {/* Información Personal */}
          <fieldset>
            <legend className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <User size={13} /> Información Personal
            </legend>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <FormField label="Nombre *" value={form.nombre} onChange={(v) => set("nombre", v)} placeholder="Juan Pérez" />
              <FormField label="Email *" value={form.email} onChange={(v) => set("email", v)} disabled={isEdit} placeholder="juan@empresa.com" />
              <FormField label="Teléfono" value={form.telefono} onChange={(v) => set("telefono", v)} placeholder="+34 600 123 456" />
              <FormField label="Cargo" value={form.cargo} onChange={(v) => set("cargo", v)} placeholder="CTO, CEO, Developer..." />
            </div>
          </fieldset>

          {/* Empresa */}
          <fieldset>
            <legend className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <Building2 size={13} /> Información de Empresa
            </legend>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <FormField label="Empresa" value={form.company_name} onChange={(v) => set("company_name", v)} placeholder="Acme Corp" />
              <div>
                <Label className="text-xs">Tipo empresa</Label>
                <Select value={String(form.tipo_empresa ?? "")} onValueChange={(v) => set("tipo_empresa", v)}>
                  <SelectTrigger className="mt-1"><SelectValue placeholder="Seleccionar..." /></SelectTrigger>
                  <SelectContent>
                    {TIPOS_EMPRESA.map((t) => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className="text-xs">Tamaño</Label>
                <Select value={String(form.company_size ?? "")} onValueChange={(v) => set("company_size", v)}>
                  <SelectTrigger className="mt-1"><SelectValue placeholder="Seleccionar..." /></SelectTrigger>
                  <SelectContent>
                    {COMPANY_SIZES.map((s) => <SelectItem key={s} value={s}>{s} empleados</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <FormField label="Industria/Sector" value={form.industry} onChange={(v) => set("industry", v)} placeholder="Technology, Finance..." />
              <FormField label="Sitio web" value={form.website} onChange={(v) => set("website", v)} placeholder="https://acme.com" />
              <FormField label="LinkedIn" value={form.linkedin_url} onChange={(v) => set("linkedin_url", v)} placeholder="https://linkedin.com/in/..." />
            </div>
          </fieldset>

          {/* Ubicación */}
          <fieldset>
            <legend className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <MapPin size={13} /> Ubicación
            </legend>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <FormField label="Ciudad" value={form.ciudad} onChange={(v) => set("ciudad", v)} placeholder="Madrid" />
              <div>
                <Label className="text-xs">País</Label>
                <Select value={String(form.pais ?? "ES")} onValueChange={(v) => set("pais", v)}>
                  <SelectTrigger className="mt-1"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {PAISES.map((p) => <SelectItem key={p.code} value={p.code}>{p.label}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="sm:col-span-2">
                <Label className="text-xs">Dirección</Label>
                <Input className="mt-1" value={String(form.direccion ?? "")} onChange={(e) => set("direccion", e.target.value)} placeholder="Calle Mayor 10, 28013 Madrid" />
              </div>
            </div>
          </fieldset>

          {/* Clasificación CRM */}
          <fieldset>
            <legend className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <Tag size={13} /> Clasificación CRM
            </legend>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <Label className="text-xs">Origen</Label>
                <Select value={String(form.origen ?? "MANUAL")} onValueChange={(v) => set("origen", v)}>
                  <SelectTrigger className="mt-1"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {ORIGENES.map((o) => <SelectItem key={o} value={o}>{o.replace(/_/g, " ")}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className="text-xs">Estado</Label>
                <Select value={String(form.estado ?? "ACTIVO")} onValueChange={(v) => set("estado", v)}>
                  <SelectTrigger className="mt-1"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {ESTADOS.map((e) => <SelectItem key={e} value={e}>{e}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className="text-xs">Pack</Label>
                <Select value={String(form.pack_asignado ?? "NO_ASIGNADO")} onValueChange={(v) => set("pack_asignado", v)}>
                  <SelectTrigger className="mt-1"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {PACKS.map((p) => <SelectItem key={p} value={p}>{p}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </fieldset>

          {/* GDPR */}
          <fieldset>
            <legend className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <Shield size={13} /> Consentimientos GDPR
            </legend>
            <div className="flex flex-col gap-3">
              <div className="flex items-center gap-2">
                <Checkbox
                  checked={!!form.gdpr_consent}
                  onCheckedChange={(v) => set("gdpr_consent", !!v)}
                />
                <Label className="text-sm">Acepto el tratamiento de datos (GDPR) <span className="text-destructive">*</span></Label>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  checked={!!form.marketing_consent}
                  onCheckedChange={(v) => set("marketing_consent", !!v)}
                />
                <Label className="text-sm">Acepto recibir comunicaciones de marketing</Label>
              </div>
            </div>
          </fieldset>

          {/* Notas */}
          <fieldset>
            <legend className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <FileText size={13} /> Notas Internas
            </legend>
            <Textarea
              value={String(form.notas ?? "")}
              onChange={(e) => set("notas", e.target.value)}
              placeholder="Notas internas sobre el contacto..."
              rows={3}
            />
          </fieldset>
        </div>

        <div className="flex justify-end gap-2 mt-4">
          <Button variant="outline" onClick={onClose}>Cancelar</Button>
          <Button onClick={handleSave} disabled={createContact.isPending}>
            {createContact.isPending && <Loader2 className="h-4 w-4 animate-spin mr-1" />}
            {isEdit ? "Guardar" : "Crear"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

// ─── Shared UI components ───────────────────────────────────────
function Field({ label, value, icon }: { label: string; value: unknown; icon?: React.ReactNode }) {
  const v = value != null && value !== "" ? String(value) : "—";
  return (
    <div className="rounded-md border bg-muted/20 px-3 py-2">
      <div className="flex items-center gap-1 text-xs text-muted-foreground mb-0.5">{icon} {label}</div>
      <div className="text-sm font-medium break-all">{v}</div>
    </div>
  );
}

function SectionTitle({ title, icon }: { title: string; icon?: React.ReactNode }) {
  return (
    <h4 className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
      {icon} {title}
    </h4>
  );
}

function FormField({ label, value, onChange, disabled, placeholder }: {
  label: string; value: unknown; onChange: (v: string) => void; disabled?: boolean; placeholder?: string;
}) {
  return (
    <div>
      <Label className="text-xs">{label}</Label>
      <Input
        className="mt-1"
        value={String(value ?? "")}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder={placeholder}
      />
    </div>
  );
}

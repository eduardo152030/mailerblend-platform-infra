import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { PACK_COLORS } from "@/lib/linkedin-mock-data";
import { Send, UserCheck, MessageSquare, CalendarCheck, TrendingUp, Users, Zap, Info, Bell, Check, X, Bot } from "lucide-react";
import { useLSSDashboard, useLSSOutcomes, useLSSLeads, useLSSApproveApproval, useLSSRejectApproval, useLSSRateLimitStatus } from "@/hooks/use-api";
import { toast } from "@/hooks/use-toast";
import { useState } from "react";
import LSSLeadDetail from "./LSSLeadDetail";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

const KPI_TOOLTIPS: Record<string, { icon: string; title: string; desc: string; sections: { label: string; text: string }[] }> = {
  "Total Leads": {
    icon: "👥", title: "TOTAL DE LEADS",
    desc: "Total de leads en el sistema LinkedIn Sourcing (todos los estados).",
    sections: [
      { label: "📊 Incluye", text: "Nuevos, En proceso, Aceptados, Convertidos, Archivados" },
      { label: "💡 Nota", text: "Es el volumen total del pipeline. No todos son leads activos." },
      { label: "🎯 Objetivo", text: "Crecimiento sostenido sin comprometer calidad (score promedio > 60)" },
    ],
  },
  "Invites Enviadas": {
    icon: "✉️", title: "INVITACIONES ENVIADAS",
    desc: "Total de invitaciones LinkedIn enviadas en los últimos 30 días.",
    sections: [
      { label: "📊 Estados incluidos", text: "INVITE_SENT, PENDING, ACCEPTED, NO_ACCEPT" },
      { label: "⚠️ Límite diario", text: "15-25 invites/día para evitar restricciones de LinkedIn" },
      { label: "🎯 Objetivo", text: "Consistencia diaria (no enviar todo el mismo día)" },
    ],
  },
  "Acceptance Rate": {
    icon: "✅", title: "TASA DE ACEPTACIÓN",
    desc: "% de leads que aceptaron la invitación vs. total enviados.",
    sections: [
      { label: "📊 Fórmula", text: "(Aceptados / Invites Enviados) × 100" },
      { label: "🎯 Benchmarks", text: "🔴 < 15% → Revisar ICP\n🟡 15-25% → Aceptable\n🟢 25-40% → Bueno\n💎 > 40% → Excelente" },
      { label: "⚠️ Stop-loss", text: "Si < 5% durante 3 días → Pausar y revisar" },
    ],
  },
  "Conversaciones": {
    icon: "💬", title: "CONVERSACIONES ACTIVAS",
    desc: "Leads con intercambio de mensajes activo actualmente.",
    sections: [
      { label: "📊 Criterio", text: "Status ACCEPTED + tiene mensajes con último mensaje < 7 días" },
      { label: "🎯 Objetivo", text: "Mantener conversaciones fluidas hacia agendamiento de call" },
      { label: "📈 Funnel típico", text: "Conversaciones → Booked: 30-50%" },
    ],
  },
  "Booked Calls": {
    icon: "📅", title: "CALLS AGENDADAS",
    desc: "Leads que agendaron sesión de diagnóstico en Cal.com.",
    sections: [
      { label: "🎯 Momento clave", text: "Lead mostró interés real, timing confirmado" },
      { label: "💡 Preparación", text: "1. Revisar conversación\n2. Identificar pain points\n3. Tener claro pack ideal\n4. Investigar empresa" },
      { label: "📈 Conversión típica", text: "Booked → Oportunidad: 40-60%" },
    ],
  },
  "Convertidos": {
    icon: "⚡", title: "LEADS CONVERTIDOS",
    desc: "Leads que se convirtieron en Oportunidades en el CRM.",
    sections: [
      { label: "🎯 North Star", text: "Este es el objetivo final del sistema" },
      { label: "💰 Valor típico", text: "GUARDIAN: 500-800 €/mes\nMOTOR: 1,100-1,600 €/mes\nFORTALEZA: 1,700-2,500+ €/mes" },
      { label: "📈 Objetivo mensual", text: "2-5 conversiones/mes con prospección quality-first" },
    ],
  },
};

export default function LSSDashboard() {
  const { data, isLoading, isError } = useLSSDashboard({ days: 30 });
  const { data: rateLimitData } = useLSSRateLimitStatus();
  const [bookedOpen, setBookedOpen] = useState(false);
  const [conversacionesOpen, setConversacionesOpen] = useState(false);
  const [convertidosOpen, setConvertidosOpen] = useState(false);
  const [approvalsOpen, setApprovalsOpen] = useState(false);
  const [selectedLead, setSelectedLead] = useState<Record<string, any> | null>(null);
  const [approveTarget, setApproveTarget] = useState<Record<string, any> | null>(null);
  const [finalMessage, setFinalMessage] = useState("");

  const { data: bookedData, isLoading: bookedLoading } = useLSSOutcomes(
    { outcome: "BOOKED", limit: 50 }
  );
  const bookedOutcomes = (bookedData as any)?.items ?? [];

  // FIX 1: Use active_conversations_list from dashboard instead of fetching by status
  const convLeads = (d => d?.active_conversations_list ?? [])(data as any);

  const { data: convertedLeadsData, isLoading: convertedLoading } = useLSSLeads(
    convertidosOpen ? { status: "CONVERTED", limit: 50 } : { limit: 1 }
  );
  const convertedLeads = convertidosOpen ? ((convertedLeadsData as any)?.items ?? []) : [];

  // "Por Pack" usa by_pack del dashboard endpoint

  const approveMut = useLSSApproveApproval();
  const rejectMut = useLSSRejectApproval();

  const handleBookedClick = () => setBookedOpen(true);
  const handleConversacionesClick = () => setConversacionesOpen(true);
  const handleConvertidosClick = () => setConvertidosOpen(true);

  const handleSelectLead = (lead: Record<string, any>, closeDialog: () => void) => {
    closeDialog();
    setSelectedLead(lead);
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i}><CardContent className="pt-5 pb-4 px-5"><Skeleton className="h-14 w-full" /></CardContent></Card>
          ))}
        </div>
      </div>
    );
  }

  if (isError || !data) {
    return <p className="text-sm text-destructive">Error cargando dashboard LSS</p>;
  }

  const d = data as Record<string, any>;
  const statusCounts = (d.by_status ?? {}) as Record<string, number>;

  // Use by_status counts as fallback since some API fields may return 0
  const convertedCount = statusCounts["CONVERTED"] ?? d.converted_opportunities ?? 0;
  const conversacionesCount = d.active_conversations ?? 0;

  const kpiCards = [
    { label: "Total Leads", value: d.total_leads ?? 0, icon: Users, color: "text-blue-500", clickable: false },
    { label: "Invites Enviadas", value: d.invites_sent ?? 0, icon: Send, color: "text-blue-500", clickable: false },
    {
      label: "Acceptance Rate",
      value: `${d.acceptances ?? 0}`,
      icon: UserCheck,
      color: "text-emerald-500",
      suffix: d.acceptance_rate != null ? ` (${Math.round(d.acceptance_rate)}%)` : "",
      clickable: false,
    },
    {
      label: "Conversaciones",
      value: conversacionesCount,
      icon: MessageSquare,
      color: "text-purple-500",
      clickable: true,
      onClick: handleConversacionesClick,
    },
    {
      label: "Booked Calls",
      value: d.booked_calls ?? 0,
      icon: CalendarCheck,
      color: "text-primary",
      clickable: true,
      onClick: handleBookedClick,
    },
    {
      label: "Convertidos",
      value: convertedCount,
      icon: Zap,
      color: "text-amber-500",
      clickable: true,
      onClick: handleConvertidosClick,
    },
  ];

  const byPackFromDashboard = (d.by_pack ?? {}) as Record<string, number>;

  // Siempre mostrar los 3 packs principales aunque tengan 0 leads
  const ALL_PACKS = ["GUARDIAN", "MOTOR", "FORTALEZA"] as const;
  const byPack: Record<string, number> = {};
  for (const pack of ALL_PACKS) {
    byPack[pack] = byPackFromDashboard[pack] ?? 0;
  }
  // Agregar cualquier otro pack no estándar que exista en los datos
  for (const [pack, count] of Object.entries(byPackFromDashboard)) {
    if (!byPack[pack]) byPack[pack] = count;
  }
  const byStatus = (d.by_status ?? {}) as Record<string, number>;
  const segPerf = (d.segments_performance ?? {}) as Record<string, { invites: number; accepts: number; acceptance_rate: number }>;

  return (
    <div className="space-y-6">
      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {kpiCards.map((k) => (
          <Card
            key={k.label}
            className={k.clickable && (k.value as number) > 0 ? "cursor-pointer hover:ring-1 hover:ring-primary/40 transition-all" : ""}
            onClick={k.clickable && (k.value as number) > 0 ? k.onClick : undefined}
          >
            <CardContent className="pt-5 pb-4 px-5 relative">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-muted-foreground">{k.label}</span>
                <div className="flex items-center gap-1.5">
                  {KPI_TOOLTIPS[k.label] && (
                    <TooltipProvider delayDuration={200}>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Info size={13} className="text-muted-foreground/60 hover:text-primary cursor-help transition-colors" />
                        </TooltipTrigger>
                        <TooltipContent side="bottom" align="end" className="max-w-xs p-3 space-y-2">
                          <p className="font-bold text-sm">{KPI_TOOLTIPS[k.label].icon} {KPI_TOOLTIPS[k.label].title}</p>
                          <p className="text-xs text-muted-foreground">{KPI_TOOLTIPS[k.label].desc}</p>
                          {KPI_TOOLTIPS[k.label].sections.map((s, i) => (
                            <div key={i}>
                              <p className="text-xs font-semibold">{s.label}</p>
                              <p className="text-xs text-muted-foreground whitespace-pre-line">{s.text}</p>
                            </div>
                          ))}
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  )}
                  <k.icon size={16} className={k.color} />
                </div>
              </div>
              <p className="text-2xl font-bold">
                {k.value}
                {k.suffix && <span className="text-sm font-normal text-muted-foreground">{k.suffix}</span>}
              </p>
              {k.clickable && (k.value as number) > 0 && (
                <p className="text-[10px] text-primary mt-1">Click para ver →</p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Rate limit indicators + 7d mini stats */}
      {(() => {
        const rl = rateLimitData as any;
        return (
          <Card>
            <CardContent className="pt-4 pb-3 px-5 space-y-2">
              {rl && (
                <div className="flex flex-wrap gap-4 sm:gap-6 text-sm mb-1">
                  <span className={rl.invites?.can_send ? "" : "text-destructive font-semibold"}>
                    📤 Invites: {rl.invites?.sent_today ?? 0}/{rl.invites?.cap ?? 0}
                  </span>
                  <span className={rl.messages?.can_send ? "" : "text-destructive font-semibold"}>
                    💬 Msgs: {rl.messages?.sent_today ?? 0}/{rl.messages?.cap ?? 0}
                  </span>
                  {rl.cooldown_active && (
                    <span className="text-destructive font-semibold animate-pulse">⏸️ COOLDOWN</span>
                  )}
                </div>
              )}
              {(d.new_leads_7d != null || d.accepted_7d != null || d.booked_7d != null) && (
                <>
                  <p className="text-xs font-medium text-muted-foreground mb-1">Últimos 7 días</p>
                  <div className="flex flex-wrap gap-4 sm:gap-6 text-sm">
                    <span>📥 {d.new_leads_7d ?? 0} nuevos</span>
                    <span>✅ {d.accepted_7d ?? 0} aceptados</span>
                    <span>📅 {d.booked_7d ?? 0} booked</span>
                    <span
                      className={`cursor-pointer transition-colors ${(d.pending_approvals ?? 0) > 0 ? "text-amber-500 font-semibold animate-pulse" : ""}`}
                      onClick={() => (d.pending_approvals ?? 0) > 0 && setApprovalsOpen(true)}
                    >
                      🔔 {d.pending_approvals ?? 0} pend. aprobación
                    </span>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        );
      })()}

      <div className="grid lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingUp size={16} /> Por Pack
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {Object.entries(byPack).map(([pack, count]) => {
              const p = PACK_COLORS[pack] || PACK_COLORS.NONE;
              return (
                <div key={pack} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                  <div className="flex items-center gap-2">
                    <span>{p.emoji}</span>
                    <span className={`text-sm font-medium ${p.text}`}>{p.label}</span>
                  </div>
                  <span className="text-sm font-medium">{count} leads</span>
                </div>
              );
            })}
            {Object.keys(byPack).length === 0 && (
              <p className="text-xs text-muted-foreground">Sin datos</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              📊 Por Status
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {Object.entries(byStatus).map(([status, count]) => (
              <div key={status} className="flex items-center justify-between p-2 rounded bg-muted/50">
                <Badge variant="outline" className="text-[10px]">{status}</Badge>
                <span className="text-sm font-medium">{count as number}</span>
              </div>
            ))}
            {Object.keys(byStatus).length === 0 && (
              <p className="text-xs text-muted-foreground">Sin datos</p>
            )}
          </CardContent>
        </Card>
      </div>

      {Object.keys(segPerf).length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              🎯 Segmentos A/B
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {Object.entries(segPerf).map(([seg, stats]) => (
              <div key={seg} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                <Badge variant="outline" className="text-xs">{seg}</Badge>
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  <span>{stats.invites} invites</span>
                  <span>•</span>
                  <span>{stats.accepts} aceptados</span>
                  <span>•</span>
                  <span className="font-semibold text-primary">{Math.round(stats.acceptance_rate)}%</span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Booked leads picker dialog */}
      <Dialog open={bookedOpen} onOpenChange={setBookedOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="text-base">📅 Leads con Booked Calls</DialogTitle>
          </DialogHeader>
          {bookedLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-14 w-full" />)}
            </div>
          ) : bookedOutcomes.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4 text-center">No hay leads con booked calls.</p>
          ) : (
            <ScrollArea className="max-h-[50vh]">
              <div className="space-y-2">
                {bookedOutcomes.map((oc: any) => {
                  const packColor = PACK_COLORS[oc.lead_pack_candidate] || PACK_COLORS.NONE;
                  return (
                    <Card
                      key={oc.id}
                      className="cursor-pointer hover:ring-1 hover:ring-primary/30 transition-all"
                      onClick={() => handleSelectLead({ ...oc, id: oc.linkedin_lead_id, full_name: oc.lead_full_name || "Lead" }, () => setBookedOpen(false))}
                    >
                      <CardContent className="p-3">
                        <p className="text-sm font-medium">{oc.lead_full_name || "Lead"}</p>
                        <p className="text-xs text-muted-foreground">{oc.lead_title} @ {oc.lead_company}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="outline" className={`text-[10px] ${packColor.text}`}>{packColor.emoji} {packColor.label}</Badge>
                          <span className="text-xs text-muted-foreground">Score: {oc.lead_score}</span>
                        </div>
                        {oc.outcome_notes && <p className="text-xs text-muted-foreground mt-1">📝 {oc.outcome_notes}</p>}
                        {oc.scheduled_at && (
                          <p className="text-xs text-primary mt-1">📅 Call: {new Date(oc.scheduled_at).toLocaleDateString("es-ES")}</p>
                        )}
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </ScrollArea>
          )}
        </DialogContent>
      </Dialog>

      {/* Conversaciones leads picker dialog */}
      <Dialog open={conversacionesOpen} onOpenChange={setConversacionesOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="text-base">💬 Leads en Conversación</DialogTitle>
          </DialogHeader>
          {convLeads.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4 text-center">No hay leads en conversación activa.</p>
          ) : (
            <ScrollArea className="max-h-[50vh]">
              <div className="space-y-2">
                {convLeads.map((lead: any) => (
                  <Card
                    key={lead.lead_id || lead.id}
                    className="cursor-pointer hover:ring-1 hover:ring-primary/30 transition-all"
                    onClick={() => handleSelectLead({ ...lead, id: lead.lead_id || lead.id }, () => setConversacionesOpen(false))}
                  >
                    <CardContent className="p-3">
                      <p className="text-sm font-medium">{lead.full_name}</p>
                      <p className="text-xs text-muted-foreground">{lead.title} @ {lead.company}</p>
                      {lead.last_message_at && (
                        <p className="text-xs text-muted-foreground mt-1">💬 Último msg: {new Date(lead.last_message_at).toLocaleDateString("es-ES")}</p>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          )}
        </DialogContent>
      </Dialog>

      {/* Convertidos leads picker dialog */}
      <Dialog open={convertidosOpen} onOpenChange={setConvertidosOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="text-base">⚡ Leads Convertidos</DialogTitle>
          </DialogHeader>
          {convertedLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-14 w-full" />)}
            </div>
          ) : convertedLeads.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4 text-center">No hay leads convertidos.</p>
          ) : (
            <ScrollArea className="max-h-[50vh]">
              <div className="space-y-2">
                {convertedLeads.map((lead: any) => (
                  <Card
                    key={lead.id}
                    className="cursor-pointer hover:ring-1 hover:ring-primary/30 transition-all"
                    onClick={() => handleSelectLead(lead, () => setConvertidosOpen(false))}
                  >
                    <CardContent className="p-3">
                      <p className="text-sm font-medium">{lead.full_name}</p>
                      <p className="text-xs text-muted-foreground">{lead.title} @ {lead.company}</p>
                      <p className="text-xs text-muted-foreground mt-1">Score: {lead.lead_score}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          )}
        </DialogContent>
      </Dialog>

      {/* Pending Approvals modal */}
      <Dialog open={approvalsOpen} onOpenChange={setApprovalsOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-base">🔔 Drafts Pendientes de Aprobación</DialogTitle>
          </DialogHeader>
          {(() => {
            const pendingList = (d.pending_approvals_list ?? []) as any[];
            if (pendingList.length === 0) {
              return <p className="text-sm text-muted-foreground py-4 text-center">No hay drafts pendientes.</p>;
            }
            return (
              <ScrollArea className="max-h-[60vh]">
                <div className="space-y-3">
                  {pendingList.map((ap: any) => {
                    const packColor = PACK_COLORS[ap.lead_pack_candidate] || PACK_COLORS.NONE;
                    return (
                      <Card key={ap.approval_id}>
                        <CardContent className="p-4 space-y-3">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm font-medium">{ap.lead_full_name}</p>
                              <p className="text-xs text-muted-foreground">{ap.lead_title} @ {ap.lead_company}</p>
                            </div>
                            <div className="flex items-center gap-2">
                              <Badge variant="outline" className={`text-[10px] ${packColor.text}`}>{packColor.emoji} {packColor.label}</Badge>
                              <span className="text-xs text-muted-foreground">Score: {ap.lead_score}</span>
                            </div>
                          </div>
                          <div className="bg-muted/50 rounded-lg p-3">
                            <p className="text-sm italic">"{ap.draft_message}"</p>
                          </div>
                          {ap.ai_rationale && (
                            <div className="flex items-start gap-2 text-xs text-muted-foreground">
                              <Bot size={14} className="shrink-0 mt-0.5" />
                              <p>{ap.ai_rationale}</p>
                            </div>
                          )}
                          <div className="flex gap-2">
                            <Button size="sm" variant="outline" onClick={() => {
                              setApprovalsOpen(false);
                              setSelectedLead({ id: ap.linkedin_lead_id, full_name: ap.lead_full_name });
                            }}>
                              Ver lead →
                            </Button>
                            <Button size="sm" onClick={() => {
                              setApproveTarget(ap);
                              setFinalMessage(ap.draft_message || "");
                            }}>
                              <Check size={14} className="mr-1" /> Aprobar
                            </Button>
                            <Button size="sm" variant="outline" className="text-destructive" onClick={() => {
                              rejectMut.mutate(
                                { id: ap.approval_id, data: { human_note: "Rechazado desde dashboard" } },
                                {
                                  onSuccess: () => toast({ title: "❌ Draft rechazado" }),
                                  onError: () => toast({ title: "Error al rechazar", variant: "destructive" }),
                                }
                              );
                            }}>
                              <X size={14} className="mr-1" /> Rechazar
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              </ScrollArea>
            );
          })()}
        </DialogContent>
      </Dialog>

      {/* Quick Approve dialog */}
      <Dialog open={!!approveTarget} onOpenChange={() => setApproveTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Aprobar Draft</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-xs font-medium text-muted-foreground">Mensaje final</label>
              <Textarea value={finalMessage} onChange={(e) => setFinalMessage(e.target.value)} rows={4} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setApproveTarget(null)}>Cancelar</Button>
            <Button onClick={() => {
              if (!approveTarget) return;
              approveMut.mutate(
                { id: approveTarget.approval_id || approveTarget.id, data: { final_message: finalMessage } },
                {
                  onSuccess: () => {
                    toast({ title: "✅ Mensaje aprobado y enviado" });
                    setApproveTarget(null);
                  },
                  onError: () => toast({ title: "Error al aprobar", variant: "destructive" }),
                }
              );
            }} disabled={approveMut.isPending}>
              <Check size={14} className="mr-1" /> Aprobar y Enviar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Lead detail sheet */}
      {selectedLead && (
        <LSSLeadDetail lead={selectedLead} onClose={() => setSelectedLead(null)} />
      )}
    </div>
  );
}

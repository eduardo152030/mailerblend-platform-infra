import { useState, useRef, useCallback } from "react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { PACK_COLORS, STATUS_COLORS, KANBAN_COLUMNS, PIPELINE_STATUS_MAP } from "@/lib/linkedin-mock-data";
import { Star, Upload, Info } from "lucide-react";
import LSSLeadDetail from "./LSSLeadDetail";
import LSSImportModal from "./LSSImportModal";
import { useLSSLeads, useLSSOutcomes } from "@/hooks/use-api";

const COLUMN_TOOLTIPS: Record<string, { icon: string; title: string; desc: string; sections: { label: string; text: string }[] }> = {
  NEW: {
    icon: "📥", title: "NUEVOS",
    desc: "Lead recién importado o identificado.",
    sections: [
      { label: "➡️ Próximo paso", text: "Auto-clasificación de Pack y scoring" },
      { label: "⏱️ Tiempo típico", text: "0-1 día" },
    ],
  },
  INVITE_QUEUED: {
    icon: "⏳", title: "EN COLA",
    desc: "Lead calificado esperando envío de invitación LinkedIn.",
    sections: [
      { label: "✅ Requisitos", text: "• Pack asignado\n• Score ≥ 50\n• No es duplicado" },
      { label: "➡️ Próximo paso", text: "Enviar invitación LinkedIn" },
      { label: "⏱️ Tiempo típico", text: "1-2 días (depende del cupo diario)" },
    ],
  },
  INVITE_SENT: {
    icon: "📤", title: "INVITACIÓN ENVIADA",
    desc: "Invitación LinkedIn enviada. Esperando aceptación del lead.",
    sections: [
      { label: "⏱️ Ventana de espera", text: "7-14 días" },
      { label: "➡️ Posibles outcomes", text: "✅ Acepta → Aceptados\n❌ No acepta → Reciclaje o archive" },
      { label: "🔄 Reintento", text: "Si no acepta y hay señal nueva, se puede reintentar" },
    ],
  },
  ACCEPTED: {
    icon: "✅", title: "ACEPTADOS",
    desc: "Lead aceptó la invitación. Conexión establecida.",
    sections: [
      { label: "➡️ Próximo paso", text: "1. Research profundo (web + Places)\n2. IA genera draft de mensaje\n3. Aprobación humana vía Telegram\n4. Inicio de conversación" },
      { label: "⭐ Momento crítico", text: "Primera impresión cuenta" },
    ],
  },
  IN_CONVERSATION: {
    icon: "💬", title: "EN CONVERSACIÓN",
    desc: "Conversación activa con el lead.",
    sections: [
      { label: "📊 Objetivos", text: "1. Validar interés real\n2. Identificar dolor/timing\n3. Agendar sesión diagnóstico (Cal.com)" },
      { label: "⚠️ Reglas", text: "• Mensajes naturales, fragmentados\n• No CTA directo en primer mensaje\n• Micro-validación antes de Cal.com" },
    ],
  },
  BOOKED: {
    icon: "📅", title: "CALL AGENDADA",
    desc: "Lead agendó sesión de diagnóstico.",
    sections: [
      { label: "✅ Próximos pasos", text: "1. Prepararse para la call\n2. Revisar conversación completa\n3. Identificar pain points clave\n4. Después de call → crear oportunidad" },
      { label: "🎯 Tasa conversión típica", text: "Call → Oportunidad: 40-60%" },
    ],
  },
  CONVERTED: {
    icon: "⚡", title: "CONVERTIDOS",
    desc: "Lead convertido en Oportunidad en CRM.",
    sections: [
      { label: "✅ Logros", text: "• Sesión diagnóstico completada\n• Fit confirmado\n• Oportunidad creada\n• Pipeline comercial iniciado" },
      { label: "🎯 Nota", text: "Este es el North Star del sistema" },
    ],
  },
  ARCHIVED: {
    icon: "📦", title: "ARCHIVADOS",
    desc: "Leads descartados o no prioritarios.",
    sections: [
      { label: "🔍 Razones comunes", text: "• No aceptó invitación (sin señales nuevas)\n• No es fit después de conversación\n• Ghosteó (dejó de responder)\n• Pack incorrecto" },
      { label: "💡 Nota", text: "Pueden ser revisados si aparecen señales nuevas" },
    ],
  },
};

function ScoreStars({ score }: { score: number }) {
  const stars = score >= 80 ? 3 : score >= 60 ? 2 : 1;
  return (
    <span className="flex items-center gap-0.5 shrink-0">
      <span className="text-xs font-bold">{score}</span>
      {Array.from({ length: stars }).map((_, i) => (
        <Star key={i} size={10} className="fill-yellow-400 text-yellow-400" />
      ))}
    </span>
  );
}

function LeadCard({ lead, onClick, isFocused, onFocus }: { lead: Record<string, any>; onClick: () => void; isFocused?: boolean; onFocus?: () => void }) {
  const pack = PACK_COLORS[lead.pack_candidate] || PACK_COLORS.NONE;
  const ref = useRef<HTMLDivElement>(null);

  if (isFocused && ref.current) {
    ref.current.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onFocus?.();
  };

  const handleDoubleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onClick();
  };

  return (
    <Card
      ref={ref}
      tabIndex={0}
      className={`p-3 cursor-pointer hover:ring-1 hover:ring-primary/30 transition-all overflow-hidden outline-none ${isFocused ? "ring-2 ring-primary shadow-md" : ""}`}
      onClick={handleClick}
      onDoubleClick={handleDoubleClick}
      onFocus={onFocus}
    >
      <p className="text-sm font-medium truncate" title={lead.full_name}>{lead.full_name}</p>
      <p className="text-xs text-muted-foreground truncate" title={`${lead.title} @ ${lead.company}`}>{lead.title} @ {lead.company}</p>
      <div className="flex items-center justify-between mt-2 gap-1 overflow-hidden">
        <Badge className={`text-[10px] px-1.5 py-0 shrink-0 whitespace-nowrap ${pack.bg} ${pack.text} border-0`}>
          {pack.emoji} {pack.label}
        </Badge>
        <ScoreStars score={lead.lead_score ?? 0} />
      </div>
    </Card>
  );
}

export default function LSSLeadsPipeline() {
  const [selectedLead, setSelectedLead] = useState<Record<string, any> | null>(null);
  const [importOpen, setImportOpen] = useState(false);
  const [focusedCard, setFocusedCard] = useState<{ col: string; idx: number } | null>(null);

  const handleColumnKeyDown = useCallback((e: React.KeyboardEvent, colKey: string, leads: any[]) => {
    if (!["ArrowDown", "ArrowUp", "Enter"].includes(e.key)) return;
    e.preventDefault();

    const currentIdx = focusedCard?.col === colKey ? focusedCard.idx : -1;

    if (e.key === "ArrowDown") {
      const next = Math.min(currentIdx + 1, leads.length - 1);
      setFocusedCard({ col: colKey, idx: next });
    } else if (e.key === "ArrowUp") {
      const prev = Math.max(currentIdx - 1, 0);
      setFocusedCard({ col: colKey, idx: prev });
    } else if (e.key === "Enter" && currentIdx >= 0 && currentIdx < leads.length) {
      setSelectedLead(leads[currentIdx]);
    }
  }, [focusedCard]);
  const { data, isLoading } = useLSSLeads({ limit: 200 });
  const { data: bookedData } = useLSSOutcomes({ outcome: "BOOKED", limit: 50 });

  const allLeads = (data as any)?.items ?? [];
  const bookedOutcomes = (bookedData as any)?.items ?? [];

  // Build leads per column using real DB status mapping
  const getColumnLeads = (colKey: string) => {
    if (colKey === "BOOKED") {
      // BOOKED is an outcome, not a status - convert outcomes to lead-like objects
      return bookedOutcomes.map((oc: any) => ({
        id: oc.linkedin_lead_id,
        full_name: oc.lead_full_name || "Lead",
        title: oc.lead_title,
        company: oc.lead_company,
        pack_candidate: oc.lead_pack_candidate,
        lead_score: oc.lead_score,
        status: "BOOKED",
      }));
    }
    const statuses = PIPELINE_STATUS_MAP[colKey] || [];
    let leads = allLeads.filter((l: any) => statuses.includes(l.status));
    if (colKey === "ACCEPTED") {
      leads = leads.filter((l: any) => (l.total_attempts ?? 0) < 1);
    } else if (colKey === "IN_CONVERSATION") {
      leads = leads.filter((l: any) => (l.total_attempts ?? 0) >= 1);
    }
    return leads;
  };

  return (
    <>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-muted-foreground">Pipeline de Leads</h3>
        <Button size="sm" variant="outline" onClick={() => setImportOpen(true)}>
          <Upload size={14} className="mr-1" /> Importar leads
        </Button>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-3">
          {Array.from({ length: 7 }).map((_, i) => (
            <div key={i}>
              <Skeleton className="h-8 w-24 mb-3" />
              <Skeleton className="h-32 w-full" />
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-7 2xl:grid-cols-8 gap-3">
          {KANBAN_COLUMNS.map((col) => {
            const leads = getColumnLeads(col.key);
            return (
              <div key={col.key}>
                <div className="flex items-center gap-2 mb-3 px-1">
                  <Badge variant="outline" className={`text-[10px] ${STATUS_COLORS[col.key] || ""}`}>
                    {col.label}
                  </Badge>
                  <span className="text-xs text-muted-foreground">{leads.length}</span>
                  {COLUMN_TOOLTIPS[col.key] && (
                    <TooltipProvider delayDuration={200}>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Info size={13} className="text-muted-foreground/60 hover:text-primary cursor-help transition-colors" />
                        </TooltipTrigger>
                        <TooltipContent side="bottom" align="start" className="max-w-xs p-3 space-y-2">
                          <p className="font-bold text-sm">{COLUMN_TOOLTIPS[col.key].icon} {COLUMN_TOOLTIPS[col.key].title}</p>
                          <p className="text-xs text-muted-foreground">{COLUMN_TOOLTIPS[col.key].desc}</p>
                          {COLUMN_TOOLTIPS[col.key].sections.map((s, i) => (
                            <div key={i}>
                              <p className="text-xs font-semibold">{s.label}</p>
                              <p className="text-xs text-muted-foreground whitespace-pre-line">{s.text}</p>
                            </div>
                          ))}
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  )}
                </div>
                <div
                  className="max-h-[60vh] overflow-y-auto outline-none"
                  tabIndex={0}
                  onKeyDown={(e) => handleColumnKeyDown(e, col.key, leads)}
                >
                  <div className="space-y-2 min-h-[80px] p-1 rounded-lg bg-muted/30">
                    {leads.map((lead: any, idx: number) => (
                      <LeadCard
                        key={lead.id}
                        lead={lead}
                        isFocused={focusedCard?.col === col.key && focusedCard?.idx === idx}
                        onFocus={() => setFocusedCard({ col: col.key, idx })}
                        onClick={() => setSelectedLead(lead)}
                      />
                    ))}
                    {leads.length === 0 && (
                      <p className="text-xs text-muted-foreground text-center py-6">Sin leads</p>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {selectedLead && (
        <LSSLeadDetail lead={selectedLead} onClose={() => setSelectedLead(null)} />
      )}
      <LSSImportModal open={importOpen} onOpenChange={setImportOpen} />
    </>
  );
}

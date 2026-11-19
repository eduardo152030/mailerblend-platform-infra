import { Badge } from "@/components/ui/badge";
import { format } from "date-fns";
import { es } from "date-fns/locale";

interface TimelineEvent {
  date: string;
  type: string;
  title: string;
  description?: string;
  icon: string;
}

interface Props {
  lead: Record<string, any>;
  attempts: Record<string, any>[];
  conversations: Record<string, any>[];
  approvals: Record<string, any>[];
  outcome?: Record<string, any> | null;
}

export default function LeadDetailTimeline({ lead, attempts, conversations, approvals, outcome }: Props) {
  const events: TimelineEvent[] = [];

  // Attempts
  attempts.forEach((a) => {
    const meta = typeof a.metadata === "string" ? (() => { try { return JSON.parse(a.metadata); } catch { return {}; } })() : (a.metadata ?? {});
    events.push({
      date: a.attempted_at,
      type: "attempt",
      title: a.attempt_type?.replace(/_/g, " ") || "Attempt",
      description: a.result === "COMPLETED"
        ? meta.fields_updated ? `Campos: ${meta.fields_updated.join(", ")}` : (meta.auto_classified ? `Auto-clasificado, score: ${meta.initial_score}` : a.result)
        : a.result,
      icon: a.attempt_type === "INVITE" ? "📨" : a.attempt_type === "SCORE_UPDATE" ? "📊" : "⚡",
    });
  });

  // Conversations
  conversations.forEach((c) => {
    events.push({
      date: c.sent_at,
      type: "message",
      title: c.direction === "SENT" ? "Mensaje enviado" : "Mensaje recibido",
      description: `"${c.message_text?.slice(0, 80)}${(c.message_text?.length ?? 0) > 80 ? "..." : ""}" — ${c.sent_by}`,
      icon: c.direction === "SENT" ? "📤" : "📥",
    });
  });

  // Approvals
  approvals.forEach((a) => {
    events.push({
      date: a.created_at,
      type: "approval",
      title: "Approval creada",
      description: a.approved == null ? "Pendiente" : a.approved ? "Aprobada" : "Rechazada",
      icon: "📝",
    });
  });

  // Outcome
  if (outcome) {
    events.push({
      date: outcome.created_at,
      type: "outcome",
      title: `Outcome: ${outcome.outcome}`,
      description: outcome.notes,
      icon: "🎯",
    });
  }

  // Sort DESC
  events.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

  if (events.length === 0) {
    return <p className="text-center text-sm text-muted-foreground py-10">Sin actividad registrada.</p>;
  }

  const typeColors: Record<string, string> = {
    attempt: "bg-blue-500/15 text-blue-700 dark:text-blue-400",
    message: "bg-primary/15 text-primary",
    approval: "bg-amber-500/15 text-amber-700 dark:text-amber-400",
    outcome: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-400",
  };

  return (
    <div className="space-y-1">
      <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-4">📊 Timeline de Actividad</h4>
      <div className="relative">
        <div className="absolute left-3 top-0 bottom-0 w-px bg-border" />
        <div className="space-y-4">
          {events.map((ev, i) => (
            <div key={i} className="flex gap-4 relative">
              <div className="w-6 h-6 rounded-full bg-background border flex items-center justify-center text-xs z-10 shrink-0">
                {ev.icon}
              </div>
              <div className="flex-1 pb-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-medium">{ev.title}</span>
                  <Badge variant="outline" className={`text-[9px] px-1.5 py-0 ${typeColors[ev.type] || ""}`}>
                    {ev.type}
                  </Badge>
                </div>
                {ev.description && (
                  <p className="text-xs text-muted-foreground mt-0.5">{ev.description}</p>
                )}
                <p className="text-[10px] text-muted-foreground mt-1">
                  {ev.date ? format(new Date(ev.date), "dd MMM yyyy, HH:mm", { locale: es }) : ""}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

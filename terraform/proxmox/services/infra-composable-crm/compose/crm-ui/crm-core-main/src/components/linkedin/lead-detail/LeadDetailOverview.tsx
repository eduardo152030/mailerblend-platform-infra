import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { linkedinProfileUrl, PACK_COLORS } from "@/lib/linkedin-presentation";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import { formatDistanceToNow } from "date-fns";

function Field({ label, children }: { label: string; children?: React.ReactNode }) {
  return (
    <div>
      <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-0.5">{label}</p>
      <div className="text-sm">{children != null && children !== "" ? children : "—"}</div>
    </div>
  );
}

interface Props {
  lead: Record<string, any>;
  attempts: Record<string, any>[];
  conversations: Record<string, any>[];
  approvals: Record<string, any>[];
  outcome?: Record<string, any> | null;
}

export default function LeadDetailOverview({ lead, attempts, conversations, approvals, outcome }: Props) {
  const pack = PACK_COLORS[lead.pack_candidate] || PACK_COLORS.NONE;
  const rawBreakdown = lead.score_breakdown;
  const scoreBreakdown: Record<string, number> = typeof rawBreakdown === "string"
    ? (() => { try { return JSON.parse(rawBreakdown); } catch { return {}; } })()
    : (rawBreakdown ?? {});

  const pendingApprovals = approvals.filter((a) => a.approved == null);

  return (
    <div className="space-y-5">
      {/* Info Básica */}
      <section>
        <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">📋 Información Básica</h4>
        <div className="grid grid-cols-2 gap-3">
          <Field label="LinkedIn">
            {lead.linkedin_url ? (
              <a href={linkedinProfileUrl(lead.linkedin_url)} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline text-sm truncate block">
                {lead.linkedin_url.replace("https://linkedin.com/in/", "")}
              </a>
            ) : "—"}
          </Field>
          <Field label="Empresa">{lead.company}</Field>
          <Field label="Cargo">{lead.title}</Field>
          <Field label="Ubicación">{lead.location}</Field>
          <Field label="Pack">
            <Badge className={`${pack.bg} ${pack.text} border-0 text-xs`}>{pack.emoji} {pack.label}</Badge>
          </Field>
          <Field label="Segmento">{lead.segment}</Field>
          <Field label="Creado">
            {lead.created_at ? format(new Date(lead.created_at), "dd MMM yyyy, HH:mm", { locale: es }) : "—"}
          </Field>
          <Field label="Actualizado">
            {lead.updated_at ? format(new Date(lead.updated_at), "dd MMM yyyy, HH:mm", { locale: es }) : "—"}
          </Field>
        </div>
      </section>

      <Separator />

      {/* Lead Score */}
      <section>
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">🎯 Lead Score</h4>
          <span className="text-lg font-bold">{lead.lead_score ?? 0}/100</span>
        </div>
        <Progress value={lead.lead_score ?? 0} className="h-2 mb-3" />
        {Object.keys(scoreBreakdown).length > 0 && (
          <div className="space-y-2">
            {Object.entries(scoreBreakdown).map(([key, val]) => (
              <div key={key} className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground capitalize">{key.replace(/_/g, " ")}</span>
                <div className="flex items-center gap-2">
                  <Progress value={val as number} className="h-1.5 w-20" />
                  <span className="text-xs font-medium w-8 text-right">{val as number} pts</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <Separator />

      {/* Stats Rápidas */}
      <section>
        <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">📊 Stats Rápidas</h4>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Card>
            <CardContent className="p-3 text-center">
              <p className="text-2xl font-bold">{attempts.length}</p>
              <p className="text-[10px] text-muted-foreground">Attempts</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-3 text-center">
              <p className="text-2xl font-bold">{conversations.length}</p>
              <p className="text-[10px] text-muted-foreground">Mensajes</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-3 text-center">
              <p className="text-2xl font-bold">{pendingApprovals.length}</p>
              <p className="text-[10px] text-muted-foreground">Approvals pend.</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-3 text-center">
              <p className="text-2xl font-bold text-xs">
                {lead.last_attempt_at
                  ? formatDistanceToNow(new Date(lead.last_attempt_at), { locale: es, addSuffix: true })
                  : "—"}
              </p>
              <p className="text-[10px] text-muted-foreground">Última actividad</p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Outcome */}
      {outcome && (
        <>
          <Separator />
          <section>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">✅ Outcome</h4>
            <Card className="bg-emerald-500/5 border-emerald-500/20">
              <CardContent className="p-4 space-y-1">
                <div className="flex items-center gap-2">
                  <Badge className="bg-emerald-600/20 text-emerald-700 dark:text-emerald-300 border-0">{outcome.outcome}</Badge>
                </div>
                {outcome.call_scheduled_at && (
                  <p className="text-sm">📅 Call: {format(new Date(outcome.call_scheduled_at), "dd MMM yyyy", { locale: es })}</p>
                )}
                {outcome.notes && <p className="text-sm text-muted-foreground">📝 {outcome.notes}</p>}
                {outcome.calendar_event_id && (
                  <p className="text-xs text-muted-foreground">🔗 Event: {outcome.calendar_event_id}</p>
                )}
                {outcome.created_at && (
                  <p className="text-xs text-muted-foreground">⏰ {format(new Date(outcome.created_at), "dd MMM yyyy, HH:mm", { locale: es })}</p>
                )}
              </CardContent>
            </Card>
          </section>
        </>
      )}
    </div>
  );
}

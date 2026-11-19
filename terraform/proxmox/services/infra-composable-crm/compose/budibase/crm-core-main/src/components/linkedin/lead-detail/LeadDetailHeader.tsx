import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { PACK_COLORS, STATUS_COLORS } from "@/lib/linkedin-mock-data";
import { ExternalLink, Pencil, Zap, Trash2 } from "lucide-react";

interface Props {
  lead: Record<string, any>;
  outcome?: Record<string, any> | null;
  onDelete?: () => void;
}

export default function LeadDetailHeader({ lead, outcome, onDelete }: Props) {
  const pack = PACK_COLORS[lead.pack_candidate] || PACK_COLORS.NONE;
  const score = lead.lead_score ?? 0;
  const initials = (lead.full_name || "?")
    .split(" ")
    .map((w: string) => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <div className="space-y-4">
      {/* Identity */}
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-lg shrink-0">
          {initials}
        </div>
        <div className="flex-1 min-w-0">
          <h2 className="text-lg font-semibold leading-tight">{lead.full_name}</h2>
          <p className="text-sm text-muted-foreground">{lead.title} @ {lead.company}</p>
          {lead.location && (
            <p className="text-xs text-muted-foreground">📍 {lead.location}</p>
          )}
        </div>
      </div>

      {/* Badges row */}
      <div className="flex flex-wrap items-center gap-2">
        <Badge className={`${pack.bg} ${pack.text} border-0 text-xs`}>{pack.emoji} {pack.label}</Badge>
        <Badge className={`${STATUS_COLORS[lead.status] || ""} border-0 text-xs`}>{lead.status}</Badge>
        {outcome && (
          <Badge className="bg-emerald-600/20 text-emerald-700 dark:text-emerald-300 border-0 text-xs">
            📅 {outcome.outcome}
          </Badge>
        )}
        <div className="flex items-center gap-2 ml-auto">
          <span className="text-xs text-muted-foreground">Score</span>
          <Progress value={score} className="h-2 w-16" />
          <span className="text-sm font-bold">{score}</span>
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex flex-wrap gap-2">
        {lead.linkedin_url && (
          <Button variant="outline" size="sm" asChild>
            <a href={lead.linkedin_url} target="_blank" rel="noopener noreferrer">
              <ExternalLink size={14} className="mr-1" /> LinkedIn
            </a>
          </Button>
        )}
        {lead.status === "CONVERTED" && (
          <Button variant="outline" size="sm">
            <Zap size={14} className="mr-1" /> Crear Oportunidad
          </Button>
        )}
        {onDelete && (
          <Button variant="outline" size="sm" className="text-destructive hover:text-destructive" onClick={onDelete}>
            <Trash2 size={14} className="mr-1" /> Eliminar
          </Button>
        )}
      </div>
    </div>
  );
}

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import { Bot } from "lucide-react";

interface Props {
  approvals: Record<string, any>[];
}

export default function LeadDetailApprovals({ approvals }: Props) {
  if (approvals.length === 0) {
    return <p className="text-center text-sm text-muted-foreground py-10">No hay approvals para este lead.</p>;
  }

  return (
    <>
      <div className="space-y-3">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">✅ Drafts de IA Generados</h4>
        {approvals.map((a) => {
          const isPending = a.approved == null;
          return (
            <Card key={a.id} className={isPending ? "border-primary/30" : ""}>
              <CardContent className="p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">
                    {a.created_at ? format(new Date(a.created_at), "dd MMM yyyy, HH:mm", { locale: es }) : ""}
                  </span>
                  <Badge variant={isPending ? "default" : a.approved ? "secondary" : "destructive"} className="text-[10px]">
                    {isPending ? "⏳ Pendiente" : a.approved ? "✅ Aprobado" : "❌ Rechazado"}
                  </Badge>
                </div>

                <div className="bg-muted/50 rounded-lg p-3">
                  <p className="text-sm">{a.draft_message}</p>
                </div>

                {a.ai_rationale && (
                  <div className="flex items-start gap-2 text-xs text-muted-foreground">
                    <Bot size={14} className="shrink-0 mt-0.5" />
                    <p>{a.ai_rationale}</p>
                  </div>
                )}

                {a.final_message && a.final_message !== a.draft_message && (
                  <div className="bg-primary/5 rounded-lg p-3">
                    <p className="text-[10px] uppercase text-muted-foreground mb-1">Mensaje final</p>
                    <p className="text-sm">{a.final_message}</p>
                  </div>
                )}

              </CardContent>
            </Card>
          );
        })}
      </div>

    </>
  );
}

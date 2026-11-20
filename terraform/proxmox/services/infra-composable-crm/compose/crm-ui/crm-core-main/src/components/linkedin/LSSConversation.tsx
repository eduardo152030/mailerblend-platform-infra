import { Badge } from "@/components/ui/badge";
import { formatDistanceToNow } from "date-fns";
import { es } from "date-fns/locale";

const SENTIMENT_COLORS: Record<string, string> = {
  POSITIVE: "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400",
  NEUTRAL: "bg-muted text-muted-foreground",
  NEGATIVE: "bg-red-500/15 text-red-600 dark:text-red-400",
};

export default function LSSConversation({
  lead,
  conversations,
}: {
  lead: Record<string, any>;
  conversations: Record<string, any>[];
}) {
  return (
    <div className="flex flex-col h-full">
      <p className="text-xs text-muted-foreground mb-4">
        💬 Historial con {lead.full_name} — {lead.title} @ {lead.company}
      </p>

      {/* Messages */}
      <div className="flex-1 space-y-4 mb-4">
        {conversations.map((msg: any) => {
          const isSent = msg.direction === "SENT";
          return (
            <div key={msg.id} className={`flex ${isSent ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[85%] rounded-lg p-3 ${isSent ? "bg-primary/10" : "bg-muted"}`}>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[10px] font-medium">
                    {isSent ? "📤 Tú" : `📥 ${msg.sent_by}`}
                  </span>
                  <span className="text-[10px] text-muted-foreground">
                    {formatDistanceToNow(new Date(msg.sent_at), { addSuffix: true, locale: es })}
                  </span>
                  {msg.sentiment && (
                    <Badge className={`text-[9px] px-1 py-0 border-0 ${SENTIMENT_COLORS[msg.sentiment] || ""}`}>
                      {msg.sentiment}
                    </Badge>
                  )}
                  {msg.intent && (
                    <Badge variant="outline" className="text-[9px] px-1 py-0">
                      {msg.intent}
                    </Badge>
                  )}
                </div>
                <p className="text-sm">{msg.message_text}</p>
              </div>
            </div>
          );
        })}

        {conversations.length === 0 && (
          <p className="text-center text-sm text-muted-foreground py-10">
            No hay mensajes aún con este lead.
          </p>
        )}
      </div>

    </div>
  );
}

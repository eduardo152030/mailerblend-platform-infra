import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ArrowLeft, Send, CalendarDays } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { es } from "date-fns/locale";
import { useLSSCreateConversation } from "@/hooks/use-api";
import { toast } from "@/hooks/use-toast";

const SENTIMENT_COLORS: Record<string, string> = {
  POSITIVE: "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400",
  NEUTRAL: "bg-muted text-muted-foreground",
  NEGATIVE: "bg-red-500/15 text-red-600 dark:text-red-400",
};

export default function LSSConversation({
  lead,
  conversations,
  onBack,
}: {
  lead: Record<string, any>;
  conversations: Record<string, any>[];
  onBack: () => void;
}) {
  const [message, setMessage] = useState("");
  const createMsg = useLSSCreateConversation();

  const handleSend = () => {
    if (!message.trim()) return;
    createMsg.mutate(
      {
        linkedin_lead_id: lead.id,
        message_text: message.trim(),
        direction: "SENT",
        sent_by: "Jainer",
      },
      {
        onSuccess: () => {
          setMessage("");
          toast({ title: "Mensaje enviado" });
        },
        onError: () => {
          toast({ title: "Error al enviar", variant: "destructive" });
        },
      }
    );
  };

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

      {/* Input */}
      <div className="flex gap-2 pt-3 border-t">
        <Input
          placeholder="Escribir mensaje..."
          className="flex-1"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <Button size="icon" variant="default" onClick={handleSend} disabled={createMsg.isPending}>
          <Send size={16} />
        </Button>
        <Button size="icon" variant="outline" title="Enviar link Cal.com">
          <CalendarDays size={16} />
        </Button>
      </div>
    </div>
  );
}

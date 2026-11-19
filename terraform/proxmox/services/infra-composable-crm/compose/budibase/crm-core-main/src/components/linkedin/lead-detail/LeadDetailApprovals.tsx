import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { useLSSApproveApproval, useLSSRejectApproval } from "@/hooks/use-api";
import { toast } from "@/hooks/use-toast";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import { Check, X, Bot } from "lucide-react";

interface Props {
  approvals: Record<string, any>[];
  onApproved?: () => void;
}

export default function LeadDetailApprovals({ approvals, onApproved }: Props) {
  const [approveTarget, setApproveTarget] = useState<Record<string, any> | null>(null);
  const [finalMessage, setFinalMessage] = useState("");
  const [angle, setAngle] = useState("");
  const [painAssessment, setPainAssessment] = useState("");
  const [humanNote, setHumanNote] = useState("");

  const approveMut = useLSSApproveApproval();
  const rejectMut = useLSSRejectApproval();

  const openApprove = (a: Record<string, any>) => {
    setApproveTarget(a);
    setFinalMessage(a.draft_message || "");
    setAngle("");
    setPainAssessment("");
    setHumanNote("");
  };

  const handleApprove = () => {
    if (!approveTarget) return;
    approveMut.mutate(
      {
        id: approveTarget.id,
        data: {
          final_message: finalMessage,
          angle: angle || undefined,
          pain_assessment: painAssessment || undefined,
          human_note: humanNote || undefined,
        },
      },
      {
        onSuccess: () => {
          toast({ title: "✅ Mensaje aprobado y enviado" });
          setApproveTarget(null);
          onApproved?.();
        },
        onError: () => toast({ title: "Error al aprobar", variant: "destructive" }),
      }
    );
  };

  const handleReject = (id: string) => {
    rejectMut.mutate(
      { id, data: { human_note: "Rechazado manualmente" } },
      {
        onSuccess: () => toast({ title: "Draft rechazado" }),
        onError: () => toast({ title: "Error al rechazar", variant: "destructive" }),
      }
    );
  };

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

                {isPending && (
                  <div className="flex gap-2">
                    <Button size="sm" onClick={() => openApprove(a)}>
                      <Check size={14} className="mr-1" /> Aprobar
                    </Button>
                    <Button size="sm" variant="outline" className="text-destructive" onClick={() => handleReject(a.id)}>
                      <X size={14} className="mr-1" /> Rechazar
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Approve dialog */}
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
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium text-muted-foreground">Angle</label>
                <Select value={angle} onValueChange={setAngle}>
                  <SelectTrigger><SelectValue placeholder="Seleccionar..." /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="good">Bueno</SelectItem>
                    <SelectItem value="needs_work">Mejorable</SelectItem>
                    <SelectItem value="bad">Malo</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground">Pain Assessment</label>
                <Select value={painAssessment} onValueChange={setPainAssessment}>
                  <SelectTrigger><SelectValue placeholder="Seleccionar..." /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="real">Real</SelectItem>
                    <SelectItem value="assumed">Asumido</SelectItem>
                    <SelectItem value="unclear">No claro</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground">Nota adicional</label>
              <Textarea value={humanNote} onChange={(e) => setHumanNote(e.target.value)} rows={2} placeholder="Feedback para la IA..." />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setApproveTarget(null)}>Cancelar</Button>
            <Button onClick={handleApprove} disabled={approveMut.isPending}>
              <Check size={14} className="mr-1" /> Aprobar y Enviar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

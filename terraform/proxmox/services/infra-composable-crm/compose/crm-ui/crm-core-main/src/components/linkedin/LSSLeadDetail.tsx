import { Sheet, SheetContent, SheetHeader } from "@/components/ui/sheet";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { useLSSLeadSnapshot, useLSSOutcomes, useLSSDeleteLead } from "@/hooks/use-api";
import { toast } from "@/hooks/use-toast";
import { useState } from "react";
import { LayoutDashboard, MessageSquare, CheckSquare, Clock } from "lucide-react";

import LeadDetailHeader from "./lead-detail/LeadDetailHeader";
import LeadDetailOverview from "./lead-detail/LeadDetailOverview";
import LeadDetailApprovals from "./lead-detail/LeadDetailApprovals";
import LeadDetailTimeline from "./lead-detail/LeadDetailTimeline";
import LSSConversation from "./LSSConversation";

export default function LSSLeadDetail({ lead, onClose }: { lead: Record<string, any>; onClose: () => void }) {
  const [tab, setTab] = useState("overview");
  const { data: snapshot, isLoading } = useLSSLeadSnapshot(lead.id);
  const { data: outcomesData } = useLSSOutcomes({ lead_id: lead.id, limit: 1 });
  const deleteMut = useLSSDeleteLead();

  const snap = snapshot as Record<string, any> | undefined;
  const leadData = snap?.lead ?? lead;
  const attempts = snap?.attempts ?? [];
  const conversations = snap?.conversations ?? [];
  const approvals = snap?.approvals ?? [];
  const outcome = ((outcomesData as any)?.items ?? [])[0] ?? null;

  const handleDelete = () => {
    if (!confirm("¿Eliminar este lead? Esta acción no se puede deshacer.")) return;
    deleteMut.mutate(lead.id, {
      onSuccess: () => {
        toast({ title: "Lead eliminado" });
        onClose();
      },
      onError: () => toast({ title: "Error al eliminar", variant: "destructive" }),
    });
  };

  return (
    <Sheet open onOpenChange={onClose}>
      <SheetContent className="w-full sm:max-w-xl overflow-y-auto p-0">
        {isLoading ? (
          <div className="p-6 space-y-4">
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-64 w-full" />
          </div>
        ) : (
          <div className="flex flex-col h-full">
            {/* Header */}
            <div className="p-6 pb-0">
              <LeadDetailHeader lead={leadData} outcome={outcome} onDelete={handleDelete} />
            </div>

            <Separator className="mt-4" />

            {/* Tabs */}
            <Tabs value={tab} onValueChange={setTab} className="flex-1 flex flex-col">
              <TabsList className="mx-6 mt-3 w-auto justify-start">
                <TabsTrigger value="overview" className="text-xs">
                  <LayoutDashboard size={13} className="mr-1" /> Overview
                </TabsTrigger>
                <TabsTrigger value="conversations" className="text-xs">
                  <MessageSquare size={13} className="mr-1" /> Chat ({conversations.length})
                </TabsTrigger>
                <TabsTrigger value="approvals" className="text-xs">
                  <CheckSquare size={13} className="mr-1" /> Approvals ({approvals.length})
                </TabsTrigger>
                <TabsTrigger value="timeline" className="text-xs">
                  <Clock size={13} className="mr-1" /> Timeline
                </TabsTrigger>
              </TabsList>

              <div className="flex-1 overflow-y-auto p-6">
                <TabsContent value="overview" className="mt-0">
                  <LeadDetailOverview
                    lead={leadData}
                    attempts={attempts}
                    conversations={conversations}
                    approvals={approvals}
                    outcome={outcome}
                  />
                </TabsContent>

                <TabsContent value="conversations" className="mt-0 h-full">
                  <LSSConversation
                    lead={leadData}
                    conversations={conversations}
                    onBack={() => setTab("overview")}
                  />
                </TabsContent>

                <TabsContent value="approvals" className="mt-0">
                  <LeadDetailApprovals
                    approvals={approvals}
                    onApproved={() => setTab("conversations")}
                  />
                </TabsContent>

                <TabsContent value="timeline" className="mt-0">
                  <LeadDetailTimeline
                    lead={leadData}
                    attempts={attempts}
                    conversations={conversations}
                    approvals={approvals}
                    outcome={outcome}
                  />
                </TabsContent>
              </div>
            </Tabs>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}

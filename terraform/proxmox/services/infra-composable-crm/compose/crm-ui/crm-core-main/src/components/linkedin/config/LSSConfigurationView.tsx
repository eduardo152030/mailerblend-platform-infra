import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BookOpen, Gauge, Activity, Pause, MessageSquare } from "lucide-react";
import KnowledgeBaseSection from "./KnowledgeBaseSection";
import RateLimitsSection from "./RateLimitsSection";
import ActivityLogSection from "./ActivityLogSection";
import CooldownsSection from "./CooldownsSection";
import InviteTemplatesSection from "./InviteTemplatesSection";

export default function LSSConfigurationView() {
  return (
    <Tabs defaultValue="knowledge" className="w-full">
      <TabsList className="flex-wrap h-auto gap-1">
        <TabsTrigger value="knowledge" className="text-xs">
          <BookOpen size={13} className="mr-1" /> Knowledge Base
        </TabsTrigger>
        <TabsTrigger value="rate-limits" className="text-xs">
          <Gauge size={13} className="mr-1" /> Rate Limits
        </TabsTrigger>
        <TabsTrigger value="activity" className="text-xs">
          <Activity size={13} className="mr-1" /> Activity
        </TabsTrigger>
        <TabsTrigger value="cooldowns" className="text-xs">
          <Pause size={13} className="mr-1" /> Cooldowns
        </TabsTrigger>
        <TabsTrigger value="invite-templates" className="text-xs">
          <MessageSquare size={13} className="mr-1" /> Invite Templates
        </TabsTrigger>
      </TabsList>

      <TabsContent value="knowledge" className="mt-4">
        <KnowledgeBaseSection />
      </TabsContent>
      <TabsContent value="rate-limits" className="mt-4">
        <RateLimitsSection />
      </TabsContent>
      <TabsContent value="activity" className="mt-4">
        <ActivityLogSection />
      </TabsContent>
      <TabsContent value="cooldowns" className="mt-4">
        <CooldownsSection />
      </TabsContent>
      <TabsContent value="invite-templates" className="mt-4">
        <InviteTemplatesSection />
      </TabsContent>
    </Tabs>
  );
}

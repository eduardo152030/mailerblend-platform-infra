import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PageHeader } from "@/components/PageHeader";
import LSSDashboard from "@/components/linkedin/LSSDashboard";
import LSSLeadsPipeline from "@/components/linkedin/LSSLeadsPipeline";
import LSSConfigurationView from "@/components/linkedin/config/LSSConfigurationView";
import { LayoutDashboard, Kanban, Settings } from "lucide-react";

export default function LinkedInSourcingPage() {
  const [tab, setTab] = useState("dashboard");

  return (
    <>
      <PageHeader title="LinkedIn Sourcing" subtitle="Prospección asistida por IA" />

      <Tabs value={tab} onValueChange={setTab} className="mt-4">
        <TabsList>
          <TabsTrigger value="dashboard">
            <LayoutDashboard size={14} className="mr-1" /> Dashboard
          </TabsTrigger>
          <TabsTrigger value="pipeline">
            <Kanban size={14} className="mr-1" /> Leads Pipeline
          </TabsTrigger>
          <TabsTrigger value="config">
            <Settings size={14} className="mr-1" /> Configuración
          </TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="mt-4">
          <LSSDashboard />
        </TabsContent>

        <TabsContent value="pipeline" className="mt-4">
          <LSSLeadsPipeline />
        </TabsContent>

        <TabsContent value="config" className="mt-4">
          <LSSConfigurationView />
        </TabsContent>
      </Tabs>
    </>
  );
}

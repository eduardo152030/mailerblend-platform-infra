import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BarChart3, List } from "lucide-react";
import UTMDashboard from "@/components/utm/UTMDashboard";
import UTMLista from "@/components/utm/UTMLista";

export default function UTMPage() {
  return (
    <Tabs defaultValue="lista" className="space-y-4">
      <TabsList>
        <TabsTrigger value="dashboard" className="gap-1.5">
          <BarChart3 size={14} /> Dashboard
        </TabsTrigger>
        <TabsTrigger value="lista" className="gap-1.5">
          <List size={14} /> Registros UTM
        </TabsTrigger>
      </TabsList>

      <TabsContent value="dashboard">
        <UTMDashboard />
      </TabsContent>

      <TabsContent value="lista">
        <UTMLista />
      </TabsContent>
    </Tabs>
  );
}
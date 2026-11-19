import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BarChart3, Clock, List } from "lucide-react";
import ConversionesDashboard from "@/components/conversiones/ConversionesDashboard";
import ConversionesCola from "@/components/conversiones/ConversionesCola";
import ConversionesHistorial from "@/components/conversiones/ConversionesHistorial";

export default function ConversionesOfflinePage() {
  return (
    <Tabs defaultValue="dashboard" className="space-y-4">
      <TabsList>
        <TabsTrigger value="dashboard" className="gap-1.5">
          <BarChart3 size={14} /> Dashboard
        </TabsTrigger>
        <TabsTrigger value="cola" className="gap-1.5">
          <Clock size={14} /> Cola de Sincronización
        </TabsTrigger>
        <TabsTrigger value="historial" className="gap-1.5">
          <List size={14} /> Historial
        </TabsTrigger>
      </TabsList>

      <TabsContent value="dashboard">
        <ConversionesDashboard />
      </TabsContent>

      <TabsContent value="cola">
        <ConversionesCola />
      </TabsContent>

      <TabsContent value="historial">
        <ConversionesHistorial />
      </TabsContent>
    </Tabs>
  );
}

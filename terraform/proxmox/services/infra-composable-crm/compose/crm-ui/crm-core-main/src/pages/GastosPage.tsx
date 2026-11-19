import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BarChart3, List } from "lucide-react";
import GastosDashboard from "@/components/gastos/GastosDashboard";
import GastosLista from "@/components/gastos/GastosLista";

export default function GastosPage() {
  return (
    <Tabs defaultValue="dashboard" className="space-y-4">
      <TabsList>
        <TabsTrigger value="dashboard" className="gap-1.5">
          <BarChart3 size={14} /> Dashboard
        </TabsTrigger>
        <TabsTrigger value="lista" className="gap-1.5">
          <List size={14} /> Lista de Gastos
        </TabsTrigger>
      </TabsList>

      <TabsContent value="dashboard">
        <GastosDashboard />
      </TabsContent>

      <TabsContent value="lista">
        <GastosLista />
      </TabsContent>
    </Tabs>
  );
}

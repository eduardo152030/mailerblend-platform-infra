import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Upload, User } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { useLSSImportLeads } from "@/hooks/use-api";

export default function LSSImportModal({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const [tab, setTab] = useState("csv");
  const importMutation = useLSSImportLeads();

  const handleCSVUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!/\.csv$/i.test(file.name) || !["", "text/csv", "text/plain", "application/vnd.ms-excel"].includes(file.type) ||
        file.size > 512 * 1024) {
      toast({ title: "Selecciona un CSV de hasta 512 KiB", variant: "destructive" });
      e.target.value = "";
      return;
    }


    const reader = new FileReader();
    reader.onload = (ev) => {
      const text = ev.target?.result as string;
      const lines = text.trim().split("\n");
      const headers = lines[0].split(",").map((h) => h.trim().toLowerCase());
      const leads = lines.slice(1).map((line) => {
        const vals = line.split(",").map((v) => v.trim());
        const obj: Record<string, string> = Object.create(null);
        headers.forEach((h, i) => { if (vals[i]) obj[h] = vals[i]; });
        return obj;
      }).filter((l) => l.linkedin_url || l.full_name);

      if (leads.length === 0) {
        toast({ title: "CSV vacío", description: "No se encontraron leads válidos", variant: "destructive" });
        return;
      }

      importMutation.mutate(
        { leads, auto_classify: true },
        {
          onSuccess: (result) => {
            toast({
              title: `${result.successful} leads importados`,
              description: result.failed > 0 ? `${result.failed} fallidos, ${result.duplicates} duplicados` : undefined,
            });
            onOpenChange(false);
          },
          onError: () => {
            toast({ title: "Error al importar", variant: "destructive" });
          },
        }
      );
    };
    reader.readAsText(file);
  };

  const handleManual = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const lead: Record<string, string> = {};
    form.forEach((v, k) => { if (v) lead[k] = v as string; });

    const packValue = lead.pack_candidate;
    if (packValue === "__auto__") delete lead.pack_candidate;

    importMutation.mutate(
      { leads: [lead], auto_classify: !packValue || packValue === "__auto__" },
      {
        onSuccess: (result) => {
          toast({ title: `Lead importado (${result.successful} OK)` });
          onOpenChange(false);
        },
        onError: () => {
          toast({ title: "Error al importar", variant: "destructive" });
        },
      }
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Importar Leads de LinkedIn</DialogTitle>
        </DialogHeader>

        <Tabs value={tab} onValueChange={setTab}>
          <TabsList className="w-full">
            <TabsTrigger value="csv" className="flex-1">
              <Upload size={14} className="mr-1" /> Subir CSV
            </TabsTrigger>
            <TabsTrigger value="manual" className="flex-1">
              <User size={14} className="mr-1" /> Entrada Manual
            </TabsTrigger>
          </TabsList>

          <TabsContent value="csv" className="space-y-4 mt-4">
            <div className="border-2 border-dashed rounded-lg p-6 text-center cursor-pointer hover:border-primary/50 transition-colors"
              onClick={() => document.getElementById("csv-upload")?.click()}
            >
              <Upload size={24} className="mx-auto mb-2 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">Arrastra CSV aquí o haz click para seleccionar</p>
              <p className="text-xs text-muted-foreground mt-1">Formato: linkedin_url, full_name, title, company, location</p>
              <input id="csv-upload" type="file" accept=".csv" className="hidden" onChange={handleCSVUpload} />
            </div>
          </TabsContent>

          <TabsContent value="manual" className="mt-4">
            <form onSubmit={handleManual} className="space-y-3">
              <div>
                <Label className="text-xs">LinkedIn URL *</Label>
                <Input name="linkedin_url" placeholder="https://linkedin.com/in/..." required />
              </div>
              <div>
                <Label className="text-xs">Nombre completo *</Label>
                <Input name="full_name" placeholder="Juan Pérez" required />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label className="text-xs">Cargo</Label>
                  <Input name="title" placeholder="CTO" />
                </div>
                <div>
                  <Label className="text-xs">Empresa</Label>
                  <Input name="company" placeholder="Acme Corp" />
                </div>
              </div>
              <div>
                <Label className="text-xs">Ubicación</Label>
                <Input name="location" placeholder="Madrid, Spain" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label className="text-xs">Pack Candidato</Label>
                  <Select name="pack_candidate">
                    <SelectTrigger><SelectValue placeholder="Auto-clasificar" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="__auto__">Auto-clasificar</SelectItem>
                      <SelectItem value="GUARDIAN">🟢 Guardián</SelectItem>
                      <SelectItem value="MOTOR">🔵 Motor</SelectItem>
                      <SelectItem value="FORTALEZA">🟣 Fortaleza</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label className="text-xs">Segmento</Label>
                  <Input name="segment" placeholder="Ej: Pack2_Services_BCN" />
                </div>
              </div>
              <Button type="submit" className="w-full" disabled={importMutation.isPending}>
                {importMutation.isPending ? "Importando..." : "✅ Importar y procesar"}
              </Button>
            </form>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}

import { useState, useMemo, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2 } from "lucide-react";
import { useCreateGasto, usePatchGasto, useProveedores } from "@/hooks/use-api";
import { useToast } from "@/hooks/use-toast";

const CATEGORIAS = ["TECNOLOGIA", "MARKETING", "PERSONAL", "OFICINA", "SERVICIOS", "FORMACION", "LEGAL", "OTRO"];
const PROYECTOS = [
  { value: "Nucleo_tecnologico", label: "Núcleo Tecnológico" },
  { value: "Mailerblend", label: "Mailerblend" },
  { value: "SHARED", label: "Compartido (SHARED)" },
];
const ESTADOS = ["PENDIENTE", "PAGADO", "ANULADO", "VENCIDO"];
const METODOS_PAGO = ["Transferencia", "Tarjeta", "Domiciliación", "Efectivo", "PayPal"];
const IVA_OPTIONS = [
  { value: "21", label: "21% (General)" },
  { value: "10", label: "10% (Reducido)" },
  { value: "4", label: "4% (Superreducido)" },
  { value: "0", label: "0% (Exento)" },
];

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  editingGasto?: Record<string, unknown> | null;
}

export default function GastoFormDialog({ open, onOpenChange, editingGasto }: Props) {
  const { toast } = useToast();
  const createMutation = useCreateGasto();
  const patchMutation = usePatchGasto();
  const { data: proveedoresData } = useProveedores({ limit: 200 });
  const isEditing = !!editingGasto;

  const [form, setForm] = useState<Record<string, unknown>>({});

  useEffect(() => {
    if (open) {
      if (editingGasto) {
        setForm({ ...editingGasto });
      } else {
        setForm({
          iva_porcentaje: 21,
          categoria: "OTRO",
          project_key: "Nucleo_tecnologico",
          estado: "PAGADO",
          metodo_pago: "Transferencia",
          currency: "EUR",
          base_imponible: 0,
        });
      }
    }
  }, [open, editingGasto]);

  const setField = (key: string, value: unknown) => setForm((f) => ({ ...f, [key]: value }));

  const baseImponible = Number(form.base_imponible ?? 0);
  const ivaPorcentaje = Number(form.iva_porcentaje ?? 21);
  const ivaImporte = useMemo(() => (baseImponible * ivaPorcentaje) / 100, [baseImponible, ivaPorcentaje]);
  const totalPreview = useMemo(() => baseImponible + ivaImporte, [baseImponible, ivaImporte]);

  const formatCurrency = (v: number) =>
    new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" }).format(v);

  const handleSubmit = async () => {
    if (!form.fecha_gasto || !form.concepto) {
      toast({ title: "Error", description: "Fecha y concepto son requeridos", variant: "destructive" });
      return;
    }
    // Don't send calculated fields
    const { iva_importe, total, id, created_at, updated_at, ...payload } = form;
    try {
      if (isEditing) {
        await patchMutation.mutateAsync({ id: String(editingGasto!.id), data: payload });
        toast({ title: "Actualizado", description: "Gasto actualizado correctamente" });
      } else {
        await createMutation.mutateAsync(payload);
        toast({ title: "Creado", description: "Gasto registrado correctamente" });
      }
      onOpenChange(false);
    } catch (e: unknown) {
      toast({ title: "Error", description: String(e), variant: "destructive" });
    }
  };

  const isPending = createMutation.isPending || patchMutation.isPending;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEditing ? "Editar gasto" : "Nuevo gasto"}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Info Básica */}
          <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Información Básica</h4>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Fecha gasto *</Label>
              <Input type="date" value={String(form.fecha_gasto ?? "")} onChange={(e) => setField("fecha_gasto", e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label>Fecha vencimiento</Label>
              <Input type="date" value={String(form.fecha_vencimiento ?? "")} onChange={(e) => setField("fecha_vencimiento", e.target.value || null)} />
            </div>
          </div>
          <div className="space-y-1">
            <Label>Concepto *</Label>
            <Input placeholder="Ej: Hosting AWS - Febrero 2026" value={String(form.concepto ?? "")} onChange={(e) => setField("concepto", e.target.value)} />
          </div>

          {/* Proveedor */}
          <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Proveedor</h4>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Proveedor (lista)</Label>
              <Select value={String(form.proveedor_id ?? "")} onValueChange={(v) => {
                setField("proveedor_id", v || null);
                if (v) setField("proveedor_nombre", "");
              }}>
                <SelectTrigger><SelectValue placeholder="Seleccionar..." /></SelectTrigger>
                <SelectContent>
                  {proveedoresData?.items?.map((p) => (
                    <SelectItem key={String(p.id)} value={String(p.id)}>{String(p.nombre ?? p.name ?? p.id)}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label>O nombre manual</Label>
              <Input
                placeholder="Ej: Freelancer Juan"
                value={String(form.proveedor_nombre ?? "")}
                disabled={!!form.proveedor_id}
                onChange={(e) => setField("proveedor_nombre", e.target.value)}
              />
            </div>
          </div>

          {/* Categorización */}
          <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Categorización</h4>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Categoría</Label>
              <Select value={String(form.categoria ?? "OTRO")} onValueChange={(v) => setField("categoria", v)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {CATEGORIAS.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label>Proyecto</Label>
              <Select value={String(form.project_key ?? "Nucleo_tecnologico")} onValueChange={(v) => setField("project_key", v)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {PROYECTOS.map((p) => <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Importes */}
          <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Importes</h4>
          <div className="grid grid-cols-3 gap-3">
            <div className="space-y-1">
              <Label>Base imponible (€)</Label>
              <Input type="number" step="0.01" min="0" value={String(form.base_imponible ?? "0")} onChange={(e) => setField("base_imponible", Number(e.target.value))} />
            </div>
            <div className="space-y-1">
              <Label>IVA %</Label>
              <Select value={String(form.iva_porcentaje ?? "21")} onValueChange={(v) => setField("iva_porcentaje", Number(v))}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {IVA_OPTIONS.map((o) => <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label>Moneda</Label>
              <Select value={String(form.currency ?? "EUR")} onValueChange={(v) => setField("currency", v)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="EUR">EUR (€)</SelectItem>
                  <SelectItem value="USD">USD ($)</SelectItem>
                  <SelectItem value="GBP">GBP (£)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          {/* Calculated preview */}
          <div className="rounded-md bg-muted/50 border p-3 grid grid-cols-2 gap-2 text-sm">
            <div>
              <span className="text-muted-foreground">IVA Importe:</span>{" "}
              <span className="font-medium">{formatCurrency(ivaImporte)}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Total:</span>{" "}
              <span className="font-bold text-foreground">{formatCurrency(totalPreview)}</span>
            </div>
          </div>

          {/* Estado y Pago */}
          <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Estado y Pago</h4>
          <div className="grid grid-cols-3 gap-3">
            <div className="space-y-1">
              <Label>Estado</Label>
              <Select value={String(form.estado ?? "PAGADO")} onValueChange={(v) => setField("estado", v)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {ESTADOS.map((e) => <SelectItem key={e} value={e}>{e}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label>Método pago</Label>
              <Select value={String(form.metodo_pago ?? "Transferencia")} onValueChange={(v) => setField("metodo_pago", v)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {METODOS_PAGO.map((m) => <SelectItem key={m} value={m}>{m}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label>Nº Factura</Label>
              <Input placeholder="FAC-2026-001" value={String(form.numero_factura ?? "")} onChange={(e) => setField("numero_factura", e.target.value)} />
            </div>
          </div>

          {/* Documentos */}
          <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Documentos</h4>
          <div className="space-y-1">
            <Label>URL del adjunto (PDF/imagen)</Label>
            <Input placeholder="https://..." value={String(form.adjunto_url ?? "")} onChange={(e) => setField("adjunto_url", e.target.value)} />
          </div>

          {/* Notas */}
          <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Notas</h4>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Notas</Label>
              <Textarea rows={2} placeholder="Notas generales" value={String(form.notas ?? "")} onChange={(e) => setField("notas", e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label>Notas internas</Label>
              <Textarea rows={2} placeholder="Comentarios internos" value={String(form.internal_notes ?? "")} onChange={(e) => setField("internal_notes", e.target.value)} />
            </div>
          </div>

          <Button onClick={handleSubmit} disabled={isPending} className="w-full">
            {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : isEditing ? "Guardar cambios" : "Registrar gasto"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

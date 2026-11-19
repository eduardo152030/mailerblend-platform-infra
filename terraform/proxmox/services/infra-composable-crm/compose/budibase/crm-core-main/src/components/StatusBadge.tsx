import { cn } from "@/lib/utils";

const statusColors: Record<string, string> = {
  // Oportunidades
  "Nuevo": "bg-info/15 text-info",
  "En contacto": "bg-info/15 text-info",
  "Presupuesto enviado": "bg-warning/15 text-warning",
  "Negociación": "bg-warning/15 text-warning",
  "Ganado": "bg-success/15 text-success",
  "Perdido": "bg-destructive/15 text-destructive",
  // Lead Tags
  "Cold": "bg-muted text-muted-foreground",
  "Warm": "bg-warning/15 text-warning",
  "Hot": "bg-destructive/15 text-destructive",
  "Qualified": "bg-success/15 text-success",
  "Unqualified": "bg-muted text-muted-foreground",
  // Pendientes
  "TODO": "bg-muted text-muted-foreground",
  "IN_PROGRESS": "bg-info/15 text-info",
  "DONE": "bg-success/15 text-success",
  "BLOCKED": "bg-destructive/15 text-destructive",
  // Presupuestos
  "Draft": "bg-muted text-muted-foreground",
  "Sent": "bg-info/15 text-info",
  "Accepted": "bg-success/15 text-success",
  "Rejected": "bg-destructive/15 text-destructive",
  "Expired": "bg-warning/15 text-warning",
  // Gastos
  "PENDIENTE": "bg-warning/15 text-warning",
  "PAGADO": "bg-success/15 text-success",
  "ANULADO": "bg-muted text-muted-foreground line-through",
  "VENCIDO": "bg-destructive/15 text-destructive",
  // Proveedores / Tipos
  "TECNOLOGIA": "bg-info/15 text-info",
  "MARKETING": "bg-warning/15 text-warning",
  "SERVICIOS": "bg-primary/15 text-primary",
  "OFICINA": "bg-muted text-muted-foreground",
  "FORMACION": "bg-success/15 text-success",
  "LEGAL": "bg-destructive/15 text-destructive",
  "FINANCIERO": "bg-warning/15 text-warning",
  "TELECOMUNICACIONES": "bg-info/15 text-info",
  "TRANSPORTE": "bg-muted text-muted-foreground",
  "MANTENIMIENTO": "bg-muted text-muted-foreground",
  "HOSTING": "bg-info/15 text-info",
  "SOFTWARE": "bg-primary/15 text-primary",
  "HARDWARE": "bg-muted text-muted-foreground",
  "OTRO": "bg-muted text-muted-foreground",
  // Ad Platforms
  "GOOGLE": "bg-info/15 text-info",
  "BING": "bg-primary/15 text-primary",
  "LINKEDIN": "bg-info/15 text-info",
  "FACEBOOK": "bg-primary/15 text-primary",
  // UTM Sources
  "google": "bg-info/15 text-info",
  "facebook": "bg-primary/15 text-primary",
  "linkedin": "bg-info/15 text-info",
  "newsletter": "bg-warning/15 text-warning",
  "organic": "bg-success/15 text-success",
  // Sync status
  "PENDING": "bg-warning/15 text-warning",
  "SYNCED": "bg-success/15 text-success",
  "FAILED": "bg-destructive/15 text-destructive",
  // Conversion events
  "Lead_Submitted": "bg-muted text-muted-foreground",
  "Lead_Qualified": "bg-info/15 text-info",
  "Lead_Won": "bg-success/15 text-success",
  "Purchase": "bg-primary/15 text-primary",
  "Custom": "bg-warning/15 text-warning",
  // Generic
  "ACTIVO": "bg-success/15 text-success",
  "INACTIVO": "bg-muted text-muted-foreground",
  // Next actions
  "SEND_EMAIL": "bg-info/15 text-info",
  "CALL": "bg-warning/15 text-warning",
  "BOOK_MEETING": "bg-primary/15 text-primary",
  "SEND_PROPOSAL": "bg-info/15 text-info",
  "FOLLOW_UP": "bg-warning/15 text-warning",
  "NO_ACTION": "bg-muted text-muted-foreground",
};

const priorityColors: Record<string, string> = {
  "HIGH": "bg-destructive/15 text-destructive",
  "Alta": "bg-destructive/15 text-destructive",
  "MEDIUM": "bg-warning/15 text-warning",
  "Media": "bg-warning/15 text-warning",
  "LOW": "bg-muted text-muted-foreground",
  "Baja": "bg-muted text-muted-foreground",
};

export function StatusBadge({ value, type = "status" }: { value?: string | null; type?: "status" | "priority" }) {
  if (!value) return null;
  const colors = type === "priority" ? priorityColors : statusColors;
  const cls = colors[value] || "bg-muted text-muted-foreground";
  return (
    <span className={cn("inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium whitespace-nowrap", cls)}>
      {value}
    </span>
  );
}

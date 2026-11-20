// Mock data for LinkedIn Stealth Sourcing module

export const LSS_STATUS: Record<string, string> = {
  NEW: "Lead nuevo, sin procesar",
  INVITE_QUEUED: "En cola para enviar invitación",
  INVITE_SENT: "Invitación enviada, esperando",
  PENDING: "Pendiente dentro de ventana de espera",
  ACCEPTED: "Invitación aceptada ✓",
  NO_ACCEPT: "No aceptó en ventana de tiempo",
  RECYCLE_RETRY: "Marcado para reintento",
  ENGAGE_LATER: "Revisar más tarde",
  ARCHIVED: "Archivado, no es fit",
  IN_CONVERSATION: "Conversación activa",
  AWAITING_RESPONSE: "Esperando respuesta",
  BOOKED: "Sesión agendada",
  CONVERTED: "Convertido a oportunidad",
  NOT_FIT: "No es fit",
  GHOSTED: "Dejó de responder",
};

export const PACK_COLORS: Record<string, { bg: string; text: string; label: string; emoji: string }> = {
  GUARDIAN: { bg: "bg-emerald-500/15", text: "text-emerald-600 dark:text-emerald-400", label: "Guardián", emoji: "🟢" },
  MOTOR: { bg: "bg-blue-500/15", text: "text-blue-600 dark:text-blue-400", label: "Motor", emoji: "🔵" },
  FORTALEZA: { bg: "bg-purple-500/15", text: "text-purple-600 dark:text-purple-400", label: "Fortaleza", emoji: "🟣" },
  NONE: { bg: "bg-muted", text: "text-muted-foreground", label: "Sin pack", emoji: "⚪" },
};

export const STATUS_COLORS: Record<string, string> = {
  NEW: "bg-muted text-muted-foreground",
  INVITE_QUEUED: "bg-yellow-500/15 text-yellow-700 dark:text-yellow-400",
  INVITE_SENT: "bg-blue-500/15 text-blue-700 dark:text-blue-400",
  PENDING: "bg-orange-500/15 text-orange-700 dark:text-orange-400",
  ACCEPTED: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-400",
  NO_ACCEPT: "bg-red-500/15 text-red-600 dark:text-red-400",
  RECYCLE_RETRY: "bg-amber-500/15 text-amber-700 dark:text-amber-400",
  ENGAGE_LATER: "bg-indigo-500/15 text-indigo-700 dark:text-indigo-400",
  ARCHIVED: "bg-muted text-muted-foreground",
  IN_CONVERSATION: "bg-primary/15 text-primary",
  AWAITING_RESPONSE: "bg-cyan-500/15 text-cyan-700 dark:text-cyan-400",
  BOOKED: "bg-emerald-600/20 text-emerald-700 dark:text-emerald-300",
  CONVERTED: "bg-primary/20 text-primary",
  NOT_FIT: "bg-destructive/15 text-destructive",
  GHOSTED: "bg-muted text-muted-foreground",
};

export interface LinkedInLead {
  id: string;
  contacto_id: string | null;
  linkedin_url: string;
  full_name: string;
  title: string;
  company: string;
  location: string;
  pack_candidate: string;
  segment: string;
  status: string;
  lead_score: number;
  score_breakdown: { fit_icp: number; web_signals: number; places_signals: number };
  invite_sent_at: string | null;
  accepted_at: string | null;
  wait_window_days: number;
  next_action_at: string | null;
  web_tech_stack: string[];
  places_name: string | null;
  places_rating: number | null;
  places_user_ratings_total: number | null;
  places_types: string[];
  places_website: string | null;
  places_phone: string | null;
  places_address: string | null;
  created_at: string;
  updated_at: string;
}

export interface LinkedInConversation {
  id: string;
  linkedin_lead_id: string;
  message_text: string;
  direction: "SENT" | "RECEIVED";
  sent_at: string;
  sent_by: string;
  sentiment: string | null;
  intent: string | null;
}

export const KANBAN_COLUMNS = [
  { key: "NEW", label: "Nuevos" },
  { key: "INVITE_QUEUED", label: "En Cola" },
  { key: "INVITE_SENT", label: "Enviados" },
  { key: "ACCEPTED", label: "Aceptados" },
  { key: "IN_CONVERSATION", label: "Conversación" },
  { key: "BOOKED", label: "Booked" },
  { key: "CONVERTED", label: "Convertidos" },
  { key: "ARCHIVED", label: "Archivados" },
];

// Real DB statuses that map to each visual pipeline column
export const PIPELINE_STATUS_MAP: Record<string, string[]> = {
  NEW: ["NEW"],
  INVITE_QUEUED: ["INVITE_QUEUED"],
  INVITE_SENT: ["INVITE_SENT", "PENDING"],
  ACCEPTED: ["ACCEPTED"],       // filtered further by total_attempts <= 1
  IN_CONVERSATION: ["ACCEPTED"], // filtered further by total_attempts > 1
  BOOKED: [],                    // populated from outcomes
  CONVERTED: ["CONVERTED"],
  ARCHIVED: ["ARCHIVED", "NO_ACCEPT", "ENGAGE_LATER", "RECYCLE_RETRY"],
};


export function linkedinProfileUrl(value: unknown) {
  if (typeof value !== "string") return undefined;
  try {
    const url = new URL(value);
    if (url.protocol === "https:" && !url.username && !url.password &&
        (url.hostname === "linkedin.com" || url.hostname.endsWith(".linkedin.com"))) {
      return url.href;
    }
  } catch {
    return undefined;
  }
  return undefined;
}

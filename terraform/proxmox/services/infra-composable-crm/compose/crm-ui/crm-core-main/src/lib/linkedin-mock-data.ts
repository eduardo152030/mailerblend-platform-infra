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

const now = new Date();
const ago = (days: number) => new Date(now.getTime() - days * 86400000).toISOString();

export const MOCK_LEADS: LinkedInLead[] = [
  {
    id: "l1", contacto_id: null, linkedin_url: "https://linkedin.com/in/juanperez",
    full_name: "Juan Pérez", title: "CTO", company: "Acme Corp", location: "Madrid, Spain",
    pack_candidate: "MOTOR", segment: "Pack2_Services_BCN", status: "ACCEPTED", lead_score: 85,
    score_breakdown: { fit_icp: 30, web_signals: 35, places_signals: 20 },
    invite_sent_at: ago(7), accepted_at: ago(3), wait_window_days: 14, next_action_at: null,
    web_tech_stack: ["WordPress", "HubSpot", "Stripe", "Zapier"],
    places_name: "Acme Digital Agency", places_rating: 4.3, places_user_ratings_total: 87,
    places_types: ["Marketing Agency", "IT Services"], places_website: "https://acme.com",
    places_phone: "+34 612 345 678", places_address: "Calle Gran Vía 42, Madrid",
    created_at: ago(10), updated_at: ago(1),
  },
  {
    id: "l2", contacto_id: null, linkedin_url: "https://linkedin.com/in/mariagarcia",
    full_name: "María García", title: "Founder & CEO", company: "Clínica Dental Sonrisa", location: "Barcelona, Spain",
    pack_candidate: "GUARDIAN", segment: "A_<50reviews", status: "INVITE_SENT", lead_score: 72,
    score_breakdown: { fit_icp: 35, web_signals: 15, places_signals: 22 },
    invite_sent_at: ago(2), accepted_at: null, wait_window_days: 14, next_action_at: ago(-12),
    web_tech_stack: ["WordPress"],
    places_name: "Clínica Dental Sonrisa", places_rating: 4.7, places_user_ratings_total: 32,
    places_types: ["Dentist", "Health"], places_website: "https://sonrisa.com",
    places_phone: "+34 933 111 222", places_address: "Carrer de Balmes 15, Barcelona",
    created_at: ago(5), updated_at: ago(2),
  },
  {
    id: "l3", contacto_id: null, linkedin_url: "https://linkedin.com/in/carlosruiz",
    full_name: "Carlos Ruiz", title: "Director de Operaciones", company: "LogiTrans S.L.", location: "Valencia, Spain",
    pack_candidate: "FORTALEZA", segment: "B_>200reviews", status: "IN_CONVERSATION", lead_score: 92,
    score_breakdown: { fit_icp: 38, web_signals: 28, places_signals: 26 },
    invite_sent_at: ago(14), accepted_at: ago(10), wait_window_days: 14, next_action_at: null,
    web_tech_stack: ["Azure", "SAP", "Salesforce"],
    places_name: "LogiTrans Logística", places_rating: 3.9, places_user_ratings_total: 245,
    places_types: ["Logistics", "Transport"], places_website: "https://logitrans.es",
    places_phone: "+34 961 222 333", places_address: "Polígono Industrial Norte 12, Valencia",
    created_at: ago(20), updated_at: ago(0.5),
  },
  {
    id: "l4", contacto_id: null, linkedin_url: "https://linkedin.com/in/anatorres",
    full_name: "Ana Torres", title: "Directora General", company: "Boutique Ana", location: "Sevilla, Spain",
    pack_candidate: "GUARDIAN", segment: "A_<50reviews", status: "NEW", lead_score: 65,
    score_breakdown: { fit_icp: 30, web_signals: 15, places_signals: 20 },
    invite_sent_at: null, accepted_at: null, wait_window_days: 14, next_action_at: null,
    web_tech_stack: ["Wix"],
    places_name: "Boutique Ana", places_rating: 4.5, places_user_ratings_total: 18,
    places_types: ["Clothing Store"], places_website: null,
    places_phone: "+34 655 444 555", places_address: "Calle Sierpes 28, Sevilla",
    created_at: ago(1), updated_at: ago(1),
  },
  {
    id: "l5", contacto_id: null, linkedin_url: "https://linkedin.com/in/pedrosanchez",
    full_name: "Pedro Sánchez", title: "COO", company: "eComm Pro", location: "Bilbao, Spain",
    pack_candidate: "FORTALEZA", segment: "B_>200reviews", status: "BOOKED", lead_score: 88,
    score_breakdown: { fit_icp: 35, web_signals: 30, places_signals: 23 },
    invite_sent_at: ago(21), accepted_at: ago(16), wait_window_days: 14, next_action_at: null,
    web_tech_stack: ["Shopify", "AWS", "Datadog"],
    places_name: "eComm Pro Spain", places_rating: 4.1, places_user_ratings_total: 312,
    places_types: ["eCommerce", "Technology"], places_website: "https://ecommpro.es",
    places_phone: "+34 944 555 666", places_address: "Alameda Recalde 18, Bilbao",
    created_at: ago(25), updated_at: ago(0.2),
  },
  {
    id: "l6", contacto_id: null, linkedin_url: "https://linkedin.com/in/lauramartinez",
    full_name: "Laura Martínez", title: "CEO", company: "Digital Wave Agency", location: "Madrid, Spain",
    pack_candidate: "MOTOR", segment: "Pack2_Services_BCN", status: "INVITE_QUEUED", lead_score: 78,
    score_breakdown: { fit_icp: 28, web_signals: 32, places_signals: 18 },
    invite_sent_at: null, accepted_at: null, wait_window_days: 14, next_action_at: null,
    web_tech_stack: ["React", "Notion", "Slack", "HubSpot", "Stripe"],
    places_name: "Digital Wave", places_rating: 4.6, places_user_ratings_total: 64,
    places_types: ["Digital Agency", "Web Design"], places_website: "https://digitalwave.es",
    places_phone: "+34 611 777 888", places_address: "Calle Serrano 95, Madrid",
    created_at: ago(3), updated_at: ago(3),
  },
  {
    id: "l7", contacto_id: null, linkedin_url: "https://linkedin.com/in/robertodiaz",
    full_name: "Roberto Díaz", title: "Gerente", company: "Taller Díaz e Hijos", location: "Málaga, Spain",
    pack_candidate: "GUARDIAN", segment: "A_<50reviews", status: "NO_ACCEPT", lead_score: 58,
    score_breakdown: { fit_icp: 25, web_signals: 13, places_signals: 20 },
    invite_sent_at: ago(18), accepted_at: null, wait_window_days: 14, next_action_at: ago(-5),
    web_tech_stack: [],
    places_name: "Taller Díaz", places_rating: 3.8, places_user_ratings_total: 12,
    places_types: ["Auto Repair"], places_website: null,
    places_phone: "+34 622 999 000", places_address: "Calle Larios 5, Málaga",
    created_at: ago(22), updated_at: ago(4),
  },
  {
    id: "l8", contacto_id: null, linkedin_url: "https://linkedin.com/in/elenafernandez",
    full_name: "Elena Fernández", title: "Directora Creativa", company: "Creativa Studios", location: "Barcelona, Spain",
    pack_candidate: "MOTOR", segment: "Pack2_Services_BCN", status: "ACCEPTED", lead_score: 80,
    score_breakdown: { fit_icp: 30, web_signals: 30, places_signals: 20 },
    invite_sent_at: ago(8), accepted_at: ago(2), wait_window_days: 14, next_action_at: null,
    web_tech_stack: ["Figma", "Webflow", "Notion", "Monday.com"],
    places_name: "Creativa Studios BCN", places_rating: 4.8, places_user_ratings_total: 95,
    places_types: ["Creative Agency", "Design"], places_website: "https://creativa.es",
    places_phone: "+34 933 222 111", places_address: "Passeig de Gràcia 50, Barcelona",
    created_at: ago(12), updated_at: ago(1),
  },
  {
    id: "l9", contacto_id: null, linkedin_url: "https://linkedin.com/in/miguelangel",
    full_name: "Miguel Ángel López", title: "CEO", company: "FoodTech Spain", location: "Madrid, Spain",
    pack_candidate: "FORTALEZA", segment: "B_>200reviews", status: "GHOSTED", lead_score: 75,
    score_breakdown: { fit_icp: 30, web_signals: 25, places_signals: 20 },
    invite_sent_at: ago(30), accepted_at: ago(25), wait_window_days: 14, next_action_at: null,
    web_tech_stack: ["AWS", "React", "Node.js"],
    places_name: "FoodTech Spain", places_rating: 4.0, places_user_ratings_total: 520,
    places_types: ["Food Tech", "Restaurant Tech"], places_website: "https://foodtech.es",
    places_phone: "+34 915 666 777", places_address: "Gran Vía 28, Madrid",
    created_at: ago(35), updated_at: ago(5),
  },
  {
    id: "l10", contacto_id: null, linkedin_url: "https://linkedin.com/in/sofiaalvarez",
    full_name: "Sofía Álvarez", title: "Propietaria", company: "Estética Sofía", location: "Zaragoza, Spain",
    pack_candidate: "GUARDIAN", segment: "A_<50reviews", status: "INVITE_SENT", lead_score: 62,
    score_breakdown: { fit_icp: 28, web_signals: 14, places_signals: 20 },
    invite_sent_at: ago(4), accepted_at: null, wait_window_days: 14, next_action_at: ago(-10),
    web_tech_stack: ["WordPress"],
    places_name: "Estética Sofía", places_rating: 4.9, places_user_ratings_total: 28,
    places_types: ["Beauty Salon"], places_website: "https://esteticasofia.es",
    places_phone: "+34 976 333 444", places_address: "Calle Alfonso I 20, Zaragoza",
    created_at: ago(6), updated_at: ago(4),
  },
];

export const MOCK_CONVERSATIONS: LinkedInConversation[] = [
  {
    id: "c1", linkedin_lead_id: "l1", direction: "SENT", sent_by: "USER",
    message_text: "Hola Juan, vi que Acme está creciendo bien. Me imagino que con tantas herramientas SaaS (HubSpot, Zapier...) el tema de conectar todo puede ser un dolor. ¿Cómo lo están manejando?",
    sent_at: ago(2), sentiment: null, intent: null,
  },
  {
    id: "c2", linkedin_lead_id: "l1", direction: "RECEIVED", sent_by: "Juan Pérez",
    message_text: "Hola! Sí, exactamente ese es nuestro problema. Tenemos muchas herramientas pero todo está desconectado. ¿Qué hacéis vosotros al respecto?",
    sent_at: ago(1), sentiment: "POSITIVE", intent: "INTERESTED",
  },
  {
    id: "c3", linkedin_lead_id: "l1", direction: "SENT", sent_by: "USER",
    message_text: "Ayudamos a agencias como la vuestra a que todo funcione como un reloj sin necesidad de CTO full-time. Te puedo enseñar cómo lo hacemos. ¿Te va bien una sesión de 20 min esta semana?",
    sent_at: ago(0.75), sentiment: null, intent: null,
  },
  {
    id: "c4", linkedin_lead_id: "l3", direction: "SENT", sent_by: "USER",
    message_text: "Hola Carlos, veo que LogiTrans gestiona operaciones bastante críticas. Si la infra cae, el negocio se para, ¿no? ¿Cómo lo tenéis montado?",
    sent_at: ago(5), sentiment: null, intent: null,
  },
  {
    id: "c5", linkedin_lead_id: "l3", direction: "RECEIVED", sent_by: "Carlos Ruiz",
    message_text: "Exacto, somos muy dependientes de la infraestructura. Usamos Azure pero no tenemos un equipo dedicado. Es un punto débil que sabemos que tenemos.",
    sent_at: ago(4), sentiment: "POSITIVE", intent: "INTERESTED",
  },
];

export const MOCK_DASHBOARD = {
  kpis: {
    total_invites: 47,
    acceptances: 12,
    acceptance_rate: 0.26,
    in_conversation: 5,
    booked: 2,
    booking_rate: 0.17,
  },
  by_pack: {
    GUARDIAN: { leads: 18, accepted: 4, booked: 1 },
    MOTOR: { leads: 22, accepted: 6, booked: 1 },
    FORTALEZA: { leads: 7, accepted: 2, booked: 0 },
  },
  segments: [
    { segment: "A_<50reviews", invites: 12, accepted: 4, rate: 0.33 },
    { segment: "B_>200reviews", invites: 10, accepted: 2, rate: 0.20 },
    { segment: "Pack2_Services_BCN", invites: 15, accepted: 4, rate: 0.27 },
  ],
  recent_activity: [
    { text: "Lead Juan Pérez aceptó invitación (MOTOR)", time: ago(0.08) },
    { text: "Draft aprobado para Elena Fernández", time: ago(0.21) },
    { text: "Booked call - Pedro Sánchez (FORTALEZA)", time: ago(1) },
    { text: "Lead Sofía Álvarez importada (GUARDIAN)", time: ago(4) },
    { text: "Carlos Ruiz respondió mensaje (FORTALEZA)", time: ago(0.5) },
  ],
};

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

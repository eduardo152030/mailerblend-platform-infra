const BASE_URL = "/_svc/v1";

export interface PaginatedResponse<T = Record<string, unknown>> {
  items: T[];
  limit: number;
  offset: number;
  count: number;
  total: number;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json();
}

function qs(params: Record<string, unknown>): string {
  const s = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") s.append(k, String(v));
  });
  const str = s.toString();
  return str ? `?${str}` : "";
}

// Contacts
export const contacts = {
  list: (p: {
    limit?: number; offset?: number; q?: string;
    estado?: string; origen?: string; pack_asignado?: string;
    tipo_empresa?: string; lead_score_min?: number; lead_score_max?: number;
  } = {}) =>
    request<PaginatedResponse>(`/contacts${qs(p)}`),
  get: (id: string) => request<Record<string, unknown>>(`/contacts/${id}`),
  create: (data: Record<string, unknown>) =>
    request<Record<string, unknown>>(`/contacts`, { method: "POST", body: JSON.stringify(data) }),
  snapshot: (id: string) => request<Record<string, unknown>>(`/contacts/${id}/snapshot`),
};

// Oportunidades
export const oportunidades = {
  list: (p: {
    limit?: number; offset?: number; q?: string;
    estado?: string; lead_tag?: string; prioridad?: string; pack?: string;
    owner?: string; next_action?: string; urgencia?: string;
  } = {}) =>
    request<PaginatedResponse>(`/oportunidades${qs(p)}`),
  get: (id: string) => request<Record<string, unknown>>(`/oportunidades/${id}`),
  snapshot: (id: string) => request<Record<string, unknown>>(`/oportunidades/${id}/snapshot`),
  patch: (id: string, data: Record<string, unknown>) =>
    request<Record<string, unknown>>(`/oportunidades/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
};

// Pendientes
export const pendientes = {
  list: (p: {
    limit?: number; offset?: number; q?: string;
    status?: string; priority?: string; assigned_to?: string;
    contacto_id?: string; oportunidad_id?: string;
  } = {}) =>
    request<PaginatedResponse>(`/pendientes${qs(p)}`),
  get: (id: string) => request<Record<string, unknown>>(`/pendientes/${id}`),
  create: (data: Record<string, unknown>) =>
    request<Record<string, unknown>>(`/pendientes`, { method: "POST", body: JSON.stringify(data) }),
  patch: (id: string, data: Record<string, unknown>) =>
    request<Record<string, unknown>>(`/pendientes/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  allowedValues: () =>
    request<{ status: string[]; priority: string[] }>(`/pendientes/metadata/allowed-values`),
};

// Presupuestos
export const presupuestos = {
  list: (p: {
    limit?: number; offset?: number; q?: string;
    status?: string; contacto_id?: string; oportunidad_id?: string;
    valid_until_before?: string;
  } = {}) =>
    request<PaginatedResponse>(`/presupuestos${qs(p)}`),
  get: (id: string) => request<Record<string, unknown>>(`/presupuestos/${id}`),
  create: (data: Record<string, unknown>) =>
    request<Record<string, unknown>>(`/presupuestos`, { method: "POST", body: JSON.stringify(data) }),
  patch: (id: string, data: Record<string, unknown>) =>
    request<Record<string, unknown>>(`/presupuestos/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
};

// Gastos
export const gastos = {
  list: (p: {
    limit?: number; offset?: number; q?: string;
    categoria?: string; estado?: string; proveedor_id?: string;
    project_key?: string; from?: string; to?: string;
  } = {}) =>
    request<PaginatedResponse>(`/gastos${qs(p)}`),
  get: (id: string) => request<Record<string, unknown>>(`/gastos/${id}`),
  create: (data: Record<string, unknown>) =>
    request<Record<string, unknown>>(`/gastos`, { method: "POST", body: JSON.stringify(data) }),
  patch: (id: string, data: Record<string, unknown>) =>
    request<Record<string, unknown>>(`/gastos/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  stats: (p: { group_by?: string; from?: string; to?: string; project_key?: string } = {}) =>
    request<{ group_by: string; items: Record<string, unknown>[] }>(`/gastos/stats${qs(p)}`),
  stats2: (p: { group_by?: string; from?: string; to?: string; project_key?: string } = {}) =>
    request<{ group_by: string; items: Record<string, unknown>[] }>(`/gastos/stats2${qs(p)}`),
  statsTimeseries: (p: { bucket?: string; from?: string; to?: string; project_key?: string } = {}) =>
    request<{ bucket: string; items: Record<string, unknown>[] }>(`/gastos/stats-timeseries${qs(p)}`),
  taxSummary: (p: { from: string; to: string }) =>
    request<Record<string, unknown>>(`/gastos/tax-summary${qs(p)}`),
  pnlMonthly: (p: { from?: string; to?: string } = {}) =>
    request<{ items: Record<string, unknown>[] }>(`/gastos/pnl-monthly${qs(p)}`),
  pnlSummary: (p: { from?: string; to?: string } = {}) =>
    request<Record<string, unknown>>(`/gastos/pnl-summary${qs(p)}`),
  statsSummary: (p: { from?: string; to?: string } = {}) =>
    request<Record<string, unknown>>(`/gastos/stats-summary${qs(p)}`),
  exportCsv: (p: Record<string, unknown> = {}) =>
    `${BASE_URL}/gastos/export.csv${qs(p)}`,
};

// Proveedores
export const proveedores = {
  list: (p: { limit?: number; offset?: number; q?: string; tipo?: string } = {}) =>
    request<PaginatedResponse>(`/proveedores${qs(p)}`),
  get: (id: string) => request<Record<string, unknown>>(`/proveedores/${id}`),
  create: (data: Record<string, unknown>) =>
    request<Record<string, unknown>>(`/proveedores`, { method: "POST", body: JSON.stringify(data) }),
  patch: (id: string, data: Record<string, unknown>) =>
    request<Record<string, unknown>>(`/proveedores/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
};

// Timeline
export const timeline = {
  list: (p: {
    contacto_id?: string; oportunidad_id?: string;
    limit?: number; offset?: number;
    type?: string; q?: string; since?: string; until?: string;
  } = {}) =>
    request<PaginatedResponse>(`/timeline${qs(p)}`),
};

// UTM
export const utm = {
  list: (p: {
    limit?: number; offset?: number; q?: string;
    contacto_id?: string; utm_campaign?: string; utm_source?: string;
    utm_medium?: string; ads_platform?: string; device?: string;
    created_from?: string; created_to?: string;
  } = {}) =>
    request<PaginatedResponse>(`/utm${qs(p)}`),
  get: (id: string) => request<Record<string, unknown>>(`/utm/${id}`),
  stats: (p: { group_by?: string; created_from?: string; created_to?: string; ads_platform?: string } = {}) =>
    request<{ group_by: string; items: Record<string, unknown>[] }>(`/utm/stats${qs(p)}`),
  stats2: (p: { group_by?: string; created_from?: string; created_to?: string; ads_platform?: string } = {}) =>
    request<{ group_by: string; items: Record<string, unknown>[] }>(`/utm/stats2${qs(p)}`),
  statsConversions: (p: { group_by?: string; created_from?: string; created_to?: string } = {}) =>
    request<{ group_by: string; items: Record<string, unknown>[] }>(`/utm/stats-conversions${qs(p)}`),
};

// Conversiones Offline
export const conversionesOffline = {
  list: (p: {
    limit?: number; offset?: number;
    sync_status?: string; platform?: string; event_name?: string;
    from?: string; to?: string;
  } = {}) =>
    request<PaginatedResponse>(`/conversiones-offline${qs(p)}`),
  get: (id: string) => request<Record<string, unknown>>(`/conversiones-offline/${id}`),
  retry: (id: string) =>
    request<Record<string, unknown>>(`/conversiones-offline/${id}/retry`, { method: "POST" }),
  stats: (p: { from?: string; to?: string } = {}) =>
    request<{ items: Record<string, unknown>[] }>(`/conversiones-offline/stats${qs(p)}`),
};

// LinkedIn Sourcing
export const linkedinSourcing = {
  // Leads
  leads: {
    list: (p: {
      limit?: number; offset?: number; q?: string;
      status?: string; pack_candidate?: string; segment?: string;
      min_score?: number; max_score?: number;
    } = {}) =>
      request<PaginatedResponse>(`/linkedin-sourcing/leads${qs(p)}`),
    get: (id: string) => request<Record<string, unknown>>(`/linkedin-sourcing/leads/${id}`),
    snapshot: (id: string) => request<Record<string, unknown>>(`/linkedin-sourcing/leads/${id}/snapshot`),
    patch: (id: string, data: Record<string, unknown>) =>
      request<Record<string, unknown>>(`/linkedin-sourcing/leads/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    import: (data: { leads: Record<string, unknown>[]; auto_classify?: boolean }) =>
      request<{ total_imported: number; successful: number; failed: number; duplicates: number; errors: string[]; imported_ids: string[] }>(
        `/linkedin-sourcing/leads/import`, { method: "POST", body: JSON.stringify(data) }
      ),
    delete: (id: string) =>
      request<void>(`/linkedin-sourcing/leads/${id}`, { method: "DELETE" }),
    stats: (p: Record<string, unknown> = {}) =>
      request<Record<string, unknown>>(`/linkedin-sourcing/leads/stats${qs(p)}`),
    attempts: (id: string) =>
      request<PaginatedResponse>(`/linkedin-sourcing/leads/${id}/attempts`),
    conversations: (id: string, p: { limit?: number } = {}) =>
      request<PaginatedResponse>(`/linkedin-sourcing/leads/${id}/conversations${qs(p)}`),
  },
  // Approvals
  approvals: {
    list: (p: { limit?: number; offset?: number; pending_only?: boolean; lead_id?: string } = {}) =>
      request<PaginatedResponse>(`/linkedin-sourcing/approvals${qs(p)}`),
    get: (id: string) => request<Record<string, unknown>>(`/linkedin-sourcing/approvals/${id}`),
    create: (data: Record<string, unknown>) =>
      request<Record<string, unknown>>(`/linkedin-sourcing/approvals`, { method: "POST", body: JSON.stringify(data) }),
    approve: (id: string, data: Record<string, unknown>) =>
      request<Record<string, unknown>>(`/linkedin-sourcing/approvals/${id}/approve`, { method: "POST", body: JSON.stringify(data) }),
    reject: (id: string, data: Record<string, unknown>) =>
      request<Record<string, unknown>>(`/linkedin-sourcing/approvals/${id}/reject`, { method: "POST", body: JSON.stringify(data) }),
    feedbackStats: (p: { days?: number } = {}) =>
      request<Record<string, unknown>>(`/linkedin-sourcing/approvals/stats/feedback${qs(p)}`),
  },
  // Conversations
  conversations: {
    create: (data: Record<string, unknown>) =>
      request<Record<string, unknown>>(`/linkedin-sourcing/conversations`, { method: "POST", body: JSON.stringify(data) }),
  },
  // Outcomes
  outcomes: {
    list: (p: { limit?: number; offset?: number; outcome?: string; lead_id?: string; days?: number } = {}) =>
      request<PaginatedResponse>(`/linkedin-sourcing/outcomes${qs(p)}`),
    create: (data: Record<string, unknown>) =>
      request<Record<string, unknown>>(`/linkedin-sourcing/outcomes`, { method: "POST", body: JSON.stringify(data) }),
  },
  // Dashboard
  dashboard: (p: { days?: number } = {}) =>
    request<Record<string, unknown>>(`/linkedin-sourcing/dashboard${qs(p)}`),
  // Knowledge Base
  knowledgeBase: {
    list: (p: { category?: string; target_pack?: string; limit?: number; offset?: number } = {}) =>
      request<PaginatedResponse>(`/linkedin-sourcing/knowledge-base${qs(p)}`),
    context: (pack: string, p: { categories?: string } = {}) =>
      request<Record<string, unknown>>(`/linkedin-sourcing/knowledge-base/context/${pack}${qs(p)}`),
    create: (data: Record<string, unknown>) =>
      request<Record<string, unknown>>(`/linkedin-sourcing/knowledge-base`, { method: "POST", body: JSON.stringify(data) }),
    patch: (id: string, data: Record<string, unknown>) =>
      request<Record<string, unknown>>(`/linkedin-sourcing/knowledge-base/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    delete: (id: string) =>
      request<void>(`/linkedin-sourcing/knowledge-base/${id}`, { method: "DELETE" }),
  },
  // Rate Limits
  rateLimits: {
    currentStatus: () =>
      request<Record<string, unknown>>(`/linkedin-sourcing/rate-limits/current/status`),
    list: () =>
      request<{ items: Record<string, unknown>[] }>(`/linkedin-sourcing/rate-limits`),
    patch: (limitType: string, data: Record<string, unknown>) =>
      request<Record<string, unknown>>(`/linkedin-sourcing/rate-limits/${limitType}`, { method: "PATCH", body: JSON.stringify(data) }),
  },
  // Activity Log
  activityLog: {
    statsToday: () =>
      request<Record<string, unknown>>(`/linkedin-sourcing/activity-log/stats/today`),
    statsDaily: (p: { days?: number } = {}) =>
      request<Record<string, unknown>>(`/linkedin-sourcing/activity-log/stats/daily${qs(p)}`),
    list: (p: { hours?: number; limit?: number; offset?: number } = {}) =>
      request<PaginatedResponse>(`/linkedin-sourcing/activity-log${qs(p)}`),
  },
  // Cooldowns
  cooldowns: {
    status: () =>
      request<Record<string, unknown>>(`/linkedin-sourcing/cooldowns/status`),
    list: (p: { limit?: number } = {}) =>
      request<PaginatedResponse>(`/linkedin-sourcing/cooldowns${qs(p)}`),
    create: (data: Record<string, unknown>) =>
      request<Record<string, unknown>>(`/linkedin-sourcing/cooldowns`, { method: "POST", body: JSON.stringify(data) }),
  },
  // Invite Templates
  inviteTemplates: {
    list: (p: { limit?: number; offset?: number; is_active?: boolean; target_pack?: string } = {}) =>
      request<PaginatedResponse>(`/linkedin-sourcing/invite-templates${qs(p)}`),
    get: (id: string) => request<Record<string, unknown>>(`/linkedin-sourcing/invite-templates/${id}`),
    create: (data: Record<string, unknown>) =>
      request<Record<string, unknown>>(`/linkedin-sourcing/invite-templates`, { method: "POST", body: JSON.stringify(data) }),
    patch: (id: string, data: Record<string, unknown>) =>
      request<Record<string, unknown>>(`/linkedin-sourcing/invite-templates/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  },
};

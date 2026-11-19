import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as api from "@/lib/api";

export function useContacts(params: Parameters<typeof api.contacts.list>[0] = {}) {
  return useQuery({
    queryKey: ["contacts", params],
    queryFn: () => api.contacts.list(params),
  });
}

export function useContactSnapshot(id: string | null) {
  return useQuery({
    queryKey: ["contact-snapshot", id],
    queryFn: () => api.contacts.snapshot(id!),
    enabled: !!id,
  });
}

export function useCreateContact() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) => api.contacts.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["contacts"] });
      qc.invalidateQueries({ queryKey: ["contact-snapshot"] });
    },
  });
}

export function useOportunidades(params: Parameters<typeof api.oportunidades.list>[0] = {}) {
  return useQuery({
    queryKey: ["oportunidades", params],
    queryFn: () => api.oportunidades.list(params),
  });
}

export function useOportunidadSnapshot(id: string | null) {
  return useQuery({
    queryKey: ["oportunidad-snapshot", id],
    queryFn: () => api.oportunidades.snapshot(id!),
    enabled: !!id,
  });
}

export function usePatchOportunidad() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      api.oportunidades.patch(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["oportunidades"] });
      qc.invalidateQueries({ queryKey: ["oportunidad-snapshot"] });
    },
  });
}

export function usePendientes(params: Parameters<typeof api.pendientes.list>[0] = {}) {
  return useQuery({
    queryKey: ["pendientes", params],
    queryFn: () => api.pendientes.list(params),
  });
}

export function useCreatePendiente() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) => api.pendientes.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["pendientes"] });
      qc.invalidateQueries({ queryKey: ["oportunidad-snapshot"] });
    },
  });
}

export function usePatchPendiente() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      api.pendientes.patch(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["pendientes"] });
      qc.invalidateQueries({ queryKey: ["oportunidad-snapshot"] });
    },
  });
}

export function usePresupuestos(params: Parameters<typeof api.presupuestos.list>[0] = {}) {
  return useQuery({
    queryKey: ["presupuestos", params],
    queryFn: () => api.presupuestos.list(params),
  });
}

export function useCreatePresupuesto() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) => api.presupuestos.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["presupuestos"] });
      qc.invalidateQueries({ queryKey: ["oportunidad-snapshot"] });
    },
  });
}

export function usePatchPresupuesto() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      api.presupuestos.patch(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["presupuestos"] });
      qc.invalidateQueries({ queryKey: ["oportunidad-snapshot"] });
    },
  });
}

export function useGastos(params: Parameters<typeof api.gastos.list>[0] = {}) {
  return useQuery({
    queryKey: ["gastos", params],
    queryFn: () => api.gastos.list(params),
  });
}

export function useGastosStats2(params: Parameters<typeof api.gastos.stats2>[0] = {}) {
  return useQuery({
    queryKey: ["gastos-stats2", params],
    queryFn: () => api.gastos.stats2(params),
  });
}

export function useGastosStats(params: Parameters<typeof api.gastos.stats>[0] = {}) {
  return useQuery({
    queryKey: ["gastos-stats", params],
    queryFn: () => api.gastos.stats(params),
  });
}

export function useGastosTimeseries(params: Parameters<typeof api.gastos.statsTimeseries>[0] = {}) {
  return useQuery({
    queryKey: ["gastos-timeseries", params],
    queryFn: () => api.gastos.statsTimeseries(params),
  });
}

export function useGastosTaxSummary(params: Parameters<typeof api.gastos.taxSummary>[0]) {
  return useQuery({
    queryKey: ["gastos-tax-summary", params],
    queryFn: () => api.gastos.taxSummary(params),
    enabled: !!(params.from && params.to),
  });
}

export function useGastosPnlMonthly(params: Parameters<typeof api.gastos.pnlMonthly>[0] = {}) {
  return useQuery({
    queryKey: ["gastos-pnl-monthly", params],
    queryFn: () => api.gastos.pnlMonthly(params),
  });
}

export function useGastosPnlSummary(params: Parameters<typeof api.gastos.pnlSummary>[0] = {}) {
  return useQuery({
    queryKey: ["gastos-pnl-summary", params],
    queryFn: () => api.gastos.pnlSummary(params),
  });
}

export function useCreateGasto() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) => api.gastos.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["gastos"] });
      qc.invalidateQueries({ queryKey: ["gastos-stats2"] });
    },
  });
}

export function usePatchGasto() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      api.gastos.patch(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["gastos"] });
      qc.invalidateQueries({ queryKey: ["gastos-stats2"] });
    },
  });
}

export function useProveedores(params: Parameters<typeof api.proveedores.list>[0] = {}) {
  return useQuery({
    queryKey: ["proveedores", params],
    queryFn: () => api.proveedores.list(params),
  });
}

export function useCreateProveedor() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) => api.proveedores.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["proveedores"] }),
  });
}

export function usePatchProveedor() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      api.proveedores.patch(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["proveedores"] }),
  });
}

export function useTimeline(params: Parameters<typeof api.timeline.list>[0] = {}) {
  return useQuery({
    queryKey: ["timeline", params],
    queryFn: () => api.timeline.list(params),
    enabled: !!(params.contacto_id || params.oportunidad_id),
  });
}

export function useUtm(params: Parameters<typeof api.utm.list>[0] = {}) {
  return useQuery({
    queryKey: ["utm", params],
    queryFn: () => api.utm.list(params),
  });
}

export function useUtmStats(params: Parameters<typeof api.utm.stats>[0] = {}) {
  return useQuery({
    queryKey: ["utm-stats", params],
    queryFn: () => api.utm.stats(params),
  });
}

export function useUtmStats2(params: Parameters<typeof api.utm.stats2>[0] = {}) {
  return useQuery({
    queryKey: ["utm-stats2", params],
    queryFn: () => api.utm.stats2(params),
  });
}

export function useUtmStatsConversions(params: Parameters<typeof api.utm.statsConversions>[0] = {}) {
  return useQuery({
    queryKey: ["utm-stats-conversions", params],
    queryFn: () => api.utm.statsConversions(params),
  });
}

export function useUtmDetail(id: string | null) {
  return useQuery({
    queryKey: ["utm-detail", id],
    queryFn: () => api.utm.get(id!),
    enabled: !!id,
  });
}

// Conversiones Offline
export function useConversionesOffline(params: Parameters<typeof api.conversionesOffline.list>[0] = {}) {
  return useQuery({
    queryKey: ["conversiones-offline", params],
    queryFn: () => api.conversionesOffline.list(params),
  });
}

export function useConversionOfflineDetail(id: string | null) {
  return useQuery({
    queryKey: ["conversion-offline-detail", id],
    queryFn: () => api.conversionesOffline.get(id!),
    enabled: !!id,
  });
}

export function useConversionesOfflineStats(params: Parameters<typeof api.conversionesOffline.stats>[0] = {}) {
  return useQuery({
    queryKey: ["conversiones-offline-stats", params],
    queryFn: () => api.conversionesOffline.stats(params),
  });
}

export function useRetryConversion() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.conversionesOffline.retry(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["conversiones-offline"] });
      qc.invalidateQueries({ queryKey: ["conversiones-offline-stats"] });
    },
  });
}

// LinkedIn Sourcing
export function useLSSLeads(params: Parameters<typeof api.linkedinSourcing.leads.list>[0] = {}) {
  return useQuery({
    queryKey: ["lss-leads", params],
    queryFn: () => api.linkedinSourcing.leads.list(params),
  });
}

export function useLSSLeadsStats() {
  return useQuery({
    queryKey: ["lss-leads-stats"],
    queryFn: () => api.linkedinSourcing.leads.stats(),
  });
}

export function useLSSLeadSnapshot(id: string | null) {
  return useQuery({
    queryKey: ["lss-lead-snapshot", id],
    queryFn: () => api.linkedinSourcing.leads.snapshot(id!),
    enabled: !!id,
  });
}

export function useLSSLeadConversations(id: string | null) {
  return useQuery({
    queryKey: ["lss-lead-conversations", id],
    queryFn: () => api.linkedinSourcing.leads.conversations(id!),
    enabled: !!id,
  });
}

export function useLSSPatchLead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      api.linkedinSourcing.leads.patch(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["lss-leads"] });
      qc.invalidateQueries({ queryKey: ["lss-lead-snapshot"] });
      qc.invalidateQueries({ queryKey: ["lss-dashboard"] });
    },
  });
}

export function useLSSImportLeads() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { leads: Record<string, unknown>[]; auto_classify?: boolean }) =>
      api.linkedinSourcing.leads.import(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["lss-leads"] });
      qc.invalidateQueries({ queryKey: ["lss-dashboard"] });
    },
  });
}

export function useLSSDashboard(params: { days?: number } = {}) {
  return useQuery({
    queryKey: ["lss-dashboard", params],
    queryFn: () => api.linkedinSourcing.dashboard(params),
  });
}

export function useLSSCreateConversation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) =>
      api.linkedinSourcing.conversations.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["lss-lead-conversations"] });
      qc.invalidateQueries({ queryKey: ["lss-leads"] });
    },
  });
}

export function useLSSApprovals(params: Parameters<typeof api.linkedinSourcing.approvals.list>[0] = {}) {
  return useQuery({
    queryKey: ["lss-approvals", params],
    queryFn: () => api.linkedinSourcing.approvals.list(params),
  });
}

export function useLSSApproveApproval() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      api.linkedinSourcing.approvals.approve(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["lss-approvals"] });
      qc.invalidateQueries({ queryKey: ["lss-lead-snapshot"] });
      qc.invalidateQueries({ queryKey: ["lss-lead-conversations"] });
    },
  });
}

export function useLSSRejectApproval() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      api.linkedinSourcing.approvals.reject(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["lss-approvals"] });
      qc.invalidateQueries({ queryKey: ["lss-lead-snapshot"] });
    },
  });
}

export function useLSSOutcomes(params: Parameters<typeof api.linkedinSourcing.outcomes.list>[0] = {}) {
  return useQuery({
    queryKey: ["lss-outcomes", params],
    queryFn: () => api.linkedinSourcing.outcomes.list(params),
  });
}

export function useLSSCreateOutcome() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) =>
      api.linkedinSourcing.outcomes.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["lss-leads"] });
      qc.invalidateQueries({ queryKey: ["lss-lead-snapshot"] });
      qc.invalidateQueries({ queryKey: ["lss-dashboard"] });
      qc.invalidateQueries({ queryKey: ["lss-outcomes"] });
    },
  });
}

export function useLSSDeleteLead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.linkedinSourcing.leads.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["lss-leads"] });
      qc.invalidateQueries({ queryKey: ["lss-dashboard"] });
    },
  });
}

// Knowledge Base
export function useLSSKnowledgeBase(params: { category?: string; target_pack?: string; limit?: number } = {}) {
  return useQuery({
    queryKey: ["lss-knowledge-base", params],
    queryFn: () => api.linkedinSourcing.knowledgeBase.list(params),
  });
}

export function useLSSCreateKBEntry() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) => api.linkedinSourcing.knowledgeBase.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["lss-knowledge-base"] }),
  });
}

export function useLSSPatchKBEntry() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      api.linkedinSourcing.knowledgeBase.patch(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["lss-knowledge-base"] }),
  });
}

export function useLSSDeleteKBEntry() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.linkedinSourcing.knowledgeBase.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["lss-knowledge-base"] }),
  });
}

// Rate Limits
export function useLSSRateLimitStatus() {
  return useQuery({
    queryKey: ["lss-rate-limit-status"],
    queryFn: () => api.linkedinSourcing.rateLimits.currentStatus(),
  });
}

export function useLSSRateLimits() {
  return useQuery({
    queryKey: ["lss-rate-limits"],
    queryFn: () => api.linkedinSourcing.rateLimits.list(),
  });
}

export function useLSSPatchRateLimit() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ limitType, data }: { limitType: string; data: Record<string, unknown> }) =>
      api.linkedinSourcing.rateLimits.patch(limitType, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["lss-rate-limits"] });
      qc.invalidateQueries({ queryKey: ["lss-rate-limit-status"] });
    },
  });
}

// Activity Log
export function useLSSActivityStatsToday() {
  return useQuery({
    queryKey: ["lss-activity-stats-today"],
    queryFn: () => api.linkedinSourcing.activityLog.statsToday(),
  });
}

export function useLSSActivityStatsDaily(params: { days?: number } = {}) {
  return useQuery({
    queryKey: ["lss-activity-stats-daily", params],
    queryFn: () => api.linkedinSourcing.activityLog.statsDaily(params),
  });
}

export function useLSSActivityLog(params: { hours?: number; limit?: number } = {}) {
  return useQuery({
    queryKey: ["lss-activity-log", params],
    queryFn: () => api.linkedinSourcing.activityLog.list(params),
  });
}

// Cooldowns
export function useLSSCooldownStatus() {
  return useQuery({
    queryKey: ["lss-cooldown-status"],
    queryFn: () => api.linkedinSourcing.cooldowns.status(),
  });
}

export function useLSSCooldowns(params: { limit?: number } = {}) {
  return useQuery({
    queryKey: ["lss-cooldowns", params],
    queryFn: () => api.linkedinSourcing.cooldowns.list(params),
  });
}

export function useLSSCreateCooldown() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) => api.linkedinSourcing.cooldowns.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["lss-cooldown-status"] });
      qc.invalidateQueries({ queryKey: ["lss-cooldowns"] });
    },
  });
}

// Invite Templates
export function useLSSInviteTemplates(params: { is_active?: boolean; target_pack?: string; limit?: number } = {}) {
  return useQuery({
    queryKey: ["lss-invite-templates", params],
    queryFn: () => api.linkedinSourcing.inviteTemplates.list(params),
  });
}

export function useLSSCreateInviteTemplate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) => api.linkedinSourcing.inviteTemplates.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["lss-invite-templates"] }),
  });
}

export function useLSSPatchInviteTemplate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      api.linkedinSourcing.inviteTemplates.patch(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["lss-invite-templates"] }),
  });
}

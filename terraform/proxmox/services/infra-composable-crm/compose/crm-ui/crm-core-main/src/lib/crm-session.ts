import { createClient } from "@supabase/supabase-js";

const anonKey = import.meta.env.VITE_CRM_AUTH_ANON_KEY;

export const crmSession = anonKey
  ? createClient(window.location.origin, anonKey, {
      auth: { persistSession: false, autoRefreshToken: true, detectSessionInUrl: false },
    })
  : null;

export async function crmFetch(path: string, options?: RequestInit) {
  const headers = new Headers(options?.headers);
  if (crmSession) {
    const { data } = await crmSession.auth.getSession();
    if (!data.session) throw new Error("Inicia sesión para consultar CRMAPI.");
    headers.set("Authorization", `Bearer ${data.session.access_token}`);
  }
  return fetch(path, { ...options, headers, redirect: "error" });
}

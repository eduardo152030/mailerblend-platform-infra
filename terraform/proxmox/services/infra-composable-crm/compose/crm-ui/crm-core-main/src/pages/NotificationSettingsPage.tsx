import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { crmFetch } from "@/lib/crm-session";

const endpoint = "/_svc/v1/notifications";
type Preferences = { enabled: boolean; recipients: string[] };

export default function NotificationSettingsPage() {
  const [enabled, setEnabled] = useState(false);
  const [recipients, setRecipients] = useState("");
  const [ready, setReady] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    async function load() {
      try {
        const response = await crmFetch(endpoint, { signal: controller.signal });
        if (!response.ok) throw new Error();
        const preferences: Preferences = await response.json();
        setEnabled(preferences.enabled);
        setRecipients(preferences.recipients.join("\n"));
        setReady(true);
      } catch {
        if (!controller.signal.aborted) setMessage("No se pudo acceder a la configuración de notificaciones.");
      }
    }
    void load();
    return () => controller.abort();
  }, []);

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setMessage("");
    try {
      const response = await crmFetch(endpoint, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled, recipients: recipients.split("\n").map(email => email.trim()).filter(Boolean) }),
      });
      if (!response.ok) {
        setMessage(response.status === 422
          ? "Revisa las direcciones. Puedes guardar hasta 25 destinatarios y necesitas al menos uno si el aviso está activo."
          : "No se pudo guardar la configuración.");
        return;
      }
      const preferences: Preferences = await response.json();
      setRecipients(preferences.recipients.join("\n"));
      setMessage("Configuración guardada.");
    } catch {
      setMessage("No se pudo guardar la configuración.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="mx-auto max-w-xl space-y-5 p-6">
      <h1 className="text-2xl font-semibold">Notificaciones</h1>
      {ready && (
        <form className="space-y-4" onSubmit={save}>
          <fieldset className="space-y-4" disabled={saving}>
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={enabled} onChange={event => setEnabled(event.target.checked)} />
              Avisar cuando se crea un contacto
            </label>
            <label className="block">
              Destinatarios, uno por línea
              <textarea className="mt-1 block w-full rounded border bg-background p-2" rows={6}
                value={recipients} onChange={event => setRecipients(event.target.value)} />
            </label>
            <button className="rounded bg-primary px-4 py-2 text-primary-foreground" type="submit">
              {saving ? "Guardando…" : "Guardar"}
            </button>
          </fieldset>
        </form>
      )}
      <p role="status">{message}</p>
    </section>
  );
}

import { useState } from "react";
import { Link } from "react-router-dom";
import { crmSession } from "@/lib/crm-session";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function RequestPasswordResetPage() {
  const [email, setEmail] = useState("");
  const [sending, setSending] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  return (
    <main className="mx-auto max-w-md space-y-4 p-6">
      <h1 className="text-2xl font-semibold">Recuperar contraseña</h1>
      {submitted ? <p role="status">Si la cuenta existe, recibirás un correo con un enlace para restablecer la contraseña.</p> : (
        <form className="space-y-3" onSubmit={async event => {
          event.preventDefault();
          setSending(true);
          try {
            await crmSession?.auth.resetPasswordForEmail(email, { redirectTo: window.location.origin + "/restablecer" });
          } catch {
            // Keep the response generic whether or not the account exists.
          } finally {
            setSubmitted(true);
            setSending(false);
          }
        }}>
          <label htmlFor="recovery-email">Correo electrónico</label>
          <Input id="recovery-email" type="email" autoComplete="email" required value={email}
            onChange={event => setEmail(event.target.value)} />
          <Button type="submit" disabled={sending || !crmSession}>Enviar enlace</Button>
        </form>
      )}
      <Link to="/" className="underline">Volver al inicio de sesión</Link>
    </main>
  );
}

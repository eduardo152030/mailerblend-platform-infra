import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { crmSession } from "@/lib/crm-session";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

function recoverySession() {
  const parameters = new URLSearchParams(window.location.hash.slice(1));
  const access_token = parameters.get("access_token");
  const refresh_token = parameters.get("refresh_token");
  return parameters.get("type") === "recovery" && access_token && refresh_token
    ? { access_token, refresh_token }
    : null;
}

export default function UpdatePasswordPage() {
  const [recovery] = useState(recoverySession);
  useEffect(() => {
    if (window.location.hash) window.history.replaceState(window.history.state, "", window.location.pathname);
  }, []);
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState(false);
  const [done, setDone] = useState(false);

  return (
    <main className="mx-auto max-w-md space-y-4 p-6">
      <h1 className="text-2xl font-semibold">Restablecer contraseña</h1>
      {recovery && crmSession && !done ? (
        <form className="space-y-3" onSubmit={async event => {
          event.preventDefault();
          setSaving(true);
          setMessage("");
          try {
            const { error: sessionError } = await crmSession.auth.setSession(recovery);
            if (sessionError) throw sessionError;
            try {
              const { error } = await crmSession.auth.updateUser({ password });
              if (error) throw error;
              setPassword("");
              setDone(true);
              setMessage("Contraseña actualizada. Ya puedes iniciar sesión.");
            } finally {
              await crmSession.auth.signOut({ scope: "local" });
            }
          } catch {
            setMessage("No se pudo cambiar la contraseña. Solicita un enlace nuevo si este ha caducado.");
          } finally {
            setSaving(false);
          }
        }}>
          <label htmlFor="new-password">Contraseña nueva</label>
          <Input id="new-password" type="password" required minLength={12} autoComplete="new-password"
            value={password} onChange={event => setPassword(event.target.value)} />
          <Button type="submit" disabled={saving}>Actualizar contraseña</Button>
        </form>
      ) : !done && <p>El enlace no es válido. <Link className="underline" to="/recuperar">Solicita uno nuevo</Link>.</p>}
      <p role="status">{message}</p>
      <Link className="underline" to="/">Volver al inicio de sesión</Link>
    </main>
  );
}

import { useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { ArrowRight, Check, Kanban, Linkedin, Mail, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { crmSession } from "@/lib/crm-session";
import { cn } from "@/lib/utils";

const MODULES = [
  { id: "form_entries", label: "NT_Crm_FormEntries", icon: Users, route: "/dashboard" },
  { id: "gestion_inteligente", label: "Gestión inteligente", icon: Kanban, route: "/gastos" },
  { id: "linkedin_stealth", label: "NT_LinkedIn Stealth Sourcing", icon: Linkedin, route: "/linkedin-sourcing" },
];

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [moduleId, setModuleId] = useState(MODULES[0].id);
  const navigate = useNavigate();
  const location = useLocation();
  const optionRefs = useRef<Array<HTMLButtonElement | null>>([]);

  const handleGroupKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (event.key !== "ArrowDown" && event.key !== "ArrowUp" && event.key !== "ArrowRight" && event.key !== "ArrowLeft") {
      return;
    }
    event.preventDefault();
    const current = MODULES.findIndex((m) => m.id === moduleId);
    const forward = event.key === "ArrowDown" || event.key === "ArrowRight";
    const next = (current + (forward ? 1 : MODULES.length - 1)) % MODULES.length;
    setModuleId(MODULES[next].id);
    optionRefs.current[next]?.focus();
  };

  return (
    <div className="dark login-shell flex min-h-screen w-full items-center justify-center px-4 py-10 text-foreground">
      <div className="w-full max-w-md">
        {/* Brand */}
        <div className="mb-5 flex items-center justify-center gap-2">
          <span className="grid h-8 w-8 shrink-0 place-items-center rounded-md bg-primary text-sm font-bold text-primary-foreground">
            N
          </span>
          <span className="text-sm font-semibold tracking-wide text-foreground/80">
            NovaTech Solutions
          </span>
        </div>

        {/* Access card */}
        <form
          onSubmit={async (event) => {
            event.preventDefault();
            const target = MODULES.find((m) => m.id === moduleId);
            if (!target || submitting) return;
            if (crmSession) {
              setError("");
              setSubmitting(true);
              try {
                const { error: signInError } = await crmSession.auth.signInWithPassword({ email, password });
                if (signInError) {
                  setError("No se pudo iniciar sesión. Comprueba tus credenciales.");
                  return;
                }
              } catch {
                setError("No se pudo conectar con el servicio de acceso.");
                return;
              } finally {
                setSubmitting(false);
              }
            }
            const contact = location.state?.contact;
            const returnsToContact = typeof contact === "string" && /^\?contacto=[a-f0-9-]{36}$/i.test(contact);
            navigate(returnsToContact ? "/contactos" + contact : target.route, { replace: true });
          }}
          className="login-card rounded-xl border border-border bg-card p-6 text-card-foreground sm:p-8"
        >
          <h1 className="text-xl font-bold tracking-tight text-card-foreground sm:text-2xl">
            Accede a tu CRM
          </h1>
          <p className="mt-1.5 text-sm text-muted-foreground">
            Introduce tu correo y elige el módulo con el que quieres trabajar.
          </p>

          <div className="mt-6 space-y-5">
            {/* Email */}
            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium">
                Correo electrónico
              </Label>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  required={Boolean(crmSession)}
                  placeholder="tu@empresa.com"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  className="h-11 pl-9"
                />
              </div>
            </div>

            {crmSession && (
              <div className="space-y-2">
                <Label htmlFor="password">Contraseña</Label>
                <Input id="password" type="password" autoComplete="current-password" required
                  value={password} onChange={(event) => setPassword(event.target.value)} />
              </div>
            )}
            {crmSession && <Link to="/recuperar" className="text-sm underline">¿Olvidaste tu contraseña?</Link>}
            {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
            {/* Module picker */}
            <div className="space-y-2">
              <Label id="module-label" className="text-sm font-medium">
                ¿A qué módulo quieres acceder?
              </Label>
              <div
                role="radiogroup"
                aria-labelledby="module-label"
                onKeyDown={handleGroupKeyDown}
                className="space-y-2"
              >
                {MODULES.map((module, index) => {
                  const selected = module.id === moduleId;
                  const Icon = module.icon;
                  return (
                    <button
                      key={module.id}
                      ref={(node) => {
                        optionRefs.current[index] = node;
                      }}
                      type="button"
                      role="radio"
                      aria-checked={selected}
                      tabIndex={selected ? 0 : -1}
                      onClick={() => setModuleId(module.id)}
                      className={cn(
                        "flex w-full items-center gap-3 rounded-lg border px-3 py-2.5 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-card",
                        selected
                          ? "border-primary bg-primary/10"
                          : "border-border bg-background hover:border-primary/50 hover:bg-accent",
                      )}
                    >
                      <span
                        className={cn(
                          "grid h-8 w-8 shrink-0 place-items-center rounded-md border transition-colors",
                          selected
                            ? "border-primary/40 bg-primary/15 text-primary"
                            : "border-border bg-muted text-muted-foreground",
                        )}
                      >
                        <Icon className="h-4 w-4" />
                      </span>
                      <span
                        className={cn(
                          "truncate text-sm font-medium",
                          selected ? "text-foreground" : "text-muted-foreground",
                        )}
                      >
                        {module.label}
                      </span>
                      <span
                        className={cn(
                          "ml-auto grid h-5 w-5 shrink-0 place-items-center rounded-full border transition-colors",
                          selected
                            ? "border-primary bg-primary text-primary-foreground"
                            : "border-border text-transparent",
                        )}
                        aria-hidden="true"
                      >
                        <Check className="h-3 w-3" strokeWidth={3} />
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Submit */}
            <Button type="submit" disabled={submitting} className="h-11 w-full gap-2 text-sm font-semibold">
              Continuar
              <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
        </form>

        <p className="mt-5 text-center text-xs text-muted-foreground">
          Acceso interno · Solo personal autorizado
        </p>
      </div>
    </div>
  );
}

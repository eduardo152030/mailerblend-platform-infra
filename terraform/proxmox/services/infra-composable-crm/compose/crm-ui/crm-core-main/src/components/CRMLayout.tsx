import { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  Users, Target, CheckSquare, FileText, Receipt, Truck,
  LayoutDashboard, Menu, ChevronRight, Link2, RefreshCw,
  X, Moon, Sun, ChevronDown, Linkedin, Kanban, Settings,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const crmNavItems = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/contactos", icon: Users, label: "Contactos" },
  { to: "/oportunidades", icon: Target, label: "Oportunidades" },
  { to: "/pendientes", icon: CheckSquare, label: "Pendientes" },
  { to: "/presupuestos", icon: FileText, label: "Presupuestos" },
  { to: "/utm", icon: Link2, label: "UTM" },
  { to: "/formulario_web", icon: FileText, label: "Formularios web" },
  { to: "/facturas", icon: Receipt, label: "Facturas" },
  { to: "/historial", icon: LayoutDashboard, label: "Historial" },
  { to: "/conversiones", icon: RefreshCw, label: "Conversiones" },
];

const gestionNavItems = [
  { to: "/gastos", icon: Receipt, label: "Gastos" },
  { to: "/proveedores", icon: Truck, label: "Proveedores" },
];

const linkedinNavItems = [
  { to: "/linkedin-sourcing", icon: LayoutDashboard, label: "Dashboard LSS" },
];

const crmOptions = [
  { id: "form_entries", label: "NT_Crm_FormEntries", defaultRoute: "/dashboard", navItems: crmNavItems },
  { id: "gestion_inteligente", label: "Gestión inteligente", defaultRoute: "/gastos", navItems: gestionNavItems },
  { id: "linkedin_stealth", label: "NT_LinkedIn Stealth Sourcing", defaultRoute: "/linkedin-sourcing", navItems: linkedinNavItems },
];

function useTheme() {
  const [dark, setDark] = useState(() => {
    if (typeof window === "undefined") return false;
    const stored = localStorage.getItem("theme");
    if (stored) return stored === "dark";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("theme", dark ? "dark" : "light");
  }, [dark]);

  return { dark, toggle: () => setDark((d) => !d) };
}

function detectActiveCrm(pathname: string) {
  if (pathname.startsWith("/linkedin-sourcing")) return crmOptions[2];
  if (pathname.startsWith("/gastos") || pathname.startsWith("/proveedores")) return crmOptions[1];
  return crmOptions[0];
}

export default function CRMLayout({ children, showNotificationSettings }: { children: React.ReactNode; showNotificationSettings?: boolean }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { dark, toggle: toggleTheme } = useTheme();

  const activeCrm = detectActiveCrm(location.pathname);
  const navItems = showNotificationSettings
    ? [...activeCrm.navItems, { to: "/configuracion/notificaciones", icon: Settings, label: "Configuración · Notificaciones" }]
    : activeCrm.navItems;

  // Close mobile nav on route change
  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  const handleCrmSwitch = (crm: typeof crmOptions[number]) => {
    if (crm.id !== activeCrm.id) {
      navigate(crm.defaultRoute);
    }
  };

  const CrmDropdown = ({ className }: { className?: string }) => (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className={`flex items-center gap-1 text-xs font-bold transition-colors truncate ${className}`}>
          <span className="truncate">{activeCrm.label}</span>
          <ChevronDown size={14} className="shrink-0 opacity-60" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-56">
        {crmOptions.map((crm) => (
          <DropdownMenuItem
            key={crm.id}
            onClick={() => handleCrmSwitch(crm)}
            className={activeCrm.id === crm.id ? "bg-accent font-medium" : ""}
          >
            {crm.id === "linkedin_stealth" && <Linkedin size={14} className="mr-2 opacity-60" />}
            {crm.id === "gestion_inteligente" && <Kanban size={14} className="mr-2 opacity-60" />}
            {crm.label}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed lg:relative z-50 flex flex-col h-full bg-sidebar transition-all duration-200
          ${mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
          ${collapsed ? "lg:w-16 w-56" : "w-56"}
        `}
      >
        {/* Logo area */}
        <div className="flex items-center justify-between px-4 h-14 border-b border-sidebar-border shrink-0">
          {!collapsed && (
            <CrmDropdown className="tracking-wide text-sidebar-primary hover:text-sidebar-accent-foreground max-w-[160px]" />
          )}
          <div className="flex items-center gap-1">
            <button
              onClick={() => setMobileOpen(false)}
              className="p-1 rounded text-sidebar-foreground hover:bg-sidebar-accent transition-colors lg:hidden"
            >
              <X size={18} />
            </button>
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="p-1 rounded text-sidebar-foreground hover:bg-sidebar-accent transition-colors hidden lg:block"
            >
              {collapsed ? <ChevronRight size={18} /> : <Menu size={18} />}
            </button>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 py-2 space-y-0.5 px-2 overflow-y-auto">
          {navItems.map((item) => {
            const active = location.pathname === item.to ||
              (item.to !== "/" && location.pathname.startsWith(item.to));
            return (
              <Link
                key={item.to}
                to={item.to}
                className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors
                  ${active
                    ? "bg-sidebar-accent text-sidebar-primary font-medium"
                    : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                  }
                `}
              >
                <item.icon size={18} className="shrink-0" />
                {!collapsed && <span className="truncate">{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Theme toggle */}
        <div className="px-2 pb-3 pt-1 border-t border-sidebar-border shrink-0">
          <button
            onClick={toggleTheme}
            className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-sidebar-foreground hover:bg-sidebar-accent transition-colors w-full"
          >
            {dark ? <Sun size={18} className="shrink-0" /> : <Moon size={18} className="shrink-0" />}
            {!collapsed && <span>{dark ? "Modo claro" : "Modo oscuro"}</span>}
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 flex flex-col overflow-hidden min-w-0">
        {/* Mobile header */}
        <div className="flex items-center gap-3 px-4 h-14 border-b lg:hidden shrink-0">
          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => setMobileOpen(true)}>
            <Menu size={20} />
          </Button>
          <CrmDropdown className="text-primary max-w-[200px]" />
          <div className="ml-auto">
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={toggleTheme}>
              {dark ? <Sun size={16} /> : <Moon size={16} />}
            </Button>
          </div>
        </div>

        <div className="flex-1 overflow-auto p-4 sm:p-6">
          {children}
        </div>
      </main>
    </div>
  );
}

import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import CRMPrivateLayout from "@/components/CRMPrivateLayout";
import LoginPage from "./pages/LoginPage";
import FormEntriesListPage from "./pages/FormEntriesListPage";
import DashboardPage from "./pages/Index";
import ContactosPage from "./pages/ContactosPage";
import OportunidadesPage from "./pages/OportunidadesPage";
import PendientesPage from "./pages/PendientesPage";
import PresupuestosPage from "./pages/PresupuestosPage";
import GastosPage from "./pages/GastosPage";
import ProveedoresPage from "./pages/ProveedoresPage";
import UTMPage from "./pages/UTMPage";
import ConversionesOfflinePage from "./pages/ConversionesOfflinePage";
import LinkedInSourcingPage from "./pages/LinkedInSourcingPage";


import NotFound from "./pages/NotFound";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
});

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route element={<CRMPrivateLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/contactos" element={<ContactosPage />} />
            <Route path="/oportunidades" element={<OportunidadesPage />} />
            <Route path="/pendientes" element={<PendientesPage />} />
            <Route path="/presupuestos" element={<PresupuestosPage />} />
            <Route path="/gastos" element={<GastosPage />} />
            <Route path="/proveedores" element={<ProveedoresPage />} />
            <Route path="/utm" element={<UTMPage />} />
            <Route path="/formulario_web" element={<FormEntriesListPage key="formulario-web" screen="formulario-web" />} />
            <Route path="/facturas" element={<FormEntriesListPage key="facturas" screen="facturas" />} />
            <Route path="/historial" element={<FormEntriesListPage key="historial" screen="historial" />} />
            <Route path="/conversiones" element={<ConversionesOfflinePage />} />
            <Route path="/linkedin-sourcing" element={<LinkedInSourcingPage />} />


            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;

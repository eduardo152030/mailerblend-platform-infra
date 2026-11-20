import { useEffect, useState } from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import CRMLayout from "@/components/CRMLayout";
import { crmSession } from "@/lib/crm-session";

export default function CRMPrivateLayout() {
  const [signedIn, setSignedIn] = useState(!crmSession);
  const location = useLocation();
  const [isAdmin, setIsAdmin] = useState(false);
  const [ready, setReady] = useState(!crmSession);
  const queryClient = useQueryClient();

  useEffect(() => {
    const listener = crmSession?.auth.onAuthStateChange((event, session) => {
      if (event === "SIGNED_OUT") queryClient.clear();
      setSignedIn(Boolean(session));
      setIsAdmin(session?.user.app_metadata.crm_role === "admin");
      setReady(true);
    });
    return () => listener?.data.subscription.unsubscribe();
  }, [queryClient]);

  if (!ready) return null;
  if (!signedIn) return <Navigate to="/" replace state={{ contact: location.pathname === "/contactos" ? location.search : null }} />;
  return (
    <CRMLayout showNotificationSettings={isAdmin}>
      {crmSession && <button type="button" onClick={() => void crmSession.auth.signOut()}>Cerrar sesión</button>}
      <Outlet />
    </CRMLayout>
  );
}

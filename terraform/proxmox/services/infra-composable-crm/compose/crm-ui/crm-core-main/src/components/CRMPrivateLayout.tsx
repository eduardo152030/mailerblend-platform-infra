import { useEffect, useState } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import CRMLayout from "@/components/CRMLayout";
import { crmSession } from "@/lib/crm-session";

export default function CRMPrivateLayout() {
  const [signedIn, setSignedIn] = useState(!crmSession);
  const [ready, setReady] = useState(!crmSession);
  const queryClient = useQueryClient();

  useEffect(() => {
    const listener = crmSession?.auth.onAuthStateChange((event, session) => {
      if (event === "SIGNED_OUT") queryClient.clear();
      setSignedIn(Boolean(session));
      setReady(true);
    });
    return () => listener?.data.subscription.unsubscribe();
  }, [queryClient]);

  if (!ready) return null;
  if (!signedIn) return <Navigate to="/" replace />;
  return (
    <CRMLayout>
      {crmSession && <button type="button" onClick={() => void crmSession.auth.signOut()}>Cerrar sesión</button>}
      <Outlet />
    </CRMLayout>
  );
}

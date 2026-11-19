# CLINE-VERIFICACIÓN — límite de verificaciones repetidas

19/11/2026 Europe/Madrid. Fase 7. Estado IN PROGRESS.

- Alcance autorizado: limitar a dos las comprobaciones equivalentes y revisar la antigua regla 00.
- Rama: `docs/cline-verification-limit`. Worktree (desde la raíz Git): `terraform/mailerblend-platform-infra-cline-verification-limit`.
- Base e inicio de ronda: `0ec2476202f2f4fda277d2f3c1af8f2bb53a786b` (`origin/main`).
- Evidencia: en CT611 Cline releyó el log del mismo plan y comprobó repetidamente el mismo HEAD y estado Git, después de obtener resultados concluyentes. La sesión se detuvo manualmente. La antigua regla 00 pasó a ser la 01 en el PR #20.
- Criterio: una comprobación concluyente cierra ese criterio. Se admite una segunda si falta evidencia concreta. Cambiar de comando o compactar el contexto no reinicia el límite. Las comprobaciones distintas del workflow siguen siendo obligatorias.
- Siguiente paso: revisión del propietario y prueba en una sesión nueva de Cline. El cumplimiento durante una sesión real queda pendiente.

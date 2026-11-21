# CT633 — Entrada /login → /home de Outline

21/11/2026 Europe/Madrid. Ronda `implementation`, base
`4bd13663353baab449a1ed92fa26fd2f4ca97d5e`, rama `fix/outline-login-home`,
worktree `../mailerblend-platform-infra-outline-login`. Continúa el corte #90.
CT109 redirige /home a / y Outline v1.13.0 usa la primera colección para
usuarios sin historial. Restaurar la ruta /home nativa; normalizar solo
el Location de la colección que devuelva el callback OIDC.
Validar ambos roles en navegador con sesión limpia y conservar la
navegación directa a colecciones. Respaldar el vhost antes de recargar.

## Evidencia

CT109 guardó el vhost anterior, validó `nginx -t` y recargó. La prueba
de navegador usó DNS normal sin excepciones TLS. Dos sesiones limpias
confirmaron /login, callback /home, rol y Home visible. Tiempo desde
enviar las credenciales: administrador 1,84 s y miembro 1,74 s.
El enlace directo a Operations & Runbooks mantuvo su ruta en ambos casos.
La segunda aplicación dio `Sin cambios`.

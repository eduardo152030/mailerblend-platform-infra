# CT633 — Corte de Outline en infra-doc.mailerblend.com

21/11/2026, Europe/Madrid. Fase 7, ronda `implementation`. Rama
`ops/knowledge-platform-edge-cutover`, worktree
`../mailerblend-platform-infra-knowledge-cutover`, base
`f1eb99c18aea65101f4bd496cc04547bb37734fa`. El propietario autorizó el
corte del vhost existente y una interrupción de hasta 10 minutos.
CT101 y sus datos se preservan. CT109 conserva su certificado Certbot
y los demás vhosts. El origen dedicado de Outline incluye raíz, REST,
WebSocket y Dex. /home redirige a la raíz del nuevo origen.
El acceso se mantiene en la LAN. TLS a CT633 con su CA privada y acceso
exclusivo desde CT109. Respaldar vhost, entorno y Dex antes de activar.
Revertir ambos lados ante fallo de salud o autenticación.

## Resultado

Inicio del corte 01:02:08 CET, aceptación 01:02:20 CET. Dedicación del vhost
completada en 12 segundos entre activación y validación. `nginx -t` PASS
en candidatos y después de la recarga. El DNS existente llevó a Outline
con HTTP 200 tras seguir la redirección de /home. Health respondió OK.
Discovery de Dex y login por CT109 de administrador y miembro PASS, ambos
en el mismo workspace con las colecciones existentes.
Acceso directo al upstream desde un origen distinto de CT109 devolvió 403.
CT101 y CT633 siguieron RUNNING; la sonda existente de CT633 devolvió 1.
Los respaldos de entorno, Dex y vhost quedan en directorios de root de los
dos CT. No se modificaron Docmost ni sus datos. Queda pendiente integración
Draw.io por su propio origen y la aceptación de SMTP.

La misma clave REST leyó el UUID y el bloque PlantUML de validación
en el nuevo origen mediante el DNS normal.

[PR #90](https://github.com/eduardo152030/mailerblend-platform-infra/pull/90).

## Sincronización y guías

Ronda `review-01`, base tras sincronizar `689937de054a304421e5cb40c76f5cddf35bbe5c`.
Se incorporó a la rama el merge de #89 sin reescribir commits. La guía de
agentes, el inicio rápido, el manifiesto y el diagrama ahora reflejan el
origen verificado y distinguen Draw.io como pendiente.

# Corrección de healthchecks CRM/EVA — D-051

Seguimiento: 2026-11-07 (Europe/Madrid). Estado: **DONE — corrección técnica**.
[Roadmap](ROADMAP.md) · [Estado](CURRENT-STATUS.md) · [Decisiones](DECISIONS.md)

## Autorización y alcance

El propietario solicita revisar y resolver exactamente las tres alarmas
DockerContainerUnhealthy aparecidas tras D050: focalboard CT622, budibase-app y
crm-api CT618. Se autorizan las correcciones necesarias de sus checks y recreaciones
mínimas para aplicarlos, con backups y rollback. No se cambian imágenes instaladas,
variables de aplicación, puertos, recursos, datos/volúmenes, DB/esquemas, exporters,
reglas ni umbrales. No commits/push. F5 permanece DONE; F6 no se inicia.

## Diagnóstico y corrección

| Contenedor | Fallo demostrado | Salud real previa | Corrección |
|---|---|---|---|
| crm-api618 | wget ausente, salida1 | /health200, /ready200 y db=ok | Python instalado + urllib /ready, exige HTTP200 y db=ok |
| focalboard622 | curl ausente, salida-1; ruta /api/v2/teams devuelve400 | /api/v2/ping200 y UI200 | Bash existente, socket loopback /api/v2/ping, exige HTTP200 |
| budibase-app618 | check heredado Redis interno WRONGPASS; carga /data/.env | UI200; /api/system/status passing=true, versión3.27.4; backend/worker200; Redis externo PONG y CouchDB externo200/statusok | Python instalado: UI/backend/worker/status, CouchDB y Redis efectivos desde sus URL de entorno, más nginx -t |

El Redis externo utiliza credenciales incluidas en REDIS_URL, no una variable
REDIS_PASSWORD ausente del entorno Docker. El comprobador separa host/puerto y
credenciales: REDISCLI_AUTH en entorno del subproceso, nunca contraseña en argv ni
logs. CouchDB recibe Basic Auth sin usuario/contraseña en la URL solicitada. Fallos
se notifican con texto genérico, sin excepciones que puedan mostrar secretos.
No se modifica el Redis interno ni se cambia autenticación para hacer pasar el check.

No se instalan paquetes, binarios ni nuevas imágenes. Focalboard dispone de Bash
con /dev/tcp, comprobado dentro del contenedor original antes de tocarlo; no necesita
el comprobador estático considerado durante diagnóstico. La sonda ping acredita
respuesta del servidor; no equivale a login o flujos de negocio de Focalboard.

## IaC reproducible

- [Generador de overlays](../../scripts/generate-d051-healthchecks.py).
- [Comprobador Budibase](../../services/infra-composable-crm/recovery/healthchecks/budibase.py).
- [Overlay Budibase](../../services/infra-composable-crm/recovery/healthchecks/budibase.compose.yml).
- [Overlay API](../../services/infra-composable-crm/recovery/healthchecks/crm-api.compose.yml).
- [Overlay Focalboard](../../services/infra-eva-assistant-bot/recovery/healthchecks/focalboard.compose.yml).
- [Transacción acotada](../../scripts/repair-d051-healthchecks.py).
- [Pruebas](../../tests/monitoring/test_d051_healthchecks.py).

El script obtiene el Compose ACTIVO desde las etiquetas del contenedor y sus
archivos/env existentes. Verifica que entorno efectivo, imagen, redes, volumen y
permisos declarados coincidan con el runtime antes de parar. Selecciona únicamente
el servicio autorizado, incorpora el healthcheck y fija el mismo image ID instalado.
Redes/volúmenes se declaran externos con sus nombres exactos; nunca crea una nueva
DB/volumen ni arranca dependencias. Los valores renderizados permanecen privados.

Cada candidato usa proyecto Compose exclusivo, conservando el nombre de contenedor
que observan clientes y alertas. Esto evita que Compose elimine/reutilice el original
renombrado. Los cambios de etiquetas de proyecto/config_files y hostname derivado
del ID son metadatos de la recreación; las variables funcionales no cambian.
No ejecutar los despliegues históricos generales ni sobrescribir el Compose activo
con un fichero parcial del repositorio: perdería la configuración real preservada.

Ejecución secuencial: crm-api (d051), focalboard (d051b tras rollback), budibase-app
(d051). prepare valida config y ejecuta el nuevo check dentro de la aplicación
ORIGINAL todavía funcionando. apply hace parada ordenada sin SIGKILL, preserva y
renombra el original; copia sus datos de aplicación en frío; requiere copia externa
restaurada en staging antes de crear el candidato. Compose up --no-deps --no-build
--pull never se limita al servicio. Tras healthy se comprueban invariantes y segunda
aplicación sin cambios de ID/arranque/reinicios. verify comprueba el estado aceptado.

Los Compose privados activos quedan en /opt/healthcheck-d051/<servicio>/compose.private.json
(API/Budibase) y /opt/healthcheck-d051b/focalboard/compose.private.json. Sus etiquetas
Docker apuntan a esos archivos persistentes; no dependen de /tmp local. /tmp solo
se utilizó durante diagnóstico, nunca como dependencia productiva.

## Backups y rollback

Configuración activa, entornos, metadatos completos e inputs de Compose se archivan
antes de parar. Datos de Budibase /data y Focalboard data/config se copian en frío,
con originales detenidos. API no tiene montajes persistentes. Copias CT y fuera de
PVE contrastadas por SHA256; extracción a staging de cada archivo regular comparada
por hash. Se rechazan enlaces/rutas de extracción inseguras. Ningún backup se borra.

Privados locales: $HOME/.local/share/mailerblend-recovery/healthchecks/d051/,
incluido attempt-d051b. En CT: /opt/healthcheck-d051/ y /opt/healthcheck-d051b/.
Cada original se conserva detenido como <nombre>-d051-original o
focalboard-d051b-original. El candidato rechazado de Focalboard también se conserva.
No se actualizan datos ni esquemas de DB y no se recrean contenedores PostgreSQL,
CouchDB o Redis. Los backups/restauraciones completas F3 siguen siendo evidencia
histórica, no una restauración DB nueva realizada aquí. No extender su dispensa UAT.

Rollback acotado: parar el candidato, conservarlo renombrado, recuperar el nombre del
original y arrancarlo sobre los mismos montajes. No eliminar volúmenes, imágenes ni
usar Compose down. El script exige identidades/proyectos esperados. No reutilizar
este checkpoint sobre cambios futuros sin diagnóstico/autorización.

## Incidencias del procedimiento

1. API: gate inicial comparó DNS [] frente a null como distintos. No hubo cambio
   efectivo. La reversión preventiva intentó SIGTERM sin SIGKILL y agotó120s durante
   arranque; el candidato permaneció disponible y alcanzó healthy. Tras comprobar
   que entorno/imagen/montajes/recursos/redes eran idénticos, se reconcilió ese mismo
   candidato y se probó segunda aplicación sin recreación. Original detenido retenido.
   No se certifica comportamiento de parada SIGTERM bajo cualquier carga; queda
   como observación operativa, sin modificar código de aplicación para este alcance.
2. Focalboard: config normalizado serializa $$status para conservar el dólar literal;
   se adaptó su comparación antes de despliegue. Primer candidato rechazado por comparar
   HostConfig.Binds contra montajes estructurados de otra versión Docker/Compose,
   aunque rutas y permisos efectivos coincidían. Rollback completado: original
   disponible y datos intactos. Segundo intento usa proyecto/directory d051b para
   conservar el candidato rechazado y no sobrescribir backups.
3. Validador final compara montajes efectivos (tipo/ruta/destino/RW/propagación),
   normaliza listas DNS vacías y mantiene el rechazo de cambios reales. Regresiones
   específicas prueban equivalencias y el veto a cambios de DNS/volumen/entorno.

No se ocultan los reintentos ni se atribuyen a incidencias de las aplicaciones.
Conteo de candidatos y resultado final quedan en la evidencia al cierre.

## Validación

16 pruebas PASS: HTTP200/400/503, readiness dbok/down, Redis URL autenticada y WRONGPASS,
health false, CouchDB no listo, equivalencia de serialización y rechazo de drift real.
Compose config y ejecución directa de cada receta en el original antes de recrearlo.
Validación posterior: healthy, HTTP, imagen/env/recursos/montajes/redes, demás IDs/
arranques/reinicios, segunda aplicación, métricas cAdvisor y desaparición de alertas.
No se realizan eventos Analytics ni escrituras de negocio para probar estos checks.

La cobertura F4 17/17 y configuración F5 se conservan. El resultado de salud puntual
no implica una nueva UAT completa de CRM/EVA ni de sus automatizaciones.

## Resultado final

[Evidencia](evidence/2026-11-07-d051-result.json), 2026-11-07 16:08 CET.
Los tres contenedores están healthy, cAdvisor expone exactamente tres series de
salud1 para estas identidades y **cero alertas objetivo FIRING** en Prometheus/AM.
API /health y /ready200/dbok; Focalboard ping/UI200; Budibase status200/passing=true
y versión3.27.4 conservada. Prom/AM READY; 17Node/17cAdvisor/11Blackbox UP.
Ningún error nuevo de notificación Telegram en la ventana30m; errores históricos56
constantes. No se afirma recepción humana de los RESOLVED de D051; la ruta WARNING
puede agruparlos hasta5min. No se enviaron alertas sintéticas ni POST directos AM.

La serie antigua de Budibase permaneció temporalmente junto a la nueva después de
la recreación. Se esperó a su retirada; no se cambió la regla min ni sus umbrales
para ocultarla. La evidencia final ya no incluye esa serie y confirma resolución.

Candidatos creados: API1, Focalboard2 (primero revertido y retenido), Budibase1.
Los tres finales tienen idempotencia demostrada y conservan imageID/env/recursos/
montajes/redes. Verificación coordinada permite únicamente los otros targets D051
ya aceptados por ID/healthy/prueba, para no confundir su cambio autorizado con drift
de aplicaciones ajenas; los demás contenedores permanecen idénticos.

Backups de configuración y datos privados CT/fueraPVE restaurados en staging,
originales e imágenes conservados. Generador de overlays idempotente, 16pruebas,
compilación Python, enlaces locales y git diff --check PASS. Sin commits/push.

Pendientes separados: no se realizó login/UAT de negocio; observación de SIGTERM
de API durante arranque queda documentada para revisión futura, sin forzar cierre
ni modificar código funcional. F3 no se reabre ni amplía su dispensa. F5 conserva
DONE — Accepted. Siguiente: revisión del propietario; F6 requiere alcance/autorización.

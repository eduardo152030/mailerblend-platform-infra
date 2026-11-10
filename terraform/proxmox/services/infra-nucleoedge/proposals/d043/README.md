# CT614 — overlay aplicado D044; sondas opcionales NO aplicadas

El healthcheck nativo está aplicado sobre la base activa, como documenta
[el cierre D044](../../../../docs/roadmap/CT614-SGTM-D044-RECOVERY.md).
Las otras tres propuestas Blackbox permanecen diferidas y sin aplicar.
El procedimiento siguiente se conserva como referencia; no repetir recreaciones
sin autorización de mantenimiento.


Prioridad: recuperar la salud nativa del runtime, no cambiar las sondas para ocultar503.

1. `healthcheck.native.yml`: única corrección de Compose propuesta. Sustituye curl
   por el comprobador Node que YA contiene la imagen instalada. Se ha validado con
   `docker compose config` porstdin contra elCompose REAL sin escribir enproducción:
   imágenes/puertos/environment/recursos idénticos. Por sí sola no elimina caducidad:
   suaplicación recrea elservicio yrenueva elbootstrap cargado alarranque.
2. Los otros tres archivos son **complementos opcionales diferidos**, no requisitos
   pararecuperar sGTM ni config activa. Conservan las11sondas actuales íntegramente
   yproponen2adicionales GETnativo (13total),nuevomódulo GET200sinheadersdebypass y
   alertaSgtmRuntimeUnhealthy. Hoy esoschecks devolverían503 ydebenfallar; noGA4payload.
   No sustituir nidesactivar lasHEADexistentes; están200actualmente. Antes de usar
   estoscomplementos,separar autorización,validaciónBlackbox/promtool eintegración:
   elvalidadoractual deliberadamente NO acepta aún elnuevomódulo.

Usar la base **real** `/opt/infra-nucleoedge/docker-compose.yml`, NO elCompose
local histórico conpuertos8093/8094/otraPreviewURL yconfiguración incrustada.
No copiar secretos alrepositorio. Nativecheckerobservado usa`/healthz`; ambasrutas
`/healthz` y`/healthy` son atendidas por elbootstrap. NoHTTPHEAD paralivenessnativa.

Procedimiento propuesto para otra intervención autorizada:

- Backupprivado verificable deCompose/config/env,imageIDs yestado/montajes.
  Confirmar que `stable` local sigue apuntando a la misma imagen activa. Conservar
  configuración/originales; no pull,build,volúmenes/DNS/proxy/GoogleCloud changes.
- Comprobar accesoTLSGoogle desdeCT614 paraarranque ycapturarbaseline.
- Copiar solooverlay aldirectorio deoperaciónprivado;configvalidada sinvalores
  sensibles enstdout. Revisardiffestructural: únicamentehealthchecks.
- RecrearPreview primero conimagenlocal existente, después servir SOLOsiNativeGET
  Previewdevuelve200. Ejemplo,con rutas yaaprobadas:

  ```bash
  docker compose -f /opt/infra-nucleoedge/docker-compose.yml -f /ruta/aprobada/healthcheck.native.yml config --quiet
  docker compose -f /opt/infra-nucleoedge/docker-compose.yml -f /ruta/aprobada/healthcheck.native.yml up -d --no-deps --no-build --pull never sgtm_preview
  # Validar /healthz local8092 y /preview/healthz público antes de seguir.
  docker compose -f /opt/infra-nucleoedge/docker-compose.yml -f /ruta/aprobada/healthcheck.native.yml up -d --no-deps --no-build --pull never sgtm
  ```

- ExigirGETsinheadersespeciales200 en8091/8092 yambasrutaspúblicas,Dockerhealthy,
  mismosimageIDs/env/puertos/recursos,sinrestartsinesperados/erroresdebootstrap.
  Si fallaPreview,no avanzar alprincipal. Si fallaarranque,restaurarCompose/imagen
  anteriores medianteprocedimiento acordado; noactualizarimagen poriniciativa.
  Conservarlosbackups: unarranque nuevo depende delbootstrapGoogle disponible.
- RevisarPreviewUI yclienteGA4/tagspublicados porlectura. Aceptarhealth200NOprueba
  eventosGA4 recibidos. No cambiarHEADaGETconlosmismosIDs/page_view: podría emitir
  datos. Pruebaeventual deeventos requiere advertencia/autorización ypropiedadtest
  oexclusión acordada. NingúneventoGA4válido enviado enD043.

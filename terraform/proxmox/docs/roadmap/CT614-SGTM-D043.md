# CT614 — sGTM/Preview: diagnóstico D-043, corrección NO aplicada

**Actualización:** recuperación autorizada y completada en [D-044](CT614-SGTM-D044-RECOVERY.md). Este documento conserva el diagnóstico previo.

2026-11-06 (Europe/Madrid). Investigación porlectura; F4exporters17/17 no se reabre.

## Diagnóstico

1. **Hay un problema real de salud del runtime, además de la sonda Docker incorrecta.**
   sGTM yPreview corren desde17septiembre,unos50días,mismaimagen,sinrestarts.
   GET`/healthy` y`/healthz` dan503 enambos,privado ypúblico; elchecker nativo sale1.
   ElbootstrapGoogle devuelve503 cuando vence su temporizador desalud: base12–14días
   conajustes decalendario. Elheader diagnóstico nativo confirma edad>30y<60días en
   ambos. Elprincipal refresca sucontenedorGTMen<5min; no parece fallo deinicialización
   por credencial inválida. Causa del503 atribuida concorrobación fuerte a **bootstrap
   cargado alarranque caducado**, noremediar con umbrales ni cambiando la sonda.
   Fuente: [bootstrap oficial](https://www.googletagmanager.com/static/serverjs/latest/server_bootstrap.js)
   y[guíaGoogle](https://developers.google.com/tag-platform/tag-manager/server-side/manual-setup-guide).
2. **HealthcheckDocker incompatible:** usa`curl http://localhost:8080/`, pero no hay
   curl ni/bin/sh; además `/` devuelve400(serving)/404(Preview). LaimagenYAincluye
   `/nodejs/bin/node /app/health_checker_bin.js`,queconsultaGET`/healthz`. Corregir
   elcomando por sísolo noarreglaría elruntime503. No instalarcurl nishell.
3. **Configuración:** CONTAINER_CONFIG decodificable,conúnicosid/env/auth,IDconformaGTM,
   envnumérico positivo yauthpresente. Main/Previewiguales; nunca sepublicanvalores.
   PreviewRUN_AS_PREVIEW_SERVER=true;mainURLhttps://edge.nucleotecnologico.es/preview.
   Conexiónmain→sgtm_preview:8080 ymain→URLpúblicaPreview funciona aHTTP/TLS,
   aunque devuelven503. Preview no refresca periódicamente comoelprincipal; su
   diagnóstico deúltimorefresco noprueba authinválida. Logs acotados sin señales
   reconocidas deauth/inicialización fallida; no sevolcaronlogsni variablescompletas.
4. **Enrutamiento confirmado:**DNS79.156.8.245,TLSválido,NginxCT109:`/`→614:8091,
   `/preview/`→614:8092,quitando prefijo. Peticiónpública conmarca inocua`/healthy`
   observada porcaptura filtrada enCT614puerto8091. No problemaDNS/proxy demostrado;
   no cambiarlos. Elpropietario confirmó además las mismasrespuestas desdeEdgeRouter.
5. **400/404:**`/` no es unapáginaweb ni eventoGA4válido:400principal y404Preview
   noacreditan caída. `/g/collect` sinquery/cuerpo devuelve400principal y404Preview,
   incluyendoGET/POST/HEAD/OPTIONS. Sonpeticiones incompletas, no prueba dequeGET/POST
   válidos nofuncionen. No se enviaron eventosGA4válidos,IDs nireproducción deprobes.
6. **Blackbox NOestáfallando ahora:**ambassondasHEADexistentes reciben200,
   probe_success1,mínimo24h1;sinCollectEndpointDownactiva. Nginxno contiene reglaHEAD
   ni return200 quefabrique suéxito. HEADconelqueryactual esaceptado enesta instancia;
   noesriguroso culparalmétodo porlaalertaantigua. Laalertafiring retenida esdel2nov,
   último muestreo20:41UTC(21:41CET),paso5min; elestadoHTTPduranteelfallo era0
   (sinrespuestaHTTP),no400. No hayevidencia suficiente paradistinguirDNS/TLS/TCP
   deaquellafalla. HEAD200 tampoco valida liveness delbootstrap nientregaGA4.
7. **GA4 extremo aextremo no certificado:** mainrefresca configuración yprobesHEAD
   responden200,pero no hayexport/workspaceGTM para verificar clienteGA4,versionpublicada,
   tags/consent/triggers ni confirmación deeventos recibidos enAnalytics. No afirmar
   pérdida realdeeventos ni ausenciadepérdida solo conestoschecks. UnpreviewUI válido
   oevento controlado requiere revisión/autorización separada, sincontaminarAnalytics.

Los200delheaderdiagnóstico deantigüedad **NOsonsalud real**:sinheader `/healthz`
sigue503. No usar eseheader paraenverdecer lasprobes.

## Corrección mínima preparada

[Overlayhealthcheck](../../services/infra-nucleoedge/proposals/d043/healthcheck.native.yml)
validado contraComposeREALporstdin/config,nocuandocopia local histórica: únicamente
cambiahealthcheck,imágenes/puertos/environment/recursosidénticos. Producciónusa8091/8092;
elComposehistóricorepo8094/8093 yotraURLPreview: **no desplegarlo como base**.

Después deautorización demantenimiento: backupprivado verificable ymismaimagenlocal,
recrearPreviewprimero para recargarbootstrapGoogle,exigirGETnativo200,despuésmain.
Sinpull/build/imagen nueva,CONTAINER_CONFIG igual,sinCloud/DNS/router/cambiosproxy.
[Rutas ycomandos exactos](../../services/infra-nucleoedge/proposals/d043/README.md).
Restaurar configuración/imagen originales siarranque falla; noavanzar alprincipal
siPreviewnoestá200. Unnuevoarranque depende deaccesoTLS aGoogle; no garantizasuéxito
sin ejecutarlo. Ningúnreinicio nirecreación realizados enestediagnóstico.

Las propuestasBlackboxdeesacarpeta son **opcionales,diferidas yNOintegradas**:
conservan las11sondasexistentes yproponen2checksGETnativos(13total),solo200,TLSestricto,
sinpayload niheadersdebypass. Hoydebenfallar por503; noaplicarlasparaocultarproblema.
Nosecambió catálogo/config/reglas activos ni suvalidador. Primero resolverbackend;
no convertirHEADactualaGETconlosmismosIDs/page_view porque podríaemitireventos.

## Evidencia yvalidación

- [Inicialización](evidence/2026-11-06-d043-initialization.json),
  [estructura](evidence/2026-11-06-d043-config-structure.json),
  [sondas seguras](evidence/2026-11-06-d043-safe-probes.json).
- [Correlación pública](evidence/2026-11-06-d043-route-correlation.json),
  [Blackbox actual](evidence/2026-11-06-d043-blackbox-live.json),
  [histórico](evidence/2026-11-06-d043-alert-historical-status.json).
- [Composecandidato](evidence/2026-11-06-d043-compose-candidate-validation.json),
  [tiempo](evidence/2026-11-06-d043-time.json).3tests depropuesta y7decatálogoPASS.

No producción modificada,reinicios,imágenes nuevas,Cloud/DNS/router,commit/push.
La lectura inicial delCompose mostróCONTAINER_CONFIG preexistente sin enmascarar;
se corrigiólaforma deinspección.No se añadióesa credencial aestas evidencias/candidatos.

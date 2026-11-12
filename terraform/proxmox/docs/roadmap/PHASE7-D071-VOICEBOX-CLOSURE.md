# Fase 7.4 — D-071: Voicebox, voz personal y worker CPU

Estado: **NOT_ACCEPTED; rollback verificado, sustituido por D072**. Autorización D071,11nov2026 Europe/Madrid. No se considera
cierre técnico ni aceptación de calidad hasta ejecutar los criterios reales.

Arquitectura elegida: Voicebox existente + adaptador de engineOpenVoice + worker
API interno, sin puertos públicos. Worker procesa un trabajo por proceso hijo,
cola máxima2 incluidos activo/pendiente, timeout ycancelación de grupoPID con reap.
Presupuesto inicial3GiB,CT7GiB/3CPU/512swap/50disco sin cambios. AdaptaciónUI por
entrada de motor yvalidación de formulario, sin rediseñar arquitectura del fork.
QwenCPU bloqueado. Originales de voz privados, perfilUUID existente conservado.

ModeloOpenVoiceV2 yMeloES bajoMIT, tarjetas indicanuso comercial permitido para
vídeos; conservar avisos/licencias en la imagen. Código revisado y fijado porSHA,
pesos339.445.880bytes/11archivos persistentes descargados yverificados sin cargaML.
NoBERT/ASR ni pesos de otros idiomas; tokenizador español local. Converter usando
API oficial extract_se sobre referencia real ya validada; watermark opcional no
cargado, sin añadir otrocheckpoint. Runtime separado Python3.10/torch2.2CPU frente
aVoicebox3.12/torch2.8; imports Melo limitados aES y rutas de modelos explícitas.

Backup previo consistenteSQLite+data/config/originales:69archivos en
/opt/voicebox/backups/d071-before; imágenes ybackupsD069/D070 conservados.
Todavía no sustituido el servicio Voicebox estable al crear este informe.

## Cierre de alcance tras rechazo del propietario — 11nov2026

**NOT_ACCEPTED / restaurado.** El propietario rechazó expresamente la muestra
369ebd31: «no esa no es mi voz». La muestra corta produjo7,372s en34,256s;
trading15,391s en74,204s porUI. Cancelación real nativa0,423s y timeout1,226s
verificados, pero el ensayo de minuto se detuvo a12,145s porPSIfull del host2,12%,
sin audio de minuto. OOM0; no atribuir este veto a falta deRAM del modelo.
Rollback a imagenD069 ejecutado, workerOpenVoice parado; perfil/originales/muestras
conservados. Kokoro yPiper generan después en helpersoffline. EvidenciasD071
persistentes en evidence/ y backup69archivos restaurado/SQLiteok fueraPVE.
La preparación anterior no constituye cierre aceptado de Voicebox. D072 sustituye
el motor prioritario porQwenC/BLAS aislado; no continuar optimizando OpenVoice.

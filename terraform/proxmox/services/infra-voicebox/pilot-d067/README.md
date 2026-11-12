# Piloto D067 — ejecución acotada

[Autorización, estado y resultados](../../../docs/roadmap/PHASE7-D067-QWEN-6G.md).
No reejecutar automáticamente después de HALT o una solicitud ya registrada.

La imagen es la candidata inmutable D066, sin reconstrucción. Compose separa los
datos de producción y reutiliza la caché fijada D066 mediante bind persistente.
La imagen original permanece conservada y Kokoro se descarga de RAM durante el
ensayo. El CT tiene 6144 MiB, candidata 5200 MiB, sin swap adicional, CPU 2/3.
El supervisor externo detiene a 5,5 GiB de cgroup, crecimiento swap >64 MiB,
OOM, falta de respuesta, degradación de targets o <1,5 GiB disponibles en el host.

Prerequisitos: backup restaurado fuera de PVE, hash de la imagen original y
candidata verificado, datos aislados preparados y plan Terraform revisado:
solo CT627 memory 3072→6144, swap512, sin recreaciones ni otros campos.
El wrapper `scripts/run-d067-pilot.py` aplica el plan y prepara/revisa el plan de
rollback antes de generar audio. El supervisor se instala en PVE y se ejecuta por
systemd con `ExecStopPost` de restauración. El wrapper devuelve RAM a3072 si falla;
solo un resultado PASS conserva6144. Nunca sustituye ni borra datos productivos.

Las peticiones e IDs se registran antes de esperar el audio. Corto→30→60 segundos
son secuenciales y condicionados al PASS anterior. Se guardan WAV y SHA256,
RSS/HWM/cgroup/working set/swap/OOM/CPU/tiempo, con pico cgroup adicional tras
la parada. Un timeout es fallo y rollback, aunque no haya OOM.

`inspect-base.py` lee solo cabeceras safetensors fijadas por revisión; no descarga
pesos ni carga Base. El backend Base instalado sigue CPU FP32. No extrapolar las
mediciones CustomVoice a la clonación; falta una candidata BF16 específica Base,
grabaciones reales y una validación independiente antes de usarla.

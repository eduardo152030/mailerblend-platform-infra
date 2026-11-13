# D087 — ampliación CT627 a20GiB y guarda19GiB

[Informe y estado actual](../../../docs/roadmap/PHASE7-D087-QWEN-CHATTERBOX-PRODUCTION-VALIDATION.md).
Recursos aplicados y reconciliados. D087fallido quedópreservado; posteriorD087b
desplegado/healthy, QwenEnglishaceptado yCBdeshabilitadoenguarda7GiB.
No reejecutar automáticamente ni reutilizar nombres de backups existentes.

Orden autorizado: preflight físico y salud, backup actualizado/extracción verificada,
plan Terraform exclusivo627, resize-live.py enPVE, install-guards.py desde repositorio,
Notes y refresh-only dirigido revisado, planfinal cero cambios. BPG0.94 reiniciaría
CT al cambiarRAM: no aplicar el plan normal de memoria. No deploy-all ni apply general.

resize-live.py limita memoria a20480MiB, conserva CPU3/swap2048 y app/otrosCT,
compara identidades y conserva backups enHDD. El presupuesto físico toma el techo
operativo19GiB y exige6GiB restantes. install-guards.py conserva worker9GiB/stop8,2,
preflight4,5+0,5GiB, presión/swap y cancelación; solo guardaCT19GiB y RAMesperada20GiB.

engine_policy.py y supervise_chatterbox.py son overlays exclusivos de recursos para
el bundleD087: guarda19GiB/RAM20GiB; worker8GiB/stop7 y300s intactos. Release fija
hashes; app21270364… y dependencias/modelos siguen inmutables. No reutilizar recetas
D080/D085 para desplegar constantes15GiB/14GiB como configuración actual.

Rollback de despliegue restaura app/controlador/srcD081 con20GiB/19GiB ya aplicados.
No reducirRAM bajo una carga activa ni restaurar SQLite para deshacer recursos.
La corrección de copia está solo en deploy-d087; no hubo otro intento ni inferencia.

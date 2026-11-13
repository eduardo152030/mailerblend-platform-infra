# D-089 — Voicebox bilingüe aceptado

13 de noviembre de 2026 (Europe/Madrid). El propietario escuchó y aceptó Chatterbox
es5,48s/en5,00s y Qwen en45,04s. Qwen esD081 se conserva. Alcance VoiceboxF7.4
DONE/ACCEPTED; no cerrar F7global ni aceptar narraciones Chatterbox no probadas.

Producción CT627:20GiB/3vCPU/2GiBswap/rootfs100GiBSSD. App21270364… UID/GID999,
worker bcc5c14f… CPUFP32. Qwen Base0.6B es/en,42,A/B con checkpoint persistente,
1200caracteres/900s,hard9GiB. CB MultilingualV3 es/en,240caracteres/400tokens/EOS,
300s, WAV≤20s,stop7/hard8GiB; guardaCT19GiB y exclusión mutua con Qwen.

`audit.py` es de solo lectura: API, JS servido, validación pura240/241/1200,
configuración instalada y metadatos de perfil. No TTS, DSP, modelos cargados,
solicitudes de generación, cambios de configuración ni reinicios. Ejecutar mediante
SSH estricto al PVE existente, pasando el archivo a python3 por stdin. No imprimir
env, credenciales, SQLite ni logs completos. La auditoría no autoriza ampliar límites.

Presets Robotic/Radio/Echo Chamber/Deep Voice disponibles para ambos motores.
Eduardo usa sin efectos por defecto; API puede heredar una cadena de otro perfil
si ese perfil la configura. Normalización es independiente. Efectos con voz real
no se ensayaron ni se consideran aceptados acústicamente aquí.

Fuentes reproducibles:

- candidate-d083: contrato Qwenes/en, referencia/transcripción originales intactas.
- candidate-d085: UI/API, dependencias/modelos fijados y presets compartidos.
- startup-d086: corrección del entrypoint no privilegiado UID999.
- maintenance-d087: recursos/guardas aprobados y política efectiva.
- memory-d088 y validation-d089: assign=True, auxiliar chino diferido, observabilidad,
  candidato probado, despliegue mínimo y locks. No cuantización/cambio de pesos.
- validation-d089/resume: observador GET-only y reactivación del receipt sin reinicios.

Los pilotos y recetas de transición son históricos: no reejecutarlos ni ampliar
recursos automáticamente. El rollback conserva imagen/controlador/source link;
no restaurar SQLite antiguo encima de generaciones nuevas. Recuperar los datos
privados desde backups verificados externos al repo, sin incorporarlos a Git.
Modelos y dependencias se recuperan por revisión/hash; grabación original solo RO.

Publicación: repositorio IaC mailerblend-platform-infra, flujo existente main→origin/main,
sin force. Git no almacena imágenes OCI, pesos, voz, WAV, SQLite, checkpoints,
backups, env/credenciales ni estados Terraform. La imagen Voicebox aceptada se
conserva; publicar el código no implica redesplegarla ni actualizar Proxmox Notes.

Informe y evidencia: docs/roadmap/PHASE7-D089-CHATTERBOX-PRODUCTION-VALIDATION.md,
evidence/2026-11-13-d089-acceptance-audit.json. Aceptación humana registrada como tal;
no sustituirla por un test sintético. Capacidad para1200caracteres en CB queda pendiente
fuera del cierre, aunque el código se pueda modificar para investigarla en otro alcance.

Cambio posterior: las fuentes admiten entrada1200 en Chatterbox, sin validar
generación completa. Esta publicación no cambia la producción D089 de240.
Ver docs/roadmap/VOICEBOX-CHATTERBOX-INPUT-1200.md; no reejecutar recetas ni
interpretar los digests de imágenes D089 como un nuevo build.

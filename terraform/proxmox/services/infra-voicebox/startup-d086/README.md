# D086 — corrección de startup para UID999

**Candidato validado en aislamiento; no desplegado.** D081 sigue healthy, con el
mismoID/inicio. No ejecutar transaction.py del intento fallido: fija la imagen
anterior. Un despliegue futuro exige adaptar/revisar imagen y contexto y obtener
nueva aprobación. No ejecutar A/B/C desde esta carpeta.
[Informe](../../../docs/roadmap/PHASE7-D086-UID999-STARTUP-FIX.md).

## Cambio mínimo

Dockerfile deriva de D085 verificado porhash; conserva USER999:999 y añade un
entrypoint específico CPU sin gosu, chown, chmod, usermod ni fallbackroot.
Comprueba directorios y configuración como UID999 yexec elcomando recibido.
La caché **interna de laimagen** se copia con propietario999 durante construcción;
no se cambian permisos de bindmounts. Cambiar ENTRYPOINT borra elCMD heredado en
Docker: por eso se declara explícitamente el Uvicorn original, sin alterar argumentos.
Modelos, módulos, UI, dependencias, variables ylímites siguen iguales.

`candidate-lock.json` identifica la imagen concreta validada ylos archivos fuente.
`build.sh` verifica la imagen base yconstruye exclusivamente untag nuevo, sinpull.
No hay USERroot ni RUNprivilegiado enelDockerfile de esta corrección.

## Validación reproducible

1. Confirmar D081healthy, agenteactivo, sininferencia, margen RAM/disco ybackups.
2. `access-audit.py` se ejecuta por elentrypoint real delcandidato contra losbinds
   originales enun contenedor sinred, solo para stat/access/openO_RDONLY.
   No es una prueba de arranque deAPI; no escribe en losdatos originales.
3. `prepare-fixtures.py` dentroCT627 crea copias privadas independientes de los
   tresbinds, con modos/propietarios idénticos. DB medianteSQLitebackup coherente,
   no copiarWAL vivo; rechaza symlinks fuera delclon. Nunca sobrescribe unfixture.
4. `full-startup-test.py` enPVE deriva Compose delreal. Usa la imagen fijada,
   USERimagen999 sinoverride, ENTRYPOINTyCMDUvicorn reales, mismasvariables,
   mounts internos/modos ylímites/capacidades. Solo sustituye fuentes de binds por
   lascopias, nombre/proyecto, networknone/sinpuertos yrestartno. Ningún servicio
   se conecta aSQLite productiva. No usar --entrypoint/python para esta prueba.
5. Esperarhealthy, comprobarPID1UID/GID999 yCapEff/CapPrm0, módulos/configuración,
   DBlectura/escritura conrollback ydirectoriosRW. Health debe mostrar modelo no
   cargado. Parar solo elcontenedor de prueba yverificarPID0. Conservar logs privados.
6. Ejecutar unittest D083/D085 ytestsUI existentes. `api-fixture.py` delcandidatoD085
   se ejecutó complementariamente por esteentrypoint usandoelComposeaislado;
   14API/8envíos deefectos/4DSP sintéticos pasan. No sustituye la prueba Uvicorn.
7. Comparar original frente albaseline: mismoDockerID/inicio/imagen/fuentes,
   agente,111archivos y27configs, SQLite/perfiles/WAV/checkpoints ypermisos reales.

Las copias privadas están en `/srv/voicebox/chatterbox-d085/startup-validation`,
protegidas por0700 ycon datos personales. **No incluirlas en Git, imagen ni contexto
Docker**; elcontexto deconstrucción es solo startup-fix. Se conservan para revisión,
con elcontenedor deprueba parado. No se hanmovido modelos ni reducido almacenamiento.

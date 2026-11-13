# Fase 7.4 — D086: corrección de arranque sin privilegios

12 de noviembre de 2026, Europe/Madrid. **Implementación candidata y validación
real aislada DONE. Despliegue productivo TODO, no autorizado en esta intervención.**
D081 permanece ACCEPTED / PRODUCTION yhealthy. A/B/C no ejecutados; sininferencias,
commit ni push. Esta corrección sustituye expresamente la propuesta anterior de
arrancar comoroot: el propietario exige UID999 desde elinicio y se conserva.

## Causa e inspección antes de modificar

El candidato D08519af4754… declaraba USER999:999 yheredaba unentrypoint que
intentaba `gosu voicebox`, además depreparaciones depropietarios/grupos.
El cambio deusuario/grupos falla sin privilegios yprovoca elmensaje engañoso
sobre `/app/data` no escribible. No era unproblema depermisos de laBD.

Se revalidó elrollback: D08109774c5b… healthy, agenteactivo ysintrabajos. Seleyeron
Dockerfile, USER/ENTRYPOINT/CMD deambas imágenes, script heredado yCompose real.
Compose no fuerzausuario, por loque rige elUSER de laimagen. Susvariables,
montajes ylímites se guardaron privadamente para reproducirlos enlaprueba.

Auditoría conUID999 sobre losbinds reales, sin escrituras:

| Ruta | Propietario/modo | Resultado |
| --- | --- | --- |
| /app/backend yconfig/módulos |999;dirs0755,py0644|Lectura/importación posibles|
| /app/data ycache/profiles/generations |999:999;0755|RW ytravesía permitidos|
| /app/data/voicebox.db |999:999;0644|AperturaRO ypermisoRW comprobados|
| /qwen-jobs |999:999;0700|RW ytravesía permitidos|
| CacheHuggingFace montada |999:999;0755|RW permitido|
| /home/voicebox/.cache interno |root:root;0755|Sololectura paraUID999|

La única preparación depropietarios necesaria está dentro de laimagen: elpadre de
lacaché. No se cambió chmod/chown, ACL niusuario de losvolúmenes reales.

## Corrección implementada

[Dockerfile](../../services/infra-voicebox/startup-d086/Dockerfile) y
[entrypoint-uid999.sh](../../services/infra-voicebox/startup-d086/entrypoint-uid999.sh):

1. Se mantiene **USER999:999**, sin USERroot ni capacidades adicionales.
2. ENTRYPOINT propio comprueba UID999 yacceso a directorios, módulos/config yBD;
   crea solo losdirectorios necesarios cuando sea posible con eseUID y ejecuta
   `exec "$@"`. No contiene gosu/chown/chmod/usermod, adaptación deidentidades ni
   fallbackprivilegiado. Si faltan permisos, falla con unmensaje claro.
3. `COPY --chown=999:999 home/ /home/voicebox/` prepara eldirectorio .cache interno
   durante laconstrucción. No actúa sobre ningún bindmount ni sobre datos reales.
4. Se declara explícitamente elCMDoriginal:
   `uvicorn backend.main:app --host 0.0.0.0 --port 17493`.
   Docker borra elCMDheredado alredefinir ENTRYPOINT; la comprobación previa de
   metadata detectó esa pérdida yse preservó antes de arrancar laAPI aislada.

No se cambian backend, UI, dependencias, lenguajes, referencias, modelos,
parámetros de generación, recursos ni guardas. Imagen nueva validada:

`local/voicebox:d086-uid999-candidate`

`sha256:212703647c03d428adc30f8bf4b864af82690eb41f4fe8ca052ff10dbaa45386`

BaseD08519af4754… eimagenD081 conservadas. El[lock](../../services/infra-voicebox/startup-d086/candidate-lock.json)
recoge hashes de fuentes yconfiguración. Elentrypoint heredado no se modifica
ni se vuelve autilizar para elcandidato nuevo.

## Prueba real delarranque

[full-startup-test.py](../../services/infra-voicebox/startup-d086/full-startup-test.py)
usó laimagen anterior, **su ENTRYPOINTreal ysu CMDreal deUvicorn**, sin override
--entrypoint ni ejecución directa dePython como prueba sustitutiva.

Se derivó Compose delservicio real yse comprobaron automáticamente:

- Misma imagen candidata que se propone para producción yUSER999 sinoverride.
- Mismasvariables explícitas, módulos, configuración yCMD.
- Mismasrutas internas ymodosRW de lostresbinds: /app/data, cachéHF y/qwen-jobs.
- Mismoslímites3CPU/6200MiBDocker/6600MiBDocker+swap yconfiguración decapacidades,
  Privileged=false, sinCapAdd niSecurityOpt adicionales.
- Las fuentes host son **copias privadas**, manteniendo propietarios/modos ydatos;
  SQLite mediante backup consistente. Las17symlinks están confinadas alfixture.
  No se arranca una segundaAPI sobre laSQLite ni losjobs productivos.
- Solo cambian para aislamiento: nombre/proyecto, fuentes privadas de losbinds,
  networknone/sinpuertos publicados yrestartno (para impedir bucles dereinicio).

Estas diferencias están declaradas: no se afirma haber arrancado otroservidor
sobre losbinds productivos. ElaccesoUID999 a lasfuentes reales se verificó aparte
por elentrypoint corregido con auditoría sin escrituras; laescritura efectiva,
transacciónSQLite yWAL se comprobaron en lascopias aisladas.

## Resultados

| Comprobación | Resultado |
| --- | --- |
| ArranqueUvicorn porentrypoint real |**healthy**|
| PID1 yproceso deauditoría |UID999/GID999|
| CapEff yCapPrm |**0000000000000000**, sinprivilegios efectivos/permitidos|
| Parentcache interno |Propietario999 yRW|
| Módulos/configuración |Accesibles eimportables porUID999|
| BDclonada |integrity_checkok, lectura ytransacción deescritura conrollbackPASS|
| Directorios requeridos |PruebaRW efectiva en copiasPASS|
| Perfil/referencia/historial enfixture |1/1/6 conservados|
| Modelocargado |false;0inferencias|
| Prueba conbinds reales |UID999, acceso a archivos/metadatos;0escrituras|
| Terminación delcontenedor de prueba |Parado/PID0; sinprocesosresiduales|
| D081 durante ydespués |MismoID,inicio,imagen yhealthy|

Las pruebas anteriores también pasan:10PythonD083+11PythonD085 y4UID083+5UID085,
**30tests locales**. Enlaimagen corregida, pasando también por suentrypoint,
14comprobacionesAPI,8envíos deefectos y4DSP sintéticos PASS. Son pruebas
complementarias con dobles/DBtemporal; no se confunden con elarranque real anterior.
No se usó voz personal ni se ejecutó inferencia para esos tests.

## Preservación yseguridad

Verificación final originalcontra baseline:

- D08109774c5b… healthy, agenteoriginalactivo, mismoDockerID/inicio yPIDCT.
-111archivos protegidos y27configsPVE idénticos; otros17LXC sin cambios.
- Perfiles, referencias, historial, checkpoints yWAV originales intactos por
  checksums yhuellas lógicas deSQLite. Permisos reales UID/GID/modos sin cambio.
- Rootfs100GiB,3vCPU,15GiBRAM,2GiBswap yguardas existentes intactos.
- Sin nuevosOOM; memory.eventsconserva high251/max367 heredados,OOM/kill0.
- Thinpool libre124.151GiB/31.03%, más del20% mínimo.
- Sin nuevosservicios ni puertos, sinreinicios deVoicebox productivo niCT627.

Elcontenedor deprueba se conserva parado ylosfixtures privados para revisión:
`/srv/voicebox/chatterbox-d085/startup-validation` (0700, contiene copias personales).
No forman parte delcontextoDocker, imagen oGit; no se hanborrado backups ni modelos.

## Estado ysiguiente paso

**Corrección dearranque validada exclusivamente enaislamiento.** No se hapublicado
laimagen como versiónfinal ni desplegado enproducción. No se ejecutaron A/B/C.
La fidelidad yviabilidad real delnuevo motor continúan pendientes deesosensayos.

Unpróximo despliegue necesita nuevaautorización ydebe usar eldigest21270364…,
actualizar/revisar eldestino ycontexto de lareceta coordinada (laantigua fija19af…),
revalidar backups yreadiness yconservar rollback D081. No seguir lapropuesta
anterior deUSERroot. Los[pasos reproducibles](../../services/infra-voicebox/startup-d086/README.md)
yfuentes quedan preparados sinoperar elservicio productivo.

## Evidencias

[Validación completa](evidence/2026-11-12-d086-startup-validation.json),
[permisos anteriores](evidence/2026-11-12-d086-startup-access-before.json),
[acceso porentrypoint corregido](evidence/2026-11-12-d086-startup-access-fixed.json),
[fixtures](evidence/2026-11-12-d086-startup-fixtures.json),
[configuración real yrecursos](evidence/2026-11-12-d086-startup-resources.json).

Sin despliegue productivo, inferencias, modificaciones deotrosLXC/pipeline,
commit ni push. Intervención detenida para revisión.

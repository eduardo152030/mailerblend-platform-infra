# Voicebox productivo — Qwen desacoplado D077

> Antecedente histórico. La operación aprobada se rige por
> [D082](../release-d082/README.md). No ejecutar un despliegue de esta carpeta
> para sustituir automáticamente la versión aceptada.

Web: http://192.168.1.127:17493. Perfil **Eduardo — Mi Voz**, motor **Qwen**, tamaño
**0.6B**, idioma **español**, semilla42 o vacía, personalidad desactivada. Máximo1200
caracteres por trabajo, presupuesto nominal900s. No se modifica el pipeline de vídeos.

La voz y el texto de la muestra10,8s están aceptados por el propietario. El archivo
figura en su historial: http://192.168.1.127:17493/audio/225c8772-6b09-52b0-9580-c0001fff4bcb.
Esto no valida todavía narraciones55–60s. [Informe](../../../docs/roadmap/PHASE7-D077-PRODUCTION.md).

## Flujo

Voicebox mantiene UI/API/historial/descarga y una cola serial. El adaptador no carga
modelos, no divide textos Qwen y no reintenta automáticamente. Una cola privada en
`/srv/voicebox/qwen-worker/jobs` conecta con `voicebox-qwen-627.service` en PVE, sin
puertos nuevos ni Docker socket en la aplicación. El agente solo gestiona CT627.

El agente conserva los supervisores/guardas de D077: A→checkpoint persistente→PID0
y cgroup vacío→B, solo decoder300/context25. Worker9GiB duro/sin swap, guarda8,2GiB,
CT9,5GiB, swapCT delta128MiB/techo1920MiB, PSIlocal5%/10s y márgenes físicos del
host. CT sigue3vCPU/10GiB/2GiBswap; app conserva6200m/6600m. No precarga Qwen en
Voicebox: `model_loaded=false` en reposo es correcto. El supervisor tiene su propia
disponibilidad en `GET /qwen-worker/health`.

Checkpoint, texto, eventos y métricas quedan en el job UUIDhex, directorio700 y
archivos600, UID999 del CT. B monta checkpoint en solo lectura por ambas rutas,
carga únicamente `decoder.*` y conserva los códigos si falla. Cancelar en Voicebox
escribe señal, el supervisor mata su cgroup, espera PID0 y conserva el checkpoint.
Un fallo o reinicio del agente no vuelve a ejecutar Talker; la recuperación de B
requiere revisión operativa. No usar "retry" esperando que repita A.

## IaC y mantenimiento

Desde `terraform/proxmox`, únicamente con autorización del alcance correspondiente:

```bash
python3 services/infra-voicebox/production-d077/stage.py
python3 services/infra-voicebox/production-d077/deploy.py
```

`stage.py` copia fuentes revisadas y construye candidato sin sustituir la app.
`deploy.py` exige backup, prueba la fábrica real como UID999 antes de mutaciones,
habilita el agente dedicado y sustituye solo Voicebox; falla con rollback a la
imagen/Compose anteriores. Aplicación idéntica: no recrea Voicebox ni reinicia agente.
No usar `make deploy-all`. El deploy.sh heredado detecta el lockD077 y solo reconcilia
la app, sin preparación histórica de modelos; exige supervisor ya disponible.

```bash
python3 services/infra-voicebox/production-d077/rollback.py
```

Rollback deshabilita solo el agente627 y restaura el Compose/imagen originales.
No restaura el DB antiguo por defecto: conserva nuevos audios, historial y checkpoints.
Backup previo: `/opt/voicebox/backups/d077-production-before.tar.gz`, copia externa y
restore SQLite/manifest verificados. Imagen productiva archivada fuera de CT; lock
fija su hash y preserva íntegro el lock anterior en `rollback`.

El agente inicia mediante systemd, con7–8MiB residentes observados y límite256MiB.
No modificar fuentes mientras hay trabajos activos. Una caída completa de PVE o
Docker requiere comprobar procesos y estado antes de reanudar. Solo se retiran los
contenedores efímeros propios con label `d077.root`; nunca limpiezas globales.

La publicación de la muestra aceptada es idempotente y **no genera audio**:
ejecutar `publish_accepted.py` dentro de Voicebox con `docker exec -u 999:999 -i ...`.
Exige UID999, hash exacto y perfil real; no crea perfiles. No ejecutar como root.

La observación posterior180s/7muestras y23 tests del runtime pasaron. La API se
verificó con historial/descarga idéntica y rechazo de1.7B; no se realizó una segunda
inferencia por API. La primera generación nueva desde la UI/API será el recorrido
real completo de la integración. Prometheus9090 tenía una incidencia previa y no se
reparó; no confundir salud local/dependencia con validación de la cadena central.

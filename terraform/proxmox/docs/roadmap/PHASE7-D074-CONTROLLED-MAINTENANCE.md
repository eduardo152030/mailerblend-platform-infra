# Fase 7.4 — D074: preparación de mantenimiento CT627 y revisión cAdvisor618

## Estado vigente — limpieza aprobada y ejecutada

105/105 elementos retirados:61rutas+44cacheIDs del manifiesto aprobado inalterado.
Libre7,056→18,997GiB,+11,941GiB reales. No modelos/imágenes/contenedores/voz/volúmenes
ni backupscomprimidos retirados. Voiceboxhealthy/GrafanaPromPASS/59UP,0alertas/OOM
nuevos; CT618 no modificado. No cambios derecursos/reinicios/commit/push.
Preflight yauxiliaresSQLite creados en la verificación anterior se explican en
[ejecución](evidence/2026-11-11-d074-execution.json) y
[diagnóstico posterior](PHASE7-D075-QWEN-HYPOTHESES-PHASE-A.md).

## Preparación histórica, anterior a la aprobación


Estado: **preparación DONE; ejecución BLOCKED — pendiente de aprobación del propietario**.
11nov2026, Europe/Madrid. Fase7.4 INPROGRESS. No borrados, cambio de recursos,
reinicio, actualización, commit/push ni inferencia. D074 pide aprobar lista exacta
antes de eliminación y detenerse antes de cambiar memoria. La voluntad expresa de
seguir pruebasQwen se conserva como siguiente objetivo; no se ejecuta durante esta
preparación previa ni se condiciona a corregirCT618.

## Decisión presentada para aprobación

Retirar exclusivamente las **105 entradas de la [lista exacta](PHASE7-D074-CLEANUP-LIST.md)**,
**11.946GiB potenciales**. El propietario debe aprobar
esa versión antes de cualquier acción material. [ManifiestoJSON canónico](../../services/infra-voicebox/maintenance-d074/cleanup-manifest.proposed.json),
SHA256 `d2396813e51c98e171052f0bc8765c69476467db53b098d89727954474fc8b00`. Nada fuera de su allowlist.

| Grupo propuesto | Entradas | Bytes | GiB potencial |
|---|---:|---:|---:|
| CacheBuildKit no compartido/no activo |44|4485183669|4.177|
| Temporales APT y fuente públicaD072 |47|613232640|0.571|
| Expansionesbackup duplicadas |14|7728578560|7.198|
| Total |105|12826994869|11.946|

No sumar capas/imágenes compartidas. Espacio actual~7,06GiB; aproximación tras
retirar todo aprobado~19,00GiB disponibles, no garantía de liberación física inmediata
ni recuperación exacta del disco previo a todos los modelos. Ningún ahorro deRAM
se atribuye a borrar contenedores parados o archivos en disco.

## Backups comprobados antes de proponer retirada

14/14 parejas expansión↔tar **IDENTICAL**, incluidas longitudes/contenidoSHA256,
permisos ydestinos de symlink confinados. 14/14 manifiestos dearchivos válidos,
14/14 SQLite integrity_checkok. Catorce archivos externos en almacenamiento privado
del propietario, fueraPVE/CT627, tienen exactamente el mismoSHA256 y tamaño que
cada comprimido retenido enCT. No solo coincidencia de nombres. Se recorrieron los
tars sin extraerlos en producción, con baja prioridadCPU/IO; sin modificar backups.

Se conservan **dos copiascomprimidas** de cada expansión propuesta: una dentroCT y
otra fuera, más datos/modelos productivos. Losdirectorios D071-before,D070-cancel,
D069-acceptance no forman parte de la retirada. Audios/referencias históricas
contenidas en expansiones permanecen en amboscomprimidos; eloriginal y perfil vivos
no se tocan. No eliminar única copia recuperable. Restoreprevio ycontenido verificados,
no un nuevoDR productivo; revalidar otra vez antes deejecutar.
[Comparación ycopias externas](evidence/2026-11-11-d074-backups.json).

## Docker: candidatos y exclusiones

44cacheIDs exactos InUse=false/Shared=false, probados por selector allowlist de
`docker buildx du` en Buildx0.30.0. Ningúnprune ejecutado. La API puede no liberar
algunos padres hasta que desaparezcan sus referencias; detener/omitir, no ampliar
el selector. Nunca borrar `/var/lib/containerd` ni capas por su ruta, ni hacer
`docker system prune`, limpieza globalbuilder o `down -v`.
[Prueba read-only del selector](evidence/2026-11-11-d074-cache-selector.json).
[Filtrado porID documentado](https://docs.docker.com/reference/cli/docker/buildx/prune/).

Imágenes antiguas identificadas pero **EXCLUIDAS de esta aprobación**:

| Imagen | ID completo | SizeEngine bytes | UniqueEngine bytes |
|---|---|---:|---:|
| `local/voicebox:openvoice-d071` | `sha256:70dd4896a1e8d4349c2a7c66f03623e992f092f0e435a1efc4b051e88bbe7d5e` | 5360567499 | 1298445515 |
| `local/voicebox-openvoice:d071` | `sha256:5bd20f32e2bdd221f5db2e36a8288d8f46606df2cd467a51d97272cae425d19b` | 3145176674 | 2991011426 |

OpenVoiceapp rechazada no tiene contenedores referenciándola; worker tiene su
contenedor parado `voicebox-openvoice`. No son dependencias deVoiceboxD069, pero no
se ha preparado unexportexterno deesasimágenes con blobs/restoreverificados; por
ello no se proponen borrar hoy. Sus tamaños no son ahorro garantizado y no se suman
al grupo105. Trece contenedores de ensayos parados, imágenesD066/PiperR1 y derivados
se conservan para auditoría/rollback por ahora; writablelayers totales~5,7MB no
justifican retiradas apresuradas. cAdvisor/test-nginx activos no son candidatos.
QwenC:d072 se conserva para las pruebas pedidas. ModeloCustomVoiceaislado y modelos
OpenVoice también se conservan, aunque no sean prioritarios.

ProducciónD069, rollbackR2 y originalD063, bindings/volúmenes, HF/modelos funcionales,
data/SQLite/historial/perfil/referencias/private-originals, muestrasnecesarias,
prompts/D072private/jobs, recetas/locks y archivoscomprimidos quedan protegidos.
No se modifica Compose ni se desinstalan motores. ElbuildpúblicoD072 se recupera
del archivoidéntico comprobado fueraCT; no contiene la referencia personal privada.

## CT618: cAdvisor inspeccionado, no modificado

Contenedor `7a110a7339fe9762643a954d11511e0002fb5708773ad06baa9f59d8f8aec4dc`,
imagen `sha256:b8e7d1093144fd088f425ff003d75a4aa405de075db78dae3bc563730b1bd07a`.
Running/healthy, reinicios0,StartedAt2026-11-06T19:22:41.858910316Z,OOMKilledfalse.
Límite efectivo134.217.728B=128MiB;MemorySwap268.435.456B=RAM+swap, luego128MiB
adicionales deswap permitidos; CPU0,50, reserva0. CT6186GiB no se cambia.

Cgroup actual134.119.424B≈127,91MiB;swap6.070.272B≈5,79MiB. Componentes de esta
muestra: anon10.543.104B,file5.001.216B,kernel118.312.960B. Elcargo kernel domina;
no confundirlo con heapGo ni suponer fuga delproceso. En10s,+63eventosmemory.max,
0OOM/oom_kill nuevos. PSIfullavg10~1,01%; dato informativo, **no veto nuevo al objetivoQwen**.

HistóricoPrometheus24h, selector real `instance=192.168.1.118:8085` (el targetlegacy
no tiene labelvmid):

| Métrica | Resultado |
|---|---:|
| min(up)24h | 1.0 |
| Scrapes presentes24h, cadencia30s | 2880 |
| RSSproceso actual | 16547840B / 15.78MiB |
| RSSproceso máximo24h | 27512832B / 26.24MiB |
| WorkingSetcgroup actual | 131952640B |
| WorkingSetcgroup máximo24h | 133967872B |
| Usagecgroup máximo24h | 134221824B |
| Antigüedad container_last_seen al comprobar | 17.85s |

Usagehistórico puede superar unosKiB el límite por momento/contabilidad; no implica
cambio del límite. Disponibilidadexporter y frescuraPASS no validan de nuevo todas
las cadenasCPU/Telegram. No modificar contratosF4 aceptados. Budibase/CRM/API ytodos
los demás contenedores mantienenID/imagen/StartedAt/restarts.

**Propuesta opcional:** probar exclusivamente cAdvisor618 con256MiBRAM yMemorySwap
384MiB total, conservando128MiB de swapadicional yCPU0,50, sin modificar CT ni apps.
Margen razonable frente al límite tocado repetidamente, **no necesidad demostrada
por caída ni garantía de working-set óptimo**. IaClocal preparada, NOdesplegada:
[cadvisor-618-limits.proposed.yml](../../services/infra-voicebox/maintenance-d074/cadvisor-618-limits.proposed.yml).

Aplicaría solo como overlay de la pila exacta618 existente, cuyos tres archivos
Compose están en la evidencia. No editar el fichero común128m del resto deCT.
Antes de aplicar, permisoespecífico,backup deconfig eidentidadimagen yrollback a128m;
recrear únicamente cAdvisor usando el mismoproyecto, sin `up` global, sin recrear apps.
Después600s/21muestras de memoria/events/scrapes, última muestra fresca≤45s,
sin nuevosOOM/gaps/alertas ni cambios a hermanos. No ejecutar ese procedimiento hoy.
No es una condición impuesta a Qwen ni autorización implícita de rolloutF4.

## Validación y estado final

[Verificación final](evidence/2026-11-11-d074-final.json): Voiceboxhealthy,mismoID,
imagen e inicio queD073, ningún modelo cargado; perfilEduardo único y hashes de
original/referencia conservados, módulos/modelosKokoro/Piper disponibles. WAVsPASS
D072 legibles; no nueva inferencia enD074 ni afirmar una nuevaUAT. Sin nuevas
escrituras alhistorial.18Node/18cAdvisor y59targetsUP; sin nuevosOOM ni alertas.
Persiste HostDiskFilling627FIRING anterior: mantenimiento aún no ejecutado, no declarar
el disco reparado.27configuracionesPVE yotros17CTgestionados sin cambios. Sin cambios
al pipeline, recursosCT, servicios oGitremoto; sin commit/push.

Scripts de auditoría en `services/infra-voicebox/maintenance-d074/`, ejecutados por
stdin en remoto, sin desplegar archivos ni herramientas de eliminación. Manifiesto
yoverlay son preparación local, no mantenimiento ejecutado. Python/enlaces/diffcheck
validados. **Detenido antes de eliminación y cambio de memoria**, como solicitaD074.

Siguiente: aprobación expresa de la lista105/hash indicada; después ejecutar únicamente
esealcance, validar espacio/servicio/monitorización y continuar el objetivoQwen bajo
los límites ya fijados. CT618 tiene propuesta separada, no incluida en esaaprobación.

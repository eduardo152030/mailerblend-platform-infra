# Recetas acotadas IA-CHAT

Fuente de recursos: `inventory/services/infra-llm.yml` e `infra-webui.yml` y recurso
Terraform `svc`. Configuración de apps en `services/infra-llm/{config,systemd}` y
`services/infra-webui/{compose,config}`. Los enlaces de `services/ia-local` mantienen
compatibilidad, sin duplicar la configuración. `provision.py` y su inventario son
**históricos del bootstrap**; no ejecutarlos después de adoptar Terraform.

## Estado adoptado y revalidación

SSH PVE estricto siempre, usando `$HOME/.ssh/known_hosts`, comprobación obligatoria
y BatchMode. CA pública PVE obtenida mediante ese canal; TLS verificado en Terraform.
Nunca mostrar estados, planes, credenciales ni configuraciones expandidas de Compose.

```sh
python3 scripts/generate-lxc-inventory.py
terraform validate
python3 scripts/ia-chat/adopt-terraform.py
```

El último comando guarda una copia privada de estado antes de importar exclusivamente
630/631 si faltan, y prepara un plan con dos targets. No hace apply. El resultado
esperado tras adopción es `no-op` para ambos. Los planes/estado/CA y configs SSH están
en `~/.local/share/mailerblend-recovery/ia-chat/`, fuera Git. `apply-adoption.py`
solo admite actualizaciones de metadatos/flags revisados de esos dos recursos;
rechaza creación, eliminación, redes, recursos y volúmenes. No usar apply global.
Se conserva el estado de todos los recursos anteriores sin refrescarlos.

## Reconstrucción de los CT nuevos

Antes de recrear, comprobar ID libre, capacidad física, backup y autorización de
recuperación; nunca destruir un CT para comprobar la receta. El módulo permite
creación desde `os.template_file_id`, en vez de clonar CT106; no privilegiados yDHCP.
El selector `mount_points.volume=local-lvm` crea volumen60GiB; su identidad asignada
no se reescribe después de importar. Tamaño/ruta/RO/backup siguen declarados.
Plantilla Debian12 se obtiene con pveam y checksum; conservar las MAC declaradas.
Preparar SSH público mediante `scripts/lxc_ssh.py` y pasar el archivo privado
`ssh-bootstrap.auto.tfvars.json`; no copiar claves privadas ni reemplazar claves
existentes. En630, `normalize-ssh-630.sh` selecciona SSH en modo servicio para evitar
conflicto con ssh.socket; el timeout60s admite la limitación logind del LXC sin
relajar AppArmor. Ejecutar bootstrap SSH con `--config ... --node pve --execute`.

1. Alta mediante plan Terraform limitado a esos dos CT, revisar antes de aplicar.
2. Excepción631: ejecutar en PVE `apparmor-631.py` solo bajo autorización registrada.
3. En630: `build-llama.sh` y `download-models.py`. Durante descarga el volumen nuevo
   debe estar RW: usar override acotado de `read_only` en YAML/plan, descargar,
   comprobar los cuatro bytes/SHA y devolverlo aRO mediante plan antes de servir.
   No cambiar el mountpoint de ningún otroCT. Guardar el manifiesto en/root/ia-local.
4. En631: `install-webui.sh`; copiar Compose, CSS y plantilla SearXNG a/opt/ia-chat.
   `prepare-secrets.py` enPVE crea las claves600 exclusivamente en630/631.
5. `bench.py` enPVE requiere llama-server detenido y MemAvailable host>=21GiB por
   carga; no repetir resultados válidos. Usa mmap,repack0,b512,ub128.
6. Copiar preset/unidad, `gemma-cache.jinja`, `performance-tuning.json` canónicos
   y `install-llama.py` a/root/ia-local. La selección r3 versionada configura b/ub
   e hilos sin depender de resultados históricos locales. No reinicia si los bytes
   no cambian. Sin selección, el bootstrap histórico usa benchmarks tg128/pp512.
   Copiar también `config/chat-performance.json` de WebUI a `/opt/ia-chat/`
   y reconciliar perfil persistido según [latencia](latency/README.md).
7. Antes del primer arranque, desde/opt/ia-chat usar
   `docker compose run --rm -T --no-deps --entrypoint python open-webui - < precache-auxiliary.py`.
   Descarga revisiones fijas de embedding/Whisper en el volumen persistente y permite
   auto-updatefalse desde el principio. Después arrancar Compose. Entorno WHISPER_MODEL no sobreescribe el valor deSQLite:
   reconciliar con la API administrativa y verificar el valor efectivo, sin logs
   del export de configuración. Perfil final small/int8.
8. `create-backups.py` enPVE crea solo dos jobs propios y no modifica los ajenos.
9. Monitorización: bundles por servicio en `monitoring/`, generados con
   `scripts/lxc_provisioning.py:render_monitoring`; override631 mem_limit256m.
   `install-repository-monitoring.py` instala solo630/631, con aprobación del socket
   containerdRO exclusivamente631. No instala Docker en630.
10. Crear manifiestos privados de verificación con declaraciones y hashes delbundle;
    `verify-new-lxc.py --bundle <privado> --node pve` valida CPU/RAM/cgroup/IPDHCP,
    puertos y salud. Solo su activación incorpora cpu_contract=lxc_cgroup_v1.
11. `activate-native-alert-contract.py` activa la regla ya prevista para noDocker,
    con backup/parser y recarga acotada. Después `integrate-monitoring.py prepare`
    y`apply`: backup coordinado610/616, restauración aislada, promtool/parserBlackbox,
    integración aditiva y rollback si falla. No sobrescribir transacciones previas.
12. `integrate-grafana.py` modifica únicamente el panel de salud Fleet/Details para
    tratar cAdvisorN/A; backupDB SQLite/config, no restart y comprobaciónAPI.
    `verify-grafana.py` consulta realmente los paneles de630/631.
13. `observe-monitoring.py`:600s/21muestras; HALT ante anomalía, no aceptación falsa.
    Telegram humano/end-to-end no queda acreditado por estas comprobaciones.

## Pruebas, limpieza y cierre

`validate-api.py`, `webui-check.py` y `rag-and-stt.py` prueban API/modelos/visión/
thinking/RAG/STT con guardas. Los datos y el usuario técnico son fixtures efímeras.
`reboot-check.py` enPVE prueba reboot real630/631 con mismoIP/arranque/historial;
requiere todavía la fixture. Después `cleanup-validation.py` retira exclusivamente
nuestro Knowledge/cuenta, conserva modelos globales y prueba JWT401. No borrar un
usuario real ni recrear fixture durante una reaplicación ordinaria.

`idempotence.py` enPVE verifica apps/jobs/configs sin usar ya el creador pct;
complementar con plan Terraform no-op, segunda aplicación de exporters y transacciones
sin escrituras/recargas/restarts. `final-health.py` prueba integridadSQLite, secretos,
RO y27 hashes protegidos. Backup manual631 con `vzdump --remove 0`, comprobarSHA,
zstd/tar/miembros críticos mediante `verify-backup.py`; no equivale a restauración
funcional. Copiar README operativo a `/root/ia-local/README.md` enPVE.

CT627 excluido. Sin commit/push. `install-crun.py` documenta un intento fallido y no
es dependencia activa. No utilizar deploy-all ni política/global rolloutF4.

## Cuota de swap631

La fuente vigente es `inventory/services/infra-webui.yml` (1741MiB).
`resize-swap-631.py --apply --label applied` reconcilia exclusivamente swap631
mediante PVE con digest/backup, sin reinicios. Sin --apply solo consulta.
Repetir con otra etiqueta verifica idempotencia; no imprime configuración privada.
Sincronizar Notes mediante `sync-notes.py --ct 631 --apply --evidence-dir <carpeta>`.
El bootstrap histórico compartido no es otro gestor tras la adopción Terraform.

# Fase 7.4 — D074: lista exacta de retirada propuesta

**APROBADA Y EJECUTADA.** CT627 exclusivamente. Manifiesto original conservado
sin cambios para acreditar la versión autorizada; estado final en
[ejecución](evidence/2026-11-11-d074-execution.json). La lista inferior es histórica,
no autorización para una nueva limpieza.
11nov2026, Europe/Madrid. Versión cerrada de **105 entradas**.
Manifiesto canónico con función, dependencias, motivo, hashes y recuperación por fila:
[cleanup-manifest.proposed.json](../../services/infra-voicebox/maintenance-d074/cleanup-manifest.proposed.json).
SHA256 del archivo: `d2396813e51c98e171052f0bc8765c69476467db53b098d89727954474fc8b00`.

Potencial asignado: **12826994869B / 11.946GiB**.
No es espacio ya recuperado ni garantía deGC inmediata. No se aprueba ningún elemento
no enumerado. No hay imágenes, objetosDocker, modelos, archivoscomprimidos debackup,
datos productivos, referencias, grabaciones, audios ni volúmenes en esta lista.

## 1. CacheBuildKit —44 IDs exactos

Función común: cache de compilación o fuente intermedia. Dependencias: InUse=false,
Shared=false enEngine; número de padres listado, relaciones completas enJSON. Motivo:
no necesarios para contenedores o imágenes retenidos. Recuperación: reconstruir con
fuentes/recetas fijadas preservadas; puede requerir red y no recupera el mismoIDcache.
Retirar solo porAPI/BuildKit con selector exacto, nunca borrar capas en filesystem.

| ID exacto | Bytes Engine | Padres |
|---|---:|---:|
| `039alvv69vqij5mff04cogfrm` | 8192 | 0 |
| `3ae7a6z9mz6ejuutx0el17fzv` | 19148800 | 0 |
| `4bd4pyd4hdd0nhkckehl579ko` | 8702231 | 0 |
| `54vwu56n1a25dpjog5toqhaez` | 34181120 | 0 |
| `bjsvmdgfxurqb5uby8woo69do` | 8192 | 0 |
| `bmp44895rjk9a482c29s35mbw` | 1056 | 0 |
| `c8y5ng4p4puj2vsivznf7fi62` | 24576 | 0 |
| `cc9n4utgqdchqqwkkaowoc7bo` | 8192 | 0 |
| `ckx618zyxh8gf1z2h4g7vbuwl` | 131072 | 0 |
| `csgmb5j530kcenivtgninhunz` | 4096 | 0 |
| `dm0nj6zng24s5yercokonuco7` | 6254592 | 0 |
| `gflyfzpl88hsudhu22u1me329` | 85310 | 0 |
| `gso88dg822qbaouurn2mdzyvv` | 12288 | 0 |
| `ia05deh12n2b09zy63ry71cr5` | 1175552 | 0 |
| `iecwav88rnakc534ho6kdx44d` | 30357 | 0 |
| `igqfbnlbh5h0w49f2vcv6y2ge` | 4096 | 0 |
| `izf9jojw8vhnmxdmvzqhqbocc` | 160298852 | 0 |
| `juwdbj3w0h1m5w7y7fb7zm28v` | 4096 | 0 |
| `m06hro4yqlgi3w5xmvtdba5ul` | 372482048 | 0 |
| `npsywgtu46d918ewtarcocvhr` | 69632 | 0 |
| `o4cara27r6xgeip6ioq3hyk2m` | 18503 | 0 |
| `onodw9o3mmfdvi2gi3mvw9z7b` | 183619542 | 0 |
| `p4lpjueruejdj7kjeynldore6` | 16522 | 0 |
| `p57xn6tjk145ua7ai9ygnumen` | 43065344 | 0 |
| `pv2ejpcwgqbwwqltompg5jgpz` | 10956976 | 0 |
| `qdj9f4op8n66y83psh9cpdrow` | 886632448 | 0 |
| `qsvfdye9j2pc23kmttkcz3oy8` | 8192 | 0 |
| `rex6zrysjqaamsn7reyjmv3er` | 559601 | 0 |
| `rvkt9214mj3g5wznu9189ranw` | 12288 | 0 |
| `t2hntshb853fcdq312mhhu252` | 16569 | 0 |
| `tfu156dm92c16g9joljhfqvcr` | 379080704 | 0 |
| `tnbwgnly6upuc3zjvjbsxhngw` | 2737889 | 0 |
| `ukbakly9s718meud8uqj81953` | 35807232 | 0 |
| `unsi4ucvwqsoce23ydt0iui0g` | 20776 | 0 |
| `urvgdoi2v7hia5zxqsynmd7w0` | 6524928 | 0 |
| `vnpkmjsn7luvj5i0sssnbetbh` | 16384 | 0 |
| `vp6u93en3eic8dmb5zlit4kq0` | 75698176 | 0 |
| `vxqizx2mgs78mqxz2tj1ki420` | 35799040 | 0 |
| `vz5wfmecnxdgtv6mbf1zq0eho` | 2221535232 | 0 |
| `wdy9ouimdqccec56oo8joecru` | 12288 | 0 |
| `wefuzeqs45zfb18h7f4o877d7` | 13233 | 0 |
| `y3w4g40it5ar3ravtm3jwq0wa` | 168076 | 0 |
| `yxvelzf4s39xc49b7o8yom63h` | 8192 | 0 |
| `zgd6mtif62swkdadnrxv6ysos` | 221184 | 0 |

Selectorallowlist probado solo con `docker buildx du`, selecciona exactamente44IDs.
Volver a comprobar Shared/InUse ydependencias antes de ejecutar; omitir/detener ante
deriva, no ampliar a otrosIDs ni usar opciones de limpieza por espacio/antigüedad.

## 2. Temporales —47 rutas exactas

APT: índices/cache regenerables, no paquetes instalados. Dependencias: ninguna tarea
APT/dpkg/unattended-upgrades activa al retirar; locks/partial/directorios excluidos.
Motivo: regenerables y no requeridos por Voicebox. Recuperación:apt-get update o
regeneración de cache, con red si hace falta. SHA256 por archivo enJSON.
BUILD: solo fuente pública y archivo de construcciónD072, sin private/ ni jobs/.
Dependencias: no bindmount de aplicación; copia tar idéntica fueraCT627 verificada
SHA256 `d952e340793de62b5ddd6e4fa7e54501fe99eeff2cd820c84819abd76dd8e1ee`.
Recuperación: archivo privado fueraCT627 y fuentes públicas fijadas.

| Ruta exacta | Bytes asignados | Función/recuperación |
|---|---:|---|
| `/srv/voicebox/pilot-d072/build` | 75702272 | BUILD |
| `/srv/voicebox/pilot-d072/build.tar.gz` | 58822656 | BUILD |
| `/var/cache/apt/pkgcache.bin` | 71389184 | APT |
| `/var/cache/apt/srcpkgcache.bin` | 71348224 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-security_InRelease` | 131072 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-security_main_binary-amd64_Packages` | 21028864 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-security_main_cnf_Commands-amd64` | 61440 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-security_main_i18n_Translation-en` | 15749120 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-security_multiverse_binary-amd64_Packages` | 593920 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-security_multiverse_cnf_Commands-amd64` | 4096 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-security_multiverse_i18n_Translation-en` | 167936 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-security_restricted_binary-amd64_Packages` | 38289408 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-security_restricted_cnf_Commands-amd64` | 8192 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-security_restricted_i18n_Translation-en` | 25047040 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-security_universe_binary-amd64_Packages` | 6225920 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-security_universe_cnf_Commands-amd64` | 184320 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-security_universe_i18n_Translation-en` | 2662400 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-updates_InRelease` | 131072 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-updates_main_binary-amd64_Packages` | 22511616 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-updates_main_cnf_Commands-amd64` | 77824 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-updates_main_i18n_Translation-en` | 16535552 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-updates_multiverse_binary-amd64_Packages` | 622592 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-updates_multiverse_cnf_Commands-amd64` | 4096 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-updates_multiverse_i18n_Translation-en` | 180224 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-updates_restricted_binary-amd64_Packages` | 39866368 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-updates_restricted_cnf_Commands-amd64` | 8192 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-updates_restricted_i18n_Translation-en` | 26079232 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-updates_universe_binary-amd64_Packages` | 7311360 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-updates_universe_cnf_Commands-amd64` | 212992 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy-updates_universe_i18n_Translation-en` | 3145728 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy_InRelease` | 270336 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy_main_binary-amd64_Packages` | 6782976 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy_main_cnf_Commands-amd64` | 114688 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy_main_i18n_Translation-en` | 3084288 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy_multiverse_binary-amd64_Packages` | 921600 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy_multiverse_cnf_Commands-amd64` | 32768 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy_multiverse_i18n_Translation-en` | 503808 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy_restricted_binary-amd64_Packages` | 917504 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy_restricted_cnf_Commands-amd64` | 4096 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy_restricted_i18n_Translation-en` | 233472 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy_universe_binary-amd64_Packages` | 64335872 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy_universe_cnf_Commands-amd64` | 1290240 | APT |
| `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy_universe_i18n_Translation-en` | 29839360 | APT |
| `/var/lib/apt/lists/deb.nodesource.com_node%5f24.x_dists_nodistro_InRelease` | 12288 | APT |
| `/var/lib/apt/lists/deb.nodesource.com_node%5f24.x_dists_nodistro_main_binary-amd64_Packages` | 69632 | APT |
| `/var/lib/apt/lists/download.docker.com_linux_ubuntu_dists_jammy_InRelease` | 49152 | APT |
| `/var/lib/apt/lists/download.docker.com_linux_ubuntu_dists_jammy_stable_binary-amd64_Packages` | 667648 | APT |

## 3. Expansiones duplicadas debackup —14 rutas exactas

Función: copias expandidas históricas, no datos vivos. Dependencias: conservar su
`/opt/voicebox/backups/<nombre>.tar.gz` y la copia externa indicada; mismoSHA256
verificado entre amboscomprimidos. Expansión ytar coinciden en archivos, bytes,
permisos y enlaces. Manifiestos completos válidos ySQLite integrity_checkok14/14.
Motivo: ocupan espacio duplicado de restauración. Recuperación: extraer snapshot de
cualquiera de las dos copiascomprimidas conservadas. No se pierde única copia ni se
retira elbackup comprimido. Checksums detallados enJSON/evidencia debackupsD074.

| Ruta exacta propuesta | Bytes asignados | Copia externa verificada que se conserva |
|---|---:|---|
| `/opt/voicebox/backups/d063-after-tts` | 329515008 | `/home/jainer/.local/share/mailerblend-recovery/new-lxc/voicebox-d063/backup-after-1536.tar.gz` |
| `/opt/voicebox/backups/d063-final-2048` | 330141696 | `/home/jainer/.local/share/mailerblend-recovery/new-lxc/voicebox-d063/backup-final-2048.tar.gz` |
| `/opt/voicebox/backups/d064-before-catalog` | 330301440 | `/home/jainer/.local/share/mailerblend-recovery/voicebox-d064/before-catalog.tar.gz` |
| `/opt/voicebox/backups/d064-before-memory3072` | 332644352 | `/home/jainer/.local/share/mailerblend-recovery/voicebox-d064/before-memory3072.tar.gz` |
| `/opt/voicebox/backups/d066-before-qwen` | 333074432 | `/home/jainer/.local/share/mailerblend-recovery/voicebox-d066/before-qwen.tar.gz` |
| `/opt/voicebox/backups/d067-before` | 333508608 | `/home/jainer/.local/share/mailerblend-recovery/voicebox-d067/before.tar.gz` |
| `/opt/voicebox/backups/d067-before-recreate` | 333516800 | `/home/jainer/.local/share/mailerblend-recovery/voicebox-d067/before-recreate.tar.gz` |
| `/opt/voicebox/backups/d067-final` | 334630912 | `/home/jainer/.local/share/mailerblend-recovery/voicebox-d067/final.tar.gz` |
| `/opt/voicebox/backups/d068-before` | 334635008 | `/home/jainer/.local/share/mailerblend-recovery/voicebox-d068/before.tar.gz` |
| `/opt/voicebox/backups/d068-before-piper` | 411410432 | `/home/jainer/.local/share/mailerblend-recovery/voicebox-d068/before-piper.tar.gz` |
| `/opt/voicebox/backups/d068-final` | 450187264 | `/home/jainer/.local/share/mailerblend-recovery/voicebox-d068/final.tar.gz` |
| `/opt/voicebox/backups/d068-preserved-final` | 450490368 | `/home/jainer/.local/share/mailerblend-recovery/voicebox-d068/preserved-final.tar.gz` |
| `/opt/voicebox/backups/d069-before` | 458395648 | `/home/jainer/.local/share/mailerblend-recovery/voicebox-d069/before.tar.gz` |
| `/opt/voicebox/backups/d069-final` | 2966126592 | `/home/jainer/.local/share/mailerblend-recovery/voicebox-d069/final.tar.gz` |

## Exclusiones y condición de ejecución

Conservar todos los `.tar.gz`,D071-before,D070-cancel,D069-acceptance, imágenes
operativas/rollback y todaimagenDocker, contenedores, modelosQwen/Kokoro/Piper/OpenVoice,
private-originals, perfiles, referencias, generations, caches de prompts, D072/private
/jobs y volúmenes. No retirar archivos no enumerados dentro deotrosdirectorios.

Aprobación deesta lista no aprueba CT618 ni ninguna ampliaciónRAM. Antes de cualquier
eliminación: revalidar versión/hash, identidades y tamaños, copias/restore aplicables,
locks yestadoEngine; abortar ante diferencias. Comprobar API/perfil/originales/modelos,
18LXC/alertas/OOM y espacio antes/después. La lista no contiene un script destructivo.

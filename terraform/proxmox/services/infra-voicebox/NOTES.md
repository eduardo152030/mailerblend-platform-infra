# CT 627 — infra-voicebox

**D081 — ACCEPTED / PRODUCTION; cierre D082.** Voz y contenido aceptados por el
propietario el12nov2026:1059caracteres continuos,57,36s,total676,18s,EOS ycheckpoint
íntegros,picoCT9,625GiB,sinOOM. Alcance≈1min;5–10min no validados. Audio privado.
15GiB RAM/3CPU/2GiBswap/50GiB, Base0.6B FP32/SDPA/3hilos/semilla42/español;
A→checkpoint→B300/context25; guardaCT14GiB,workerhard9GiB/stop8,2;1200chars/900s.
Sin cambios de runtime ni nuevas inferencias enD082. Runbookrelease-d082/README.md.
Pronunciación: trader→tréider comprobado; hola pendiente. No alterar texto original
para subtítulos ni pipeline de vídeos al preparar futuras sustituciones fonéticas.
Los apartados D081/D080 inferiores son antecedentes de las verificaciones.

**D081 consolidación:** configuración D080 conservada yaceptada como referencia técnica
funcional (WAV28,56s). CT15GiB/3CPU/2GiBswap; guardas14GiB/workerhard9GiB,stop8,2.
Operación: Eduardo — Mi Voz, Qwen3-TTS0.6B, Spanish; texto íntegro≤1200caracteres,
unjob serial,900s,sinreintentos automáticos. No confundir selectorUI1.7B con0.6B.
Backup privado D081 incluye datos/checkpoints yfuentes; imágenes exactas archivadas
fueraPVE yverificadas antes delnuevo ensayo. Runbookconsolidation-d081/RUNBOOK.md.

D081 único ensayoUI1059caracteres: EOS718,checkpoint1029x16, WAV57,36s, total676,18s.
Sinfragmentación/reintentos, decoder300/context25; picoCT9,625GiB,swapmáx4KiB,
PSIlocal0/OOM0. Calidad ycuatro diferenciasASR pendientes deescucha; no aceptar
contenido palabra porpalabra automáticamente. Runtimeapp yworker sin sustitución.

**D080 recursos declarados:** 3vCPU,15360MiB RAM,2048MiB swap,50GiB.
Aplicación D079; ampliación D080 verificada sin reinicio, Terraform final0cambios.
Voicebox healthy, Qwen Base0.6B FP32/SDPA mediante procesos A→checkpoint→B separados.
AgentePVE voicebox-qwen-627 solo627, sin puertos nuevos ni socketDocker en laapp.
Workerhard9GiB/guarda8,2GiB; CTguarda14GiB; decoder300/context25; sin retry.
PerfilEduardo real ytranscripción intactos; muestra10,8s aceptada, historial/descarga.
D080 único ensayo continuo573caracteres: EOS358tokens, WAV28,56s, total362,18s;
checkpoint669x16 persistido, A liberado antes B300/context25. PicoCT8,612GiB,
swap4KiB/PSIlocalmax0,36%/OOM0; 55–60s aún pendientes, no extrapolar calidad.
Backup/restore yrollbackimagenoriginal conservados. Prometheus9090 incidencia previa,
no reparado aquí. UI/API LAN192.168.1.127:17493, solo Qwen0.6B/es/semilla42,
personalidad desactivada, hasta1200caracteres/job. Kokoro yPiper conservados.

**Histórico D069 (aplicación conservada):**
Sin cambios de recursos enD069, otrosLXC ni pipeline. Web/API soloLAN192.168.1.127:17493;
ACL LAN existente, sin autenticación individual ni exposiciónWAN.

Perfil único **Eduardo — Mi Voz**, UUID1fd00418-2a79-4178-883f-af6c3f5e07ee,
referencia real8840f5e1-990b-463e-b94e-e72beef61917. Original fueraGit y privado
persistente /srv/voicebox/private-originals0700/0600; transcripción confirmada exacta.
Ocho perfiles adicionales retirados tras inventario ybackup restaurado. Motores y
catálogos integrados conservados; otras voces quedan fuera del alcance actual.

**Base0.6B:** clonación técnica completada: WAV6,40s generado en106,86s,
24kHzPCM16mono, prompt23,85s/tokens41,27s/codec33,37s. Parecido, contenido yacento
aceptados expresamente por el propietario para esta muestra. No narración60s validada ni RTF extrapolado.
Pico observado cgroup5,18GiB, HWM4,68GiB, swap+5,32MiB,VmSwap0,OOM0.
PSIfullmáximo1,72%; límites preventivos6,5GiB/swap64MiB/PSIfull2%. Sin paradas.

Imagen personal-d069 deriva de PiperD068R2; BF16/SDPA,codecFP32,doshilos yguard
porUUID real/referencias/archivos/transcripción. Solo Base0.6B;1.7B yCustomVoiceCPU
bloqueados. UnmodeloTTS, cola serial y409 para mutaciones concurrentes. Chunk200.
DockerCPU3,RAM6200MiB,RAM+swap6600MiB. Imagen anterior conservada para rollback.

**Persistencia:** /srv/voicebox/data DB/perfiles/referencias/WAV/config/Piper;
/srv/voicebox/huggingface Kokoro yBase0.6B fijado5d83992436eae1d760afd27aff78a71d676296fc.
CustomVoice aislado D066 conservado. Catálogo personal en data/voice-identities.yml.
Backups privados fueraPVE; snapshot antesretirada127archivos/25audios restaurado;
ochoZIP recuperables porperfil. No publicar audios/transcripciones/SQLite.

**Operación:** /opt/voicebox/deploy.sh verifica locks yreconcilia soloVoicebox;
personal-config.py no crea perfiles. Reiniciar/recrear soloDocker con mismosbinds;
nunca down-v ni prune. Rollback imagen/Compose sinrevertirBD; datos requieren
snapshotSQLite yarchivos coordinados. Ver evidencias del cierre para persistencia
real ysegunda aplicación. Node/cAdvisor/Blackbox/Grafana conservados para18LXC.

**Docs:** docs/roadmap/PHASE7-D069-PERSONAL.md;docs/inventory/627-LXC-INVENTORY.md;
services/infra-voicebox/VOICE-PROFILES.md. Fase7.4/D069 DONE — Accepted para perfil personal yprimera muestra.
Sin commit/push. Siguiente: uso de vozpersonal; narración larga sinvalidar.

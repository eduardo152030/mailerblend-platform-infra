# D-089 — completar validación tras conectividad

Esta reanudación no repite el español ni carga Qwen. Conservar primero el estado
terminal/WAV del trabajo del propietario y comprobar ausencia de trabajos activos.

`observer.py` separa estado del worker/API de disponibilidad del observador. Solo
admite GET a health/capabilities/history/audio con UUID validado. Ruta PVE mediante
SSH estricto ya verificado; modo direct usa PVE como fallback de lecturas. Nunca
POST, cancelación, generación ni escritura en cola/API. Una conexión fallida deja
`observer-error.json` privado y conserva el estado completado leído; no lo cambia
a failed. Los tests simulan conexión perdida tras completed y descartan duplicados.
Descarga valida PCM16 mono24kHz, número real de bytes y SHA. Polling es observación,
no repetición de inferencia. `/verified.json` evita sobrescribir una validación.

`toggle.py --enable` modifica únicamente receipt después de verificar job propietario
completado, cola vacía, sharedlock, salud, hashes, modelos, memoria y límites. No
reinicia app/agente/CT ni cambia recursos. `--disable` falla cerrado sin parar un
trabajo ajeno. No repetir automáticamente activación/inferencia tras un fallo.

Para esta ejecución: ruta PVE para la única solicitud inglesa y observación por API;
marcador exclusivo de `submit_once.py` en `/mnt/storage/d089-resume`. Español se
reutiliza desde su UUID original. Backups anteriores, workers y guardas intactos.

La causa exacta del EHOSTUNREACH histórico no se infiere de una ruta actual sana.
Se conserva error original y se registra ruta directa virtualizada y PVE puenteada
por separado. No modificar rutas, firewall, DNS ni configuración SSH del usuario.

Resultado: suite77/77, español existente revalidado y único inglés completed,
WAV5,00s/API=worker SHA. Receipt enabled=true, Qwen es/en saludable, sin trabajos
activos ni reinicios. No reejecutar toggle/submit ni otro ensayo automáticamente.
Aceptación acústica pendiente. Ver informe D089 para métricas y enlaces privados.

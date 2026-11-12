# Fase 7.4 — D069: perfil personal

La candidata deriva de la imagen D068R2 conservada. `apply.py` cambia el guard
histórico por el UUID real del propietario, comprueba perfil clonado, referencias,
archivos y transcripción no vacía. Conserva Base0.6B CPU BF16/SDPA con codecFP32,
serialización TTS y rechazo de1.7B/CustomVoice. Instrumenta etapas sin registrar
texto ni audio. No actualiza dependencias ni instala otro motor.

El piloto supervisado real `pilot.py` se ejecuta fuera del CT en PVE, con límite
180s,6.5GiB,swap+64MiB,hostdisponible1.5GiB,PSIfull2%,OOM y45s sin CPU. Antes de
invocarlo: backup restaurado, descarga única fijada verificada y candidata saludable.
Referencia/transcripción originales privados, nunca incorporar a imagen/checkout.

Rollback de imagen: restaurar Compose y lock D068R2 desde backup privado y ejecutar
`docker compose up -d --no-deps --no-build voicebox`; no restaurar toda la BD para
revertir código. Los perfiles retirados se recuperan del snapshot SQLite/archivos
verificado; existen además ocho ZIP privados con filas y muestras correspondientes.

`personal-config.py` reconcilia de forma idempotente el perfil existente, engineqwen,
idiomaes, chunk200 ycatálogo persistente. No crea perfiles ni carga modelos.

Esta es una excelente recopilación de comandos. La he organizado, actualizado con las rutas correctas y he añadido comandos de mantenimiento esenciales para asegurar que tu esquema de **Alta Disponibilidad** funcione siempre sin los errores de "X" roja.

Aquí tienes tu manual de operaciones actualizado:

---

### 📂 1. Gestión de Logs (Diagnóstico)

Usa estos comandos para ver qué está pasando "bajo el capó" de NocoDB, especialmente si ves errores 502 o de conexión.

* **Ver logs en tiempo real (seguimiento):**
```bash
ssh root@192.168.1.112 'docker logs -f infra-svc01-nocodb'

```


* **Ver las últimas 50 líneas (vistazo rápido):**
```bash
ssh root@192.168.1.112 'docker logs --tail 50 infra-svc01-nocodb'
```
---

### 🗄️ 2. Acceso a Bases de Datos (PostgreSQL)

Ahora tienes dos entornos separados: uno para el sistema y otro para tus **base de datos en general**.

* **Entrar a la DB de Sistema (Metadatos):**
```bash
ssh root@192.168.1.112 -t 'docker exec -it infra-svc01-nocodb-db psql -U nocodb -d nocodb'
```


* **Entrar a la DB de Datos (Tus tablas limpias):**
```bash
ssh root@192.168.1.112 -t 'docker exec -it infra-svc01-nocodb-db psql -U nocodb -d nucleotecnologico_data'

```



**Comandos útiles dentro de Postgres:**

* `\dt`: Listar tablas.
* `\d "Nombre_Tabla"`: Ver estructura (verificar la **Primary Key**).
* `\q`: Salir.

---

### 🧹 3. Comandos de Limpieza de Emergencia

Si la UI se llena de tablas viejas o "fantasmas" que no existen físicamente, usa este comando para limpiar la memoria de NocoDB:

* **Vaciar metadatos (Cuidado: borra configuraciones de vistas en la UI, no datos reales):**
```bash
ssh root@192.168.1.112 "docker exec -i infra-svc01-nocodb-db psql -U nocodb -d nocodb -c 'TRUNCATE TABLE nc_models_v2, nc_columns_v2, nc_views_v2, nc_sources_v2 CASCADE;'"

```bash
ssh root@192.168.1.112 "docker exec -i infra-svc01-nocodb-db psql -U nocodb -d nucleotecnologico_data  -c 'TRUNCATE TABLE nc_models_v2, nc_columns_v2, nc_views_v2, nc_sources_v2 CASCADE;'"

 A. Borrar tablas físicas de la nueva DB (Si el script falla y quieres reintentar):
```bash
ssh root@192.168.1.112 "docker exec -i infra-svc01-nocodb-db psql -U nocodb -d nucleotecnologico_data -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO nocodb;'"
---
B. Verificar Permisos de Escritura (Evitar Error 403):
```bash
ssh root@192.168.1.112 "docker exec -i infra-svc01-nocodb-db psql -U nocodb -d nucleotecnologico_data -c 'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO nocodb;'"

### 🔗 4. Actualización del Data Source (API)

Este comando vincula NocoDB con tu nueva base de datos y activa los permisos de escritura necesarios para que tus scripts funcionen.

```bash
curl -X POST -H "xc-token: $NC_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "alias": "Nucleo Tecnologico",
    "type": "pg",
    "config": {
      "client": "pg",
      "connection": {
        "host": "infra-svc01-nocodb-db",
        "port": 5432,
        "user": "nocodb",
        "password": "4822fc426efe480a3c67883bec9f7eb03c07201dd268daf3",
        "database": "nucleotecnologico_data",
        "ssl": false
      },
      "meta": {
        "allowSchemaChange": true,
        "allowDataWrite": true
      }
    },
    "inflection_column": "none",
    "inflection_table": "none"
  }' \
  "https://infra-svc01.mailerblend.com/api/v2/meta/bases/pata00z3me9f1bz/sources"

```
Comprobar el esquema de Alta Disponibilidad (Primary Keys): Ejecuta esto para ver qué tablas NO tienen Primary Key (y por lo tanto darán error de "X" roja):
```bash
ssh root@192.168.1.112 "docker exec -i infra-svc01-nocodb-db psql -U nocodb -d nucleotecnologico_data -c \"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name NOT IN (SELECT table_name FROM information_schema.table_constraints WHERE constraint_type = 'PRIMARY KEY');\""
---

### 🛡️ 5. Regla de Oro para tus 15 Títulos (Alta Disponibilidad)

Para evitar que aparezcan los errores de `getColumns` o las marcas rojas en la interfaz, cada vez que crees una tabla manualmente por SQL, usa siempre este formato:

```sql
CREATE TABLE "Nombre_De_Tu_Tabla" (
    "id" SERIAL PRIMARY KEY,  -- <-- EL CAMPO MÁS IMPORTANTE
    "titulo" TEXT,
    "creado_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

```

---

### 🔄 6. Reinicio del Sistema

Si haces cambios en el `docker-compose.yml` o si el sistema se siente "pesado":

```bash
ssh root@192.168.1.112 "cd /opt/infra-svc01 && docker compose restart nocodb"

```

Desde tu terminal (fuera de Postgres):

Incluso después de borrar la tabla en SQL, NocoDB podría seguir mostrándola en la barra lateral con un error de getColumns porque aún la tiene en su "memoria". Para forzar a la interfaz a que se sincronice y quede limpia, usa el comando de limpieza de metadatos que anotamos en tu lista:

ssh root@192.168.1.112 "docker exec -i infra-svc01-nocodb-db psql -U nocodb -d nocodb -c 'TRUNCATE TABLE nc_models_v2, nc_columns_v2, nc_views_v2, nc_sources_v2 CASCADE;'"

desde dentro 
DROP TABLE "Lead_Submissions";

2. Reinicio de Sincronización

Después de la limpieza, reinicia el servicio para que la interfaz web se actualice totalmente limpia:
Bash

ssh root@192.168.1.112 "cd /opt/infra-svc01 && docker compose restart nocodb"

Limpieza de Metadatos (Obligatorio)

Debes ejecutar este comando para que NocoDB "olvide" la tabla Contacts y deje de intentar hacer el SELECT que genera el error:
Bash

ssh root@192.168.1.112 "docker exec -i infra-svc01-nocodb-db psql -U nocodb -d nocodb -c 'TRUNCATE TABLE nc_models_v2, nc_columns_v2, nc_views_v2, nc_sources_v2 CASCADE;'"

    Por qué funciona: Este comando limpia el catálogo interno de NocoDB sin tocar tus bases de datos de Postgres.

2. Reinicio de Sincronización

Después de la limpieza, reinicia el servicio para que la interfaz web se actualice totalmente limpia:
Bash

ssh root@192.168.1.112 "cd /opt/infra-svc01 && docker compose restart nocodb"

🛡️ Esquema para tus 15 Títulos (Evitar errores futuros)

Para que no vuelvas a ver el error de relation "Contacts" does not exist o problemas con getColumns, asegúrate de que al crear tus 15 tablas:

    Crea la tabla en SQL (dentro de nucleotecnologico_data).

    Usa Primary Key: Toda tabla DEBE tener una columna id SERIAL PRIMARY KEY.

    Sync en NocoDB: Una vez creada en SQL, ve a la UI de NocoDB y dale a "Meta Sync" para que la detecte correctamente.


    ```bash
ssh root@192.168.1.112 'docker exec -it infra-svc01-db psql -U nocodb -c "\l"'

nucleotecnologico_data=#


CREATE TABLE IF NOT EXISTS nc_audit_v2 (
    id VARCHAR(20) PRIMARY KEY,
    base_id VARCHAR(20),
    project_id VARCHAR(128),
    source_id VARCHAR(20),
    fk_model_id VARCHAR(20),
    row_id VARCHAR(255),
    op_type VARCHAR(255),
    op_sub_type VARCHAR(255),
    status VARCHAR(255),
    description TEXT,
    details TEXT,
    ip VARCHAR(255),
    "user" VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

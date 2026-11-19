# Lecciones Aprendidas — infra-composable-crm (CT618)

> **VMID:** 618 | **Hostname:** infra-composable-crm | **IP:** 192.168.1.118
> **Fecha de creación:** 2026-02-28
> **Estado:** Operativo

---

## 1. Arquitectura del Stack

CT618 aloja el CRM composable autoalojado con la siguiente composición:

| Servicio | Contenedor | Imagen | Puerto | Rol |
|----------|-----------|--------|--------|-----|
| Budibase App | `budibase-app` | `budibase/budibase:latest` | `192.168.1.118:8080` | UI Builder / Runtime |
| Budibase Worker | `budibase-worker` | `budibase/budibase:latest` | interno | Workers internos |
| CouchDB | `budibase-couchdb` | `couchdb:3` | interno | Metadata Budibase (apps, screens, users) |
| Redis | `budibase-redis` | `redis:7-alpine` | interno | Sesiones y caché |
| PostgreSQL | `supabase-db` | `postgres:16-alpine` | `192.168.1.118:5432` | Source of truth (datos CRM) |

**Red Docker:** `nucleo_network` (externa, compartida con otros servicios)

### Principio de arquitectura

- **PostgreSQL (Supabase)** = source of truth de datos de negocio
- **Budibase** = capa de UI / workflows (no posee datos)
- **CouchDB** = metadata interna de Budibase (NO datos de negocio)
- **Redis** = sesiones y caché
- Sistemas externos (n8n, Lambda, lead-ingest) escriben directamente en Postgres vía API

---

## 2. Gestión de Usuarios Budibase

### 2.1. Dónde se almacenan los usuarios

Los usuarios de Budibase se almacenan en **CouchDB**, no en PostgreSQL.
El documento de usuario vive en la base de datos `global-db` con ID tipo `us_<hash>`.

```
DB: global-db
DOC: us_217c63cc4b53497ebad42602e3bd2e20
CAMPOS: email, password (bcrypt hash), roles, builder, admin, tenantId, status
```

### 2.2. Reset de contraseña — método directo en CouchDB

**Problema:** Las rutas de API de Budibase (`/api/public/v1/users/:userId`) requieren autenticación (middleware `builderOrAdmin`). No se puede resetear la contraseña vía API sin estar logueado.

**Solución encontrada:** Actualizar directamente el documento de usuario en CouchDB con un nuevo hash bcrypt.

#### Procedimiento

1. **Generar hash bcrypt dentro del contenedor `budibase-app`:**
   ```bash
   ssh -o BatchMode=yes infra-composable-crm \
     "docker exec budibase-app node -e 'const bcrypt=require(\"bcrypt\");bcrypt.hash(\"NUEVA_CONTRASEÑA\",10).then(h=>console.log(h))'"
   ```
   Esto produce un hash como: `$2b$10$bGBoYSKUSM3vEZLczMqZ3.lW6cMBHVyhtAw3iXG8w8TjWHuSPwUyS`

2. **Crear archivo JSON con el hash correcto** (en el host local):
   ```bash
   cat > /tmp/budibase_user.json <<'EOF'
   {"_id":"us_217c63cc4b53497ebad42602e3bd2e20","_rev":"<rev_actual>","email":"team@mailerblend.com","password":"$2b$10$bGBoYSKUSM3vEZLczMqZ3.lW6cMBHVyhtAw3iXG8w8TjWHuSPwUyS","roles":{},"builder":{"global":true},"admin":{"global":true},"tenantId":"default","status":"active"}
   EOF
   ```
   **⚠️ IMPORTANTE:** Usar heredoc con delimitador entre comillas simples (`'EOF'`) para evitar que bash interprete los `$` del hash bcrypt.

3. **Transferir al contenedor CouchDB:**
   ```bash
   scp /tmp/budibase_user.json infra-composable-crm:/tmp/budibase_user.json
   ssh -o BatchMode=yes infra-composable-crm \
     'docker cp /tmp/budibase_user.json budibase-couchdb:/tmp/budibase_user.json'
   ```

4. **Actualizar CouchDB:**
   ```bash
   ssh -o BatchMode=yes infra-composable-crm \
     'docker exec budibase-couchdb curl -s -X PUT -u admin:<COUCHDB_PASSWORD> -H "Content-Type: application/json" http://localhost:5984/global-db/us_217c63cc4b53497ebad42602e3bd2e20 -d @/tmp/budibase_user.json'
   ```

5. **Verificar:**
   ```bash
   ssh -o BatchMode=yes infra-composable-crm \
     'docker exec budibase-couchdb curl -s -u admin:<COUCHDB_PASSWORD> http://localhost:5984/global-db/us_217c63cc4b53497ebad42602e3bd2e20'
   ```

### 2.3. Lección crítica: Expansión de variables bash en hashes bcrypt

**Problema encontrado:** Cuando se pasa el hash bcrypt directamente en el comando `curl`, los `$` del prefijo `$2b$10$` son interpretados como variables por bash, truncando el hash a `b0` o `b0.<resto>`.

**Síntomas:** El campo `password` en CouchDB queda como `b0` en lugar del hash completo.

**Soluciones:**
- ✅ **Mejor:** Usar archivo JSON externo (`-d @archivo.json`)
- ✅ **Alternativa:** Heredoc con delimitador entre comillas simples (`<<'EOF'`)
- ❌ **Evitar:** Pasar el hash directamente en `-d '{...}'` sin escapar los `$`

### 2.4. Credenciales de CouchDB

El despliegue recibe las credenciales desde archivos privados fuera de Git.
Consultar el [plan de rotación](../../docs/roadmap/planes/CRM-COUCHDB-CREDENTIAL-ROTATION-PLAN.md)
para identificar el consumidor efectivo y validar el cambio. Un valor
documentado anteriormente se considera expuesto y requiere rotación.

---

## 3. Troubleshooting Común

### 3.1. Error: `Unable to search by SQL - CouchDB error: Not found: /_design/sqlite`

**Causa:** La app fue creada cuando Budibase pensaba que el datasource era SQLite.

**Solución:** Eliminar la app, crear una nueva, conectar Postgres **antes** de añadir componentes.

### 3.2. Error: `POST /_session: login details rejected`

**Causa:** CouchDB fue inicializado con credenciales distintas a las del `.env`.

**Solución:** Reset SOLO Budibase (ver sección 3.4).

### 3.3. Budibase `unhealthy` pero la UI responde

**Causa:** El healthcheck de Docker va retrasado respecto al estado real.

**Verificación:**
```bash
curl -I http://127.0.0.1:8080/builder
```
Si responde `200` o `301`, **funciona**.

### 3.4. Reset completo de Budibase (estado fresh install)

> ⚠️ **No borra Postgres / datos CRM**

```bash
ssh root@192.168.1.118 \
  'cd /opt/infra-composable-crm/budibase && docker compose down && \
   docker volume rm -f budibase_couchdb_data budibase_redis_data || true && \
   docker compose up -d'
```

Esto devuelve la UI al estado: Create admin user → Create workspace.

### 3.5. Redeploy quirúrgico (sin afectar otros servicios)

**Solo Budibase:**
```bash
ssh root@192.168.1.118 \
  'cd /opt/infra-composable-crm/budibase && docker compose up -d --force-recreate'
```

**Solo Postgres:**
```bash
ssh root@192.168.1.118 \
  'cd /opt/infra-composable-crm/supabase && docker compose up -d supabase-db'
```

### 3.6. Docker bind IP ≠ IP del cliente

El `docker-compose.yml` de Budibase usa `192.168.1.118:8080:80` (bind IP específico).
Esto significa que el puerto 8080 solo es accesible desde interfaces con esa IP,
no desde `0.0.0.0:8080`.

---

## 4. Convenciones y Patrones

### 4.1. Acceso sin entrar a contenedores

**Regla no escrita:** Docker bind IP ≠ IP del cliente.
Todo el acceso y debugging se hace a nivel de host, nunca dentro de contenedores.

```bash
# Estado de todos los servicios
ssh root@192.168.1.118 'docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'

# Logs
ssh root@192.168.1.118 'docker logs --tail=200 budibase-couchdb'
```

### 4.2. Source of truth = PostgreSQL

- Budibase **NO** crea tablas automáticamente
- PostgreSQL es el dueño del modelo de datos
- Budibase solo **consume** las tablas vía PostgreSQL datasource
- Sistemas externos (n8n, Lambda, lead-ingest) escriben directamente en Postgres

### 4.3. Ingestión externa

Patrón recomendado:
```
[Web / Ads / Forms] → [API Gateway / n8n / Lambda] → [PostgreSQL (Supabase)] → [Budibase UI]
```

Headers recomendados:
- `X-Ingest-Secret` — autenticación de ingestión
- `Idempotency-Key` — idempotencia para retries de n8n/Lambda

### 4.4. Modelo de datos

- Tablas: `contactos`, `oportunidades`, `historial`, `pendientes`, `presupuestos`, `facturas`, `conversiones_offline`
- Relación dual: CRM tradicional (web) + LinkedIn Sourcing (prospección activa)
- Deduplicación por email OR linkedin_url OR teléfono
- Pack-first approach: `pack_asignado` en contacto, `pack_candidate` en LinkedIn lead

---

## 5. Estructura de Directorios

```
services/infra-composable-crm/
├── compose/
│   ├── budibase/
│   │   ├── docker-compose.yml      # Stack Budibase (app, worker, couchdb, redis)
│   │   └── .env                    # Credenciales CouchDB, Redis
│   └── supabase/
│       ├── docker-compose.yml      # PostgreSQL con optimizaciones
│       └── .env                    # Credenciales Postgres, Supabase keys
├── database-schemas/
│   ├── crm_schema_v2_robusto.sql   # Schema principal
│   ├── crm_diagrama_v2_completo.md # Diagrama y documentación
│   ├── crm_guia_v2_completa.md     # Guía completa del CRM
│   ├── 01_patch_*.sql              # Patches incrementales
│   ├── 02_*.sql                    # Seed data
│   ├── 03_*.py                     # Scripts de alimentación
│   ├── 10_*.sql                    # LinkedIn migrations
│   ├── 11_*.sql                    # LinkedIn knowledge base
│   └── 12_*.sql                    # LinkedIn invite templates
├── scripts/
│   ├── status.sh                   # Estado de ambos stacks
│   ├── up-budibase.sh              # Deploy Budibase (con validación)
│   ├── up-supabase.sh              # Deploy Supabase
│   ├── deploy-crm-api.sh           # Deploy API externa
│   ├── db-env.sh                   # Variables DB
│   └── LinkedIn_Stealth_Sourcing_test_*.sh  # Tests de integración
├── api/                            # API externa (si aplica)
├── recovery/                       # Backups y recovery
├── notas.text                      # Notas técnicas (legado)
├── to-do                           # Tareas pendientes
└── lecciones-aprendidas.md         # Este documento

---

## 6. Credenciales y Seguridad

> Gestionar las credenciales en archivos privados de cada despliegue. Verificar la configuración efectiva antes de rotar.

| Servicio | Usuario | Dónde encontrar password |
|----------|---------|-------------------------|
| CouchDB | `admin` | `compose/budibase/.env` → `COUCHDB_PASSWORD` |
| Redis | (ninguno) | `compose/budibase/.env` → `REDIS_PASSWORD` |
| PostgreSQL | `pgadmin2026f` | `compose/supabase/.env` → `POSTGRES_PASSWORD` |

### Notas de seguridad

- El `.env` de Budibase tiene **dos líneas duplicadas** de `COUCHDB_USER` y `COUCHDB_PASSWORD` con valores diferentes. El último valor definido es el que se usa.
- Las Supabase keys (`JWT_SECRET`, `ANON_KEY`, `SERVICE_ROLE_KEY`) están en `CHANGE_ME` — no están configuradas.
- El acceso SSH usa `infra-composable-crm` como alias de host (configurado en `~/.ssh/config`).

---

## 7. Estado Actual del Sistema

- **Infra:** Estable
- **Budibase UI:** Funcional en `http://192.168.1.118:8080` (Builder: `/builder`)
- **PostgreSQL:** Conectado, source of truth
- **Comunicación interna:** `nucleo_network`
- **Servicios:** 5 contenedores (budibase-app, budibase-worker, budibase-couchdb, budibase-redis, supabase-db)

### Próximas fases

1. **Fase 1 (CRM Base):** Schema + Budibase screens + RLS básico ✅
2. **Fase 2 (Analytics):** Dashboard + tracking conversiones + reportes
3. **Fase 3 (LinkedIn Sourcing):** n8n + Playwright + Telegram bot + scoring + IA

---

## 8. Comandos de Referencia Rápida

```bash
# Estado de servicios
ssh root@192.168.1.118 'docker ps --format "table {{.Names}}\t{{.Status}}"'

# Logs CouchDB
ssh root@192.168.1.118 'docker logs --tail=100 budibase-couchdb'

# Logs PostgreSQL
ssh root@192.168.1.118 'docker logs --tail=100 supabase-db'

# Healthcheck Budibase UI
curl -I http://192.168.1.118:8080/builder

# Acceder a CouchDB (solo lectura)
ssh root@192.168.1.118 \
  'docker exec budibase-couchdb curl -s -u admin:<pass> http://localhost:5984/global-db/_all_docs'

# Acceder a PostgreSQL
ssh root@192.168.1.118 \
  'docker exec supabase-db psql -U pgadmin2026f -d postgres -c "\\dt"'

# Redeploy Budibase
ssh root@192.168.1.118 'cd /opt/infra-composable-crm/budibase && docker compose up -d'

# Redeploy Postgres
ssh root@192.168.1.118 'cd /opt/infra-composable-crm/supabase && docker compose up -d'

# Reset Budibase (peligroso)
ssh root@192.168.1.118 \
  'cd /opt/infra-composable-crm/budibase && docker compose down && \
   docker volume rm -f budibase_couchdb_data budibase_redis_data || true && \
   docker compose up -d'
```

---

## 9. Decisiones Técnicas

| Decisión | Alternativa rechazada | Razón |
|----------|----------------------|-------|
| Budibase + CouchDB + Postgres | Budibase con SQLite interno | SQLite no soporta producción, CouchDB es requerido por Budibase |
| Postgres como source of truth | Budibase como dueño de datos | Composable: se puede cambiar UI sin tocar datos |
| Bind IP `192.168.1.118:8080:80` | `0.0.0.0:8080:80` | Control de acceso por interfaz |
| Docker bind IP para debugging | Entrar a contenedores | Regla IaC-only: diagnosticar desde host |
| Hash bcrypt en CouchDB | API de reset de contraseña | API requiere auth, bucle vicioso |

---

## 10. Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-02-28 | Creación del documento | Cline + usuario |
| 2026-02-28 | Sección 2: Reset de contraseña en CouchDB | Cline + usuario |
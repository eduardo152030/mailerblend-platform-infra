# infra-svc01 (NocoDB) — Registro de configuración

Ubicación (desde tu repo):
- Estás trabajando desde: `~/work/mailerblend-platform-infra/terraform/proxmox`
- Servicio: `services/infra-svc01/`
- Compose: `services/infra-svc01/compose/docker-compose.yml`
- Env (plantilla en repo): `services/infra-svc01/compose/.env`
- Deploy remoto (CT 192.168.1.112): `/opt/infra-svc01/`

## 1) Acceso (LAN y Dominio)

LAN:
- `http://192.168.1.112:18080`

Dominio (edge-router reverse proxy):
- `https://infra-svc01.mailerblend.com`

> Nota: si haces pruebas con `curl -I` (HEAD), algunas rutas del UI pueden devolver 404 aunque en navegador funcione (el UI carga principalmente assets/SPA). La verificación fiable es abrir en navegador y confirmar que carga el login y la interfaz.

## 2) Login inicial / usuario y contraseña

En NocoDB OSS, la primera vez que abres la UI te pide crear el **Admin (email + password)**.
- Ese password **no está en `.env`** y no se “lee” desde el contenedor.
- Si ya lo creaste: usa ese mismo email/password.
- Si lo olvidaste: usa “Forgot password” desde la UI (si tienes SMTP configurado) o re-crea la metadata DB (esto borra la configuración de NocoDB) — ver sección “Reset”.

## 3) Variables importantes (.env)

Ejemplo funcional (meta DB en Postgres):
```env
# Postgres
POSTGRES_DB=nocodb
POSTGRES_USER=nocodb
POSTGRES_PASSWORD=<tu_password_largo>

# NocoDB metadata DB (formato que te funcionó)
NC_DB=pg://db:5432?u=nocodb&p=<tu_password_largo>&d=nocodb

# JWT
NC_AUTH_JWT_SECRET=<random_64_hex>
```

### SMTP (para invitations/forgot password)

Añadir en `services/infra-svc01/compose/.env` (en repo) **y desplegar**:
```env
NC_SMTP_HOST=authsmtp.securemail.pro
NC_SMTP_PORT=465
NC_SMTP_SECURE=true
NC_SMTP_USERNAME=team@nucleotecnologico.es
NC_SMTP_PASSWORD=64qIP&Cd^2DhJDJLgY^%
NC_SMTP_FROM=team@nucleotecnologico.es
```

**OJO con Bash:** passwords con `&` rompen el comando si no usas comillas.
Ejemplos correctos:
```bash
export NC_SMTP_PASSWORD='64qIP&Cd^2DhJDJLgY^%'
# o
NC_SMTP_PASSWORD='64qIP&Cd^2DhJDJLgY^%' ./scripts/deploy-service.sh infra-svc01 192.168.1.112
```

## 4) Deploy (sin tocar nada dentro del contenedor)

Desde: `~/work/mailerblend-platform-infra/terraform/proxmox`

1) Desplegar el servicio al CT:
```bash
./scripts/deploy-service.sh infra-svc01 192.168.1.112
```

2) Health rápido desde tu máquina:
```bash
curl -sS -I http://192.168.1.112:18080/api/v1/version | head
curl -sS -I http://192.168.1.112:18080/ | head
```

3) Ver estado de contenedores (en el CT, sin entrar al contenedor):
```bash
ssh root@192.168.1.112 'docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}"'
ssh root@192.168.1.112 'docker logs --tail=120 infra-svc01-nocodb'
```

## 5) Reset (si vuelves a tener error de password con Postgres)

Síntoma típico:
- `password authentication failed for user "nocodb"`
- o cambios de password sin recrear volumen.

**Reset completo de volúmenes** (borra metadata/configuración de NocoDB):
```bash
ssh root@192.168.1.112 'cd /opt/infra-svc01 && docker compose down -v && docker compose up -d'
```

Luego vuelve a abrir la UI y crea de nuevo el admin.

## 6) Edge-router (dominio + HTTPS)

- Dominio: `infra-svc01.mailerblend.com` -> A record a tu IP pública.
- Nginx reverse proxy en edge-router hacia: `http://192.168.1.112:18080`

Checklist:
- Solo **un** site enabled por `server_name infra-svc01.mailerblend.com` (evita “conflicting server name”).
- Asegurar headers típicos:
  - `proxy_set_header Host $host;`
  - `proxy_set_header X-Forwarded-Proto $scheme;`
  - `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;`

Si `certbot --nginx` dice que falta plugin:
```bash
sudo apt-get update
sudo apt-get install -y python3-certbot-nginx
```

## 7) Verificación final

- UI abre en navegador:
  - `https://infra-svc01.mailerblend.com`
- API responde:
```bash
curl -sS http://192.168.1.112:18080/api/v1/version
```
- SMTP funcionando (prueba invitación desde UI): ✅



te pongo aquí el orden de los comando que ejecutare: 

1)  cp -r ~/work/mailerblend-platform-infra/terraform/proxmox/services/infra-svc01/compose ~/work/mailerblend-platform-infra/terraform/proxmox/services/infra-svc01/compose_backup  
2)  ssh root@192.168.1.112 'docker exec infra-svc01-nocodb-db pg_dump -U nocodb nocodb' > backup_antes_de_optimizar.sql 
    ssh root@192.168.1.112 'docker exec infra-svc01-nocodb-db pg_dump -U nocodb nocodb' > backup_$(date +%F).sql

actulizo el docker-compose file
 aplico los cambios con 

./scripts/deploy-service.sh infra-svc01 192.168.1.112

# Ver que el contenedor subió bien
ssh root@192.168.1.112 'docker ps -a'

Paso 1: Limpieza de Metadatos Rotos

Vamos a usar la potencia de la terminal para limpiar las tablas que están dando error. Entra en tu base de datos y ejecuta estos comandos para "resetear" el listado de tablas de NocoDB:
ssh root@192.168.1.112 "docker exec -i infra-svc01-nocodb-db psql -U nocodb -d nocodb -c 'TRUNCATE TABLE nc_models_v2 CASCADE;'"
Opción A (Recomendada en IaC): Destruye el container con Terraform y vuelve a crearlo. Esto eliminará cualquier residuo.
Bash

terraform destroy -target='proxmox_virtual_environment_container.svc["infra-svc01"]'
terraform apply -target='proxmox_virtual_environment_container.svc["infra-svc01"]'

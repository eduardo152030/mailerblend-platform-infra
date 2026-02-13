ssh root@192.168.1.112 'docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}"'
1) Ver logs de NocoDB (la causa exacta)
ssh root@192.168.1.112 'docker logs --tail=200 infra-svc01-nocodb'


jainer@Jainer:~/work/mailerblend-platform-infra/terraform/proxmox$ ssh root@192.168.1.112 'echo "=== /opt/infra-svc01/.env ==="; sed -n "1,120p" /opt/infra-svc01/.env'
=== /opt/infra-svc01/.env ===
# Timezone
TZ=Europe/Madrid

# Postgres
POSTGRES_DB=nocodb
POSTGRES_USER=nocodb
POSTGRES_PASSWORD=OhxfvngWIJuOS6kwpOu0BkjX7q+5T3bO

# NocoDB uses this as metadata database
NC_DB=pg://db:5432?u=nocodb&p=OhxfvngWIJuOS6kwpOu0BkjX7q+5T3bO&d=nocodb
NC_AUTH_JWT_SECRET=a254a63abab09d99b6ce063825ff382434af519da207e1adb6650ca51729bef0
jainer@Jainer:~/work/mailerblend-platform-infra/terraform/proxmox$ ssh root@192.168.1.112 'docker inspect -f "{{.Name}}  Env={{range .Config.Env}}{{println .}}{{end}}" infra-svc01-nocodb-db | egrep "POSTGRES_(USER|PASSWORD|DB)="'
POSTGRES_DB=nocodb
POSTGRES_USER=nocodb
POSTGRES_PASSWORD=OhxfvngWIJuOS6kwpOu0BkjX7q+5T3bO
jainer@Jainer:~/work/mailerblend-platform-infra/terraform/proxmox$ 


3. Solución mediante Comandos (Automatizada)

Si prefieres usar la terminal, ejecuta esto exactamente en este orden:
Bash

# 1. Definir las variables en tu sesión actual de shell
export DB_USER="nocodb"
export DB_NAME="nocodb"
export DB_PASS="4822fc426efe480a3c67883bec9f7eb03c07201dd268daf3"

# 2. Sobreescribir las líneas en el .env local
sed -i "s/^POSTGRES_USER=.*/POSTGRES_USER=$DB_USER/" services/infra-svc01/compose/.env
sed -i "s/^POSTGRES_DB=.*/POSTGRES_DB=$DB_NAME/" services/infra-svc01/compose/.env
sed -i "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$DB_PASS/" services/infra-svc01/compose/.env

# 3. Corregir NC_DB (usando '#' como delimitador de sed para evitar conflictos con la URL)
sed -i "s|^NC_DB=.*|NC_DB=pg://db:5432?u=${DB_USER}\&p=${DB_PASS}\&d=${DB_NAME}|" services/infra-svc01/compose/.env

4. Re-despliegue Limpio

Como cambiaste los passwords de una base de datos que ya tiene volúmenes creados, debes borrar los volúmenes antiguos para que Postgres tome la nueva configuración (ya que el password solo se setea en la creación del volumen).

Ejecuta esto desde tu máquina local:
Bash

# 1. Sincronizar el .env corregido
./scripts/deploy-service.sh infra-svc01 192.168.1.112

# 2. Hard Reset en el servidor (Borra datos viejos)
ssh root@192.168.1.112 'cd /opt/infra-svc01 && docker compose down -v && docker compos

Comprobaciones rápidas (copy/paste)
1) Confirmar que no hay crash-loop (que lleve “Up” aumentando)
ssh root@192.168.1.112 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | egrep "infra-svc01-nocodb($|\\s)|infra-svc01-nocodb-db"'

2) Confirmar que el puerto está escuchando desde el CT
ssh root@192.168.1.112 'ss -lntp | egrep ":18080|:8080" || true'

3) Confirmar que Prometheus lo podrá monitorear (si ya tienes job/targets)
curl -sS "http://192.168.1.110:9090/api/v1/targets" \
| jq -r '.data.activeTargets[] | "\(.labels.job)\t\(.labels.instance)\t\(.health)\t\(.lastError)"' \
| egrep "infra-svc01|192.168.1.112" || true

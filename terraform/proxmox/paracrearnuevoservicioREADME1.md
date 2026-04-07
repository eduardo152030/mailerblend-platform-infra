# Crear un nuevo servicio (Runbook incremental – COPY/PASTE)

Este documento es **operativo**: todos los comandos están pensados para **copiar y pegar**.
Asume que **SIEMPRE** empiezas desde:

```bash
cd ~/work/mailerblend-platform-infra/terraform/proxmox
```

---

## REGLAS DE ORO (OBLIGATORIO)

- ❌ Nunca entrar manualmente a un container
- ❌ Nunca rehacer toda la infraestructura
- ✅ Todo se ejecuta desde este repo
- ✅ Todo es incremental

---

## VARIABLES DEL NUEVO SERVICIO (AJUSTA SOLO ESTO)

Antes de empezar, decide estos valores:

```bash
SERVICE_NAME="infra-hola"
SERVICE_VMID="622"
SERVICE_IP="192.168.1.122/24"
```

---

## 1️⃣ Crear inventario del nuevo servicio

```bash
cat > inventory/services/${SERVICE_NAME}.yml <<EOF
service:
  name: ${SERVICE_NAME}
  vmid: ${SERVICE_VMID}
  ip: ${SERVICE_IP}

resources:
  cpu: 1
  memory: 512
  disk_gb: 8

tags:
  - internal
EOF
```

Verificar:

```bash
sed -n '1,120p' inventory/services/${SERVICE_NAME}.yml
```

---

## 2️⃣ Crear estructura del servicio

> La carpeta `services/` **ya existe**

```bash
mkdir -p services/${SERVICE_NAME}/compose/html
```

---

## 3️⃣ Crear docker-compose del servicio (ejemplo básico)

```bash
cat > services/${SERVICE_NAME}/compose/docker-compose.yml <<'EOF'
services:
  app:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "127.0.0.1:8080:80"
    volumes:
      - ./html:/usr/share/nginx/html:ro
EOF
```

Contenido de prueba:

```bash
cat > services/${SERVICE_NAME}/compose/html/index.html <<'EOF'
<h1>Servicio activo</h1>
EOF
```

---

## 4️⃣ Crear SOLO el container (Terraform incremental)

```bash
terraform plan -parallelism=1 -target="proxmox_virtual_environment_container.svc[\"${SERVICE_NAME}\"]"
```

```bash
terraform apply -parallelism=1 -target="proxmox_virtual_environment_container.svc[\"${SERVICE_NAME}\"]"
```

---

## 5️⃣ Extraer IP del inventario (automático)

```bash
SERVICE_IP_ONLY="$(awk -F': ' '/^\s*ip:/{print $2}' inventory/services/${SERVICE_NAME}.yml | cut -d/ -f1)"
echo "$SERVICE_IP_ONLY"
```

---

## 6️⃣ Desplegar el servicio (SIN entrar al container)

```bash
./scripts/deploy-service.sh ${SERVICE_NAME} "$SERVICE_IP_ONLY"
```

---

## 7️⃣ Desplegar componentes comunes (monitoring)

### Node Exporter (todos los CTs)

```bash
./scripts/deploy-common.sh node-exporter "$SERVICE_IP_ONLY"
```


### cAdvisor (solo este servicio)

```bash
./scripts/deploy-common.sh cadvisor "$SERVICE_IP_ONLY"
```

---

## 8️⃣ Reconciliar Prometheus

```bash
./scripts/gen-prom-targets.py
./scripts/reconcile-prometheus.sh
```

---

## 9️⃣ Verificación final (OBLIGATORIO)  este los devulve todos claritos

```bash
curl -sS http://192.168.1.110:9090/api/v1/targets \
| jq -r '.data.activeTargets[] | "\(.labels.job)\t\(.labels.instance)\t\(.health)"' \
| sort
```

Debe verse:
- cadvisor → **up**
- node_exporter → **up**
- prometheus → **up**

---

## 10️⃣ Qué NO hacer

❌ `terraform apply` sin `-target`  
❌ Entrar por SSH a un container  
❌ Reinstalar Docker a mano  
❌ Exponer puertos directamente  

---

## CHECKLIST FINAL

- [ ] Inventario creado
- [ ] Container creado con Terraform
- [ ] Servicio desplegado
- [ ] Node exporter activo
- [ ] cAdvisor activo
- [ ] Prometheus en verde

---

## ESTADO FINAL

Si todos los checks están en **UP**, el servicio está correctamente integrado y listo para ser expuesto por el Edge Router cuando corresponda.

 regla es:

NO “entrar” interactivo al host infra-<<Service>>

Solo se permiten comandos remotos no-interactivos tipo:
ssh root@IP "comando" para hacer comprobaciones
queremos que esto sea  100% replicable, no basta con “ejecutar comandos sueltos” por SSH. Hay que dejarlo como artefacto IaC en el repo: scripts + carpeta
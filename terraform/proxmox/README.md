# Mailerblend Platform Infra (Proxmox)

Infraestructura **declarativa, reproducible y extensible** para Mailerblend, basada en **Proxmox + Terraform + Docker**, con observabilidad integrada (**Prometheus, Alertmanager, Grafana**) y **auto‑discovery** desde inventario.

> Estado: **Startup‑grade**. No homelab. Todo se crea, destruye y recrea sin pasos manuales.

---

## 🎯 Objetivos

- Infra **100% declarativa** (Terraform + inventario YAML)
- **1 LXC por servicio** (aislamiento real)
- Deploy **desde fuera** (sin entrar manualmente en los CT)
- Observabilidad **automática** para CTs actuales y futuros
- Preparado para crecer: edge‑router, CI/CD, cloud

---

## 🧱 Arquitectura

- **Proxmox VE** como hypervisor
- **Terraform** (`proxmox_virtual_environment`) para crear LXC
- **Inventario YAML** como *source of truth*
- **Docker Compose** por servicio
- **Common modules** reutilizables (node_exporter)
- **Prometheus** con file_sd (targets desde inventario)
- **Grafana** con provisioning (datasources + dashboards)

```
┌───────────────┐
│  Inventory    │  inventory/services/*.yml
└──────┬────────┘
       │
┌──────▼────────┐      ┌─────────────────────────┐
│   Terraform   │─────▶│  LXC per service        │
└──────┬────────┘      │  Docker Compose          │
       │               │  - app / infra           │
       │               │  - node_exporter         │
       │               └─────────────────────────┘
       │
┌──────▼────────┐
│  Prometheus   │  file_sd from inventory
│  Alertmanager │
└──────┬────────┘
       │
┌──────▼────────┐
│   Grafana     │  dashboards provisioned
└───────────────┘
```

---

## 📁 Estructura del repositorio

```
terraform/proxmox/
├── inventory/
│   ├── defaults.yml
│   └── services/
│       ├── infra-prom.yml
│       └── infra-grafana.yml
│
├── services/
│   ├── infra-prom/
│   │   ├── compose/
│   │   │   └── docker-compose.yml
│   │   └── config/
│   │       ├── prometheus.yml
│   │       ├── alertmanager/
│   │       │   └── alertmanager.yml
│   │       ├── rules/
│   │       └── targets/
│   │
│   ├── infra-grafana/
│   │   ├── compose/
│   │   │   └── docker-compose.yml
│   │   └── config/
│   │       ├── provisioning/
│   │       │   ├── datasources/
│   │       │   └── dashboards/
│   │       └── dashboards/
│   │
│   └── common/
│       └── node-exporter/
│           └── docker-compose.yml
│
├── scripts/
│   ├── deploy-service.sh
│   ├── deploy-common.sh
│   ├── deploy-node-exporter-all.sh
│   ├── gen-prom-targets.py
│   ├── inventory_list.py
│   └── reconcile-prometheus.sh
│
├── Makefile
└── README.md
```

---

## 🧩 Conceptos clave

### Inventario = Source of Truth
Cada servicio se declara **una sola vez** en `inventory/services/*.yml`:

```yaml
service:
  name: infra-grafana
  vmid: 611
  ip: 192.168.1.111/24

resources:
  cpu: 2
  memory: 2048
  disk_gb: 50

tags:
  - monitoring
  - grafana
```

Terraform, Prometheus y los scripts **leen de aquí**.

---

### Deploy desde fuera (regla de oro)
 ./scripts/deploy-service.sh  infra-grafana 192.168.1.111
❌ No se entra manualmente al CT

✅ Todo se hace con scripts:
- `his  ` → servicios (Prometheus, Grafana, apps)
- `deploy-common.sh` → módulos comunes (node_exporter)

Esto garantiza **reproducibilidad total**.

---
 ./scripts/deploy-common.sh node-exporter 192.168.1.110
## 📊 Observabilidad automática

### Node Exporter
- Se despliega en **todos los CTs**
- Expone métricas en `:9100`

### Prometheus
- Usa **file_sd_configs**
- Targets se generan desde inventario (`gen-prom-targets.py`)
- CT nuevo → aparece automáticamente tras `make deploy-all`

### Grafana
- Datasource Prometheus provisionado
- Dashboards provisionados desde repo
  - Prometheus 2.0 Overview
  - Node Exporter Full

---

## 🛠️ Comandos principales

### Desplegar / reconciliar TODO (modo automático)

```bash
make deploy-all
```

Esto ejecuta:
1. `terraform apply`
2. node_exporter en todos los CTs
3. regenerar targets
4. redeploy Prometheus

---

### Solo Prometheus (targets + reload)

```bash
make prom-reconcile
```

---

### Solo node_exporter (por si añades CTs)

```bash
make node-exporter-all
```

---

### Ver estado del inventario

```bash
make status
```

---

./scripts/deploy-common.sh cadvisor <IP>
./scripts/deploy-common.sh node-exporter <IP>

❌ Si no aparece → Grafana no está levantado
👉 solución:
./scripts/deploy-service.sh infra-grafana 192.168.1.111

## 🔁 Ciclo típico para añadir un nuevo servicio

1. Crear `inventory/services/infra-nuevo.yml`
2. `make deploy-all`
3. (Opcional) `./scripts/deploy-service.sh infra-nuevo <IP>`
4. Automáticamente:
   - Prometheus lo scrapea
   - Grafana muestra métricas

---

## 🔒 Seguridad y notas

- Credenciales sensibles **no** se versionan
- Admin Grafana es solo bootstrap (cambiar a secrets)
- Named volumes Docker para estado (evita problemas de permisos en LXC)

---

## 🚀 Roadmap

- Edge-router (TLS + subdominios)
- Alertmanager receivers (Slack / Email / Webhook)
- CI/CD (GitHub Actions)
- Backups Proxmox / offsite
- Migración futura a cloud (sin romper decisiones)

---

**Autor:** Eduardo Velázquez
**Proyecto:** Mailerblend Platform Infra

PASO 1 — Ver exactamente qué va a destruir Terraform

NUNCA destruyas a ciegas.

terraform init
terraform plan -destroy


✔️ Esto te mostrará:

Qué LXCs
Qué VMs
Qué volúmenes
Qué network configs

👉 Confirma que solo son recursos del homelab (no prod).

💥 PASO 2 — Destruir todo (oficialmente)

Cuando veas que es correcto:

terraform destroy


para iniciar la maquina 

terraform fmt
terraform plan  -parallelism=1
terraform apply -parallelism=1


-------------------

curl -sS http://192.168.1.110:9090/-/ready ; echo


curl -sS "http://192.168.1.110:9090/api/v1/targets" | head -n 80

./scripts/deploy-common.sh node-exporter 192.168.1.110


Crear solo el inventario del servicio
cat > inventory/services/infra-hola.yml <<'EOF'
service:
  name: infra-hola
  vmid: 613
  ip: 192.168.1.113/24

resources:
  cpu: 1
  memory: 512
  disk_gb: 8

tags:
  - demo
  - hola
EOF

paso 2 3️⃣ Crear carpetas del servicio (solo estas)


python3 scripts/gen-prom-targets.py
./scripts/deploy-service.sh infra-prom 192.168.1.110


jainer@Jainer:~/work/mailerblend-platform-infra/terraform/proxmox$ curl -sS "http://192.168.1.110:9090/api/v1/targets" \
| jq -r '.data.activeTargets[] | "\(.labels.job)\t\(.labels.instance)\t\(.health)\t\(.lastError)"' \
| sort


Opción 4 — Ver si Prometheus ve todo UP (la más importante)

ssss
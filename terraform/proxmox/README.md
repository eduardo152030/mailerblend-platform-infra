# Mailerblend Platform Infra (Proxmox)

Infraestructura **declarativa, reproducible y extensible** para Mailerblend, basada en **Proxmox + Terraform + Docker**, con observabilidad integrada (**Prometheus, Alertmanager, Grafana**) y catálogos Prometheus generados desde inventario YAML.

> Estado operativo y trabajo pendiente: [Roadmap central](docs/roadmap/ROADMAP.md)
> y [CURRENT-STATUS](docs/roadmap/CURRENT-STATUS.md). Las capacidades descritas
> como objetivos no acreditan que todo esté desplegado o aceptado. Antes de ejecutar
> comandos, revisar la fase y el alcance autorizado.

Estado contrastado el **2026-11-10 (Europe/Madrid)**: 17 LXC monitorizados,
17 Node/17 cAdvisor/18 Blackbox UP. F1–F6 cerradas en sus alcances; F7 IN PROGRESS.
Fleet Overview y LXC Details desplegados, navegación bidireccional y nueve dashboards
IaC. Las altas requieren publicar inventario/targets: no hay despliegue automático
de exporters por aparecer un CT en Proxmox.
[Cierre F6](docs/roadmap/PHASE6-D060-CLOSURE.md),
[evidencia actual](docs/roadmap/evidence/2026-11-10-d060-result.json).

Alta de nuevosCT: [NEW-LXC-PROVISIONING](docs/runbooks/NEW-LXC-PROVISIONING.md).
D061 prepara el flujo con mocks sin Docker y con Docker; ninguna alta real aplicada.
7.2SecurityHardening y7.3DisasterRecovery OUT OF SCOPE, no DONE.

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
│   Terraform   │─────▶│  LXC per service         │
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

❌ No se entra manualmente al CT

✅ Todo se hace con scripts:
- `deploy-service.sh` → servicios (Prometheus, Grafana, apps)
- `deploy-common.sh` → módulos comunes (node_exporter)

Esto garantiza **reproducibilidad total**.

---

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

El seguimiento oficial está en [docs/roadmap/ROADMAP.md](docs/roadmap/ROADMAP.md).
Para continuar otro día, abrir [CURRENT-STATUS](docs/roadmap/CURRENT-STATUS.md) y
[DECISIONS](docs/roadmap/DECISIONS.md). Las reglas de trabajo están en [AGENTS.md](AGENTS.md).

Fase 3 aceptada con dispensa de UAT; fase activa: **4 — Exporters & Monitoring Coverage**.
Los tres Journal 624/626/625 tienen exporters aceptados. La integración incremental
CPU P0 y R1 CT 613 están preparados, no desplegados: ver
[estado actual](docs/roadmap/CURRENT-STATUS.md) e
[integración](docs/roadmap/INCREMENTAL-INTEGRATION.md). F4 exige 17 cadenas completas.
`make deploy-all` es una operación global con Terraform, no un comando de diagnóstico
ni el procedimiento del piloto de F4.

## Referencia del stack de monitoring

- `infra-prom` (Prometheus + Alertmanager): `192.168.1.110`.
- `infra-grafana` (Grafana): `192.168.1.111`.
- `node-exporter` por CT: puerto `9100`.
- `cadvisor` por CT: puerto `8085`.

Prometheus usa file_sd generado desde `inventory/services/*.yml`. Para generar
catálogos localmente, sin desplegar:

```bash
./scripts/gen-prom-targets.py
```

## Ideas históricas pendientes de priorización

Edge-router (TLS/subdominios), otros receivers (Slack/Email/Webhook), CI/CD,
backups Proxmox/offsite y migración futura a cloud constaban en el README previo.
Su existencia no implica aprobación ni ejecución; la planificación efectiva y
las dependencias se registran en el roadmap central.

---

**Autor:** Eduardo Velázquez
**Proyecto:** Mailerblend Platform Infra

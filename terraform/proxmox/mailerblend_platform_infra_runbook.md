# Mailerblend Platform Infra – Runbook (Proxmox)

> **Objetivo**: documento operativo, claro y reproducible para volver a este proyecto dentro de meses y poder **destruir, recrear y extender** la infraestructura sin depender de memoria.

---

## 🧠 Principios clave (léelo siempre antes de tocar nada)

- **Todo se hace desde fuera de los contenedores (CTs)**
- **Nunca** se entra a un CT para ejecutar `docker compose`
- **El inventario YAML es la fuente de la verdad**
- Si algo no es reproducible → está mal
- Mentalidad **cloud / startup**, no homelab manual

---

## 📍 Dónde estoy siempre

```bash
cd ~/work/mailerblend-platform-infra/terraform/proxmox
```

Todos los comandos del runbook **asumen este path**.

---

## 📁 Estructura mental del proyecto

```
terraform/proxmox/
├── inventory/
│   ├── defaults.yml
│   └── services/
│       ├── infra-prom.yml
│       ├── infra-grafana.yml
│       └── <servicios>.yml
│
├── services/
│   ├── infra-prom/
│   ├── infra-grafana/
│   └── common/
│       ├── node-exporter/
│       └── cadvisor/
│
├── scripts/
│   ├── deploy-service.sh
│   ├── deploy-common.sh
│   ├── deploy-node-exporter-all.sh
│   ├── gen-prom-targets.py
│   ├── inventory_list.py
│   ├── prom-reconcile.sh
│   └── reconcile-prometheus.sh
└── README.md
```

---

## 🧨 1. Destruir TODA la infraestructura

⚠️ **Nunca destruyas a ciegas**

```bash
terraform init
terraform plan -destroy
```

Revisa:
- LXCs
- Volúmenes
- Redes

Si todo es correcto:

```bash
terraform destroy
```

✔️ Resultado: **Proxmox limpio**, sin restos gestionados por Terraform.

---

## 🏗️ 2. Crear TODA la infraestructura desde cero

```bash
terraform fmt
terraform plan -parallelism=1
terraform apply -parallelism=1
```

Esto crea:
- Todos los CTs
- Networking
- Discos

### Paso siguiente (obligatorio)

```bash
make deploy-all
```

Esto ejecuta, en orden:
1. `terraform apply`
2. `deploy-node-exporter-all.sh`
3. `gen-prom-targets.py`
4. `reconcile-prometheus.sh`

---

## 🔁 3. Orden correcto de ejecución de scripts

| Orden | Script | Qué hace |
|-----|-------|--------|
| 1 | `deploy-node-exporter-all.sh` | Instala node_exporter en todos los CTs |
| 2 | `deploy-common.sh cadvisor <IP>` | Instala cAdvisor (uno o muchos CTs) |
| 3 | `gen-prom-targets.py` | Genera targets Prometheus desde inventario |
| 4 | `reconcile-prometheus.sh` | Redeploy Prometheus con nuevos targets |
| 5 | `deploy-service.sh <svc> <IP>` | Deploy de un servicio concreto |

---

## ❌ 4. Destruir un servicio / CT específico

1. Localiza el fichero:

```bash
inventory/services/<servicio>.yml
```

2. Elimínalo o coméntalo
3. Ejecuta:

```bash
terraform plan
terraform apply
```

✔️ Terraform **solo destruye ese CT**.

---

## ➕ 5. Añadir un nuevo servicio (plantilla)

📍 **Ubicación**:

```bash
inventory/services/nocodb.yml
```

📄 **Plantilla base** (editar valores):

```yaml
service:
  name: nocodb
  vmid: <PENDIENTE>
  ip: <PENDIENTE>/24

resources:
  cpu: 2
  memory: 2048
  disk_gb: 20

tags:
  - app
  - nocodb
```

📌 **Pasos**:
1. Crear el YAML
2. `terraform apply`
3. `./scripts/deploy-service.sh nocodb <IP>`
4. `make deploy-all`

✔️ Automáticamente:
- Prometheus scrapea el CT
- Grafana puede mostrar métricas

---

## 📊 6. Comprobaciones obligatorias de salud

### Prometheus

```bash
curl http://<IP_PROM>:9090/-/ready
```
Debe devolver `200 OK`.


jainer@Jainer:~/work/mailerblend-platform-infra/terraform/proxmox$ curl http://192.168.1.110:9090/-/ready
Prometheus Server is Ready.
jainer@Jainer:~/work/mailerblend-platform-infra/terraform/proxmox$ 

### Targets

```bash
curl http://192.168.1.110:9090/api/v1/targets | jq '.data.activeTargets[].health'
```
Todos deben ser `"up"`.

### Grafana

Abrir en navegador:

```
http://<IP_GRAFANA>:3010
```

Comprobar:
- Datasource Prometheus OK
- Dashboards cargan

En **Explore → Prometheus**:

```promql
up
```

Debe devolver series con valor `1`.

---

## 🐳 7. Docker / cAdvisor (métricas por contenedor)

- cAdvisor se despliega como **common service**
- Prometheus lo descubre vía `cadvisor.json`
- Grafana usa dashboards Docker / cAdvisor – Slim

Si cambias flags o docker-compose de cAdvisor:

```bash
./scripts/deploy-common.sh cadvisor <IP>
make prom-reconcile
```

Nunca dentro del CT.

---

## 🚫 Errores comunes (y por qué están mal)

❌ Entrar al CT y ejecutar `docker compose`

❌ Editar archivos solo en `/opt`

❌ Crear dashboards solo desde UI sin exportarlos

---

## ✅ Regla de oro final

> Si destruyo TODO y lo recreo, **debe quedar exactamente igual**.

Si no → hay pasos manuales ocultos → hay que arreglarlo.

---

**Autor**: Eduardo Velázquez  
**Proyecto**: Mailerblend Platform Infra  
**Última revisión**: automática desde este runbook

como añadir cAdvisor  aun nuevo servicio ?

Perfecto, vamos paso a paso y sin magia, pensando en que mañana tengas 20 servicios y no quieras tocar nada a mano.

Voy a explicarlo en 3 niveles:

Qué hace que cAdvisor se “añada” a un servicio

Qué tienes que hacer tú (exactamente)

Cómo comprobar que ha funcionado

🧠 1. Idea clave (qué está pasando realmente)

👉 NO “añades cAdvisor a un servicio” en Prometheus directamente.

Lo que ocurre es esto:

Cada CT / VM ejecuta:

cadvisor (puerto 8085)

Prometheus NO sabe nada de tus CTs

Prometheus:

Lee inventory/services/*.yml

gen-prom-targets.py genera cadvisor.json

Prometheus scrapea automáticamente

👉 Conclusión
✅ Si un servicio está en inventory/services/
✅ y tiene cAdvisor desplegado
➡️ Prometheus lo recoge solo

🛠️ 2. Cómo añadir cAdvisor a un NUEVO servicio (procedimiento real)

Supongamos que vas a añadir nocodb.

🧩 Paso 1 — Añadir el servicio al inventory

📍 Archivo nuevo:

inventory/services/nocodb.yml


Contenido mínimo:

service:
  name: nocodb
  ip: 192.168.1.120/24


👉 Nada más.
👉 No tocas Prometheus.
👉 No tocas Grafana.

🧩 Paso 2 — Desplegar cAdvisor en ese CT

Desde tu máquina local:

./scripts/deploy-common.sh cadvisor 192.168.1.120


Esto:

Copia services/common/cadvisor

Arranca cAdvisor en el CT

Expone :8085

💡 Esto escala igual con 2 o 20 servicios.

🧩 Paso 3 — Regenerar targets de Prometheus
./scripts/gen-prom-targets.py


Esto actualiza:

services/infra-prom/config/targets/cadvisor.json


Incluyendo ahora:

192.168.1.120:8085  (nocodb)

🧩 Paso 4 — Reconciliar Prometheus
./scripts/reconcile-prometheus.sh


👉 No reinicia Prometheus
👉 Hace reload limpio

✅ 3. Comprobaciones OBLIGATORIAS
🔍 1️⃣ Prometheus ve el nuevo cAdvisor
curl http://192.168.1.110:9090/api/v1/targets | grep cadvisor -A6


Debes ver algo como:

"job":"cadvisor",
"instance":"192.168.1.120:8085",
"service":"nocodb",
"health":"up"

🔍 2️⃣ Métricas reales desde Prometheus
curl http://192.168.1.110:9090/api/v1/query?query=container_cpu_usage_seconds_total | head


Debe devolver datos.

🔍 3️⃣ Grafana (sin tocar nada)

En tu dashboard Docker / cAdvisor – Slim:

Job → cadvisor

Service → nocodb

Verás los contenedores automáticamente

🧠 Importante (esto es CLAVE para escalar)

✔️ Nunca editas Prometheus a mano
✔️ Nunca editas targets JSON a mano
✔️ Nunca creas dashboards por servicio

Solo:

inventory

deploy-common

gen + reconcile

🧱 Resumen ultra corto (para el runbook)
Añadir cAdvisor a un nuevo servicio:

1. Crear inventory/services/<svc>.yml
2. ./scripts/deploy-common.sh cadvisor <IP>
3. ./scripts/gen-prom-targets.py
4. ./scripts/reconcile-prometheus.sh
5. Verificar en Prometheus /targets

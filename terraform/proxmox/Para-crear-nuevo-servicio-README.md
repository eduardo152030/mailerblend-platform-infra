# Crear un nuevo servicio (Runbook incremental)

Este documento describe **el flujo correcto y mínimo** para crear y desplegar un **nuevo servicio** en la infraestructura **sin rehacer nada existente**.

> Regla de oro:
> - **Nunca** entrar manualmente al container.
> -  el puerto 8080  ya esta usado por otro contenedor 
> -  ips disponible desde las 168.168.1.118 (incluida)
> -  vmid 6** (**) los 2 ultimos numeros de la ip
> - **Todo** se ejecuta desde el repo:
>   `~/work/mailerblend-platform-infra/terraform/proxmox`

---

## 0. Punto de partida

```bash
cd ~/work/mailerblend-platform-infra/terraform/proxmox
```

Comprobar servicios actuales:

```bash
make status
```

---

## 1. Crear inventario del nuevo servicio

Crear el archivo de inventario:

```bash
inventory/services/infra-<nombre>.yml
```

Ejemplo:

```yaml
service:
  name: infra-hola
  vmid: 620
  ip: 192.168.1.130/24

resources:
  cpu: 1
  memory: 512
  disk_gb: 8

tags:
  - demo
  - internal
```

Notas:
- `vmid` debe ser único.
- La IP debe estar libre.
- El nombre **no debe revelar** la función real del servicio.

---

## 2. Crear estructura del servicio

La carpeta `services/` **ya existe**.  
Solo se crea la del nuevo servicio.

```bash
mkdir -p services/infra-hola/compose
```

Ejemplo con servicio básico (nginx):

```bash
mkdir -p services/infra-hola/compose/html
```

```bash
cat > services/infra-hola/compose/docker-compose.yml <<'EOF'
services:
  hola:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "127.0.0.1:8080:80"
    volumes:
      - ./html:/usr/share/nginx/html:ro
EOF
```

```bash
cat > services/infra-hola/compose/html/index.html <<'EOF'
<h1>Hola desde infra-hola</h1>
EOF
```

---

## 3. Crear SOLO el container (Terraform incremental)

```bash
terraform plan -parallelism=1 -target='proxmox_virtual_environment_container.svc["infra-hola"]'
terraform apply -parallelism=1 -target='proxmox_virtual_environment_container.svc["infra-hola"]'
```

Esto **no toca** el resto de la infraestructura.

---

## 4. Desplegar el servicio

Extraer IP del inventario:

```bash
IP="$(awk -F': ' '/^\s*ip:/{print $2}' inventory/services/infra-hola.yml | cut -d/ -f1)"
```

Desplegar:

```bash
./scripts/deploy-service.sh infra-hola "$IP"
```

---

## 5. Desplegar componentes comunes (si aplica)

### Node Exporter (todos)

```bash
./scripts/deploy-node-exporter-all.sh
```

### cAdvisor (por servicio o varios)

```bash
./scripts/deploy-common.sh cadvisor "$IP"
```

---

## 6. Reconciliar Prometheus

```bash
./scripts/gen-prom-targets.py
./scripts/reconcile-prometheus.sh
```

---

## 7. Verificación final

### Targets Prometheus

```bash
curl -sS http://192.168.1.110:9090/api/v1/targets | jq
```

Esperado:
- node_exporter: **up**
- cadvisor: **up**
- prometheus: **up**

---

## 8. Qué NO hacer

❌ `terraform apply` sin `-target`  
❌ Entrar al container por SSH para instalar cosas  
❌ Rehacer la infraestructura completa  
❌ Exponer puertos directamente

---

## 9. Checklist final

- [ ] Inventario creado
- [ ] Container creado con Terraform
- [ ] Servicio desplegado con `deploy-service.sh`
- [ ] Exporters activos
- [ ] Prometheus targets en verde

---

## Estado

Si todos los pasos están completos y los targets están **UP**, el servicio está **correctamente integrado**.

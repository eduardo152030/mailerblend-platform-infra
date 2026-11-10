# Purpose

Google Tag Manager Server-Side para Mailerblend: recepción y procesamiento de solicitudes de tracking. Serving atiende tráfico; Preview permite depurar GTM.

## Environment

Production — clasificación prod en inventario y Proxmox.

## Network

- CT 615 — infra-mailerblend-edge — IP 192.168.1.115
- Main domain: mailerblend.com
- Public URL: https://edge.mailerblend.com
- EdgeRouter/Nginx termina TLS; Serving es el destino habitual.
- `/gtm/` selecciona Preview si X-Gtm-Server-Preview o X-Gtm-Preview no están vacías; no usa `/preview/` como CT614.

## Applications

- sGTM Serving — mailerblend-sgtm-serving — 18091 → 8080/tcp.
- sGTM Preview — mailerblend-sgtm-preview — 18092 → 8080/tcp.
- Node Exporter 1.10.2 — 9100; cAdvisor v0.60.6 — 8085.
- Salud: GET `/healthz` local en ambos; público `/healthz` (Serving), `/gtm/healthz` con cabecera de selección (Preview).

## Dependencies

Proxmox/LXC, Docker, red interna, DNS, EdgeRouter/Nginx, TLS Let's Encrypt y configuración/bootstrap de Google Tag Manager. Serving depende de Preview.

## Monitoring

Prometheus recoge Node/cAdvisor. Blackbox HEAD `/g/collect` (200/204); Alertmanager → Telegram. Salud HTTP no certifica entrega GA4.

## Infrastructure as Code

`terraform/proxmox/services/infra-mailerblend-edge/`
Base activa: `/opt/infra-mailerblend-edge/docker-compose.yml` + `healthcheck.native.yml`. Mantener ambos; no desplegar el checker curl histórico.

## Documentation

`docs/inventory/615-LXC-INVENTORY.md`, desde `terraform/proxmox/`.
Recuperación: `docs/roadmap/CT615-SGTM-D048-RECOVERY.md`.

## Known Issues

- Recuperado el 06/11/2026: probable caducidad del bootstrap y checker curl incompatible. Node nativo aplicado; una recreación por servicio en D048.
- Prevención automática y entrega GA4 extremo a extremo pendientes.
- Disco real 10 GiB frente a 16 GiB declarados; discrepancia documentada, sin corregir.
- Issue #1: https://github.com/eduardo152030/mailerblend-platform-infra/issues/1

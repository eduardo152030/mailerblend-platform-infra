# Purpose

Server-Side Google Tag Manager para Núcleo Tecnológico.

## Environment

Production

## Network

- CT 614 — infra-nucleoedge — IP 192.168.1.114
- Main domain: nucleotecnologico.es
- Public URL: https://edge.nucleotecnologico.es
- Nginx en EdgeRouter: `/` → Serving; `/preview/` → Preview, elimina el prefijo.
- `/orbit/healthz` y `/orbit/ingest` pertenecen a CT617, no a este LXC.

## Applications

- sGTM Serving — 8091 → 8080/tcp — Procesamiento de tracking.
- sGTM Preview — 8092 → 8080/tcp — Depuración GTM.
- Node Exporter 1.10.2 — 9100; cAdvisor v0.60.6 — 8085.
- Salud nativa: GET `/healthz`; Preview público: `/preview/healthz`. Esperado HTTP200.

## Dependencies

Proxmox/LXC, Docker, red interna, DNS, EdgeRouter/Nginx, TLS Let's Encrypt y Google Tag Manager. Serving depende de Preview.

## Monitoring

Prometheus → Alertmanager / Telegram; Node Exporter y cAdvisor; Blackbox HEAD `/g/collect` (200/204). Estas sondas no certifican entrega GA4 ni toda la salud del bootstrap.

## Infrastructure as Code

- `terraform/proxmox/services/infra-nucleoedge/`
- Inventario: `terraform/proxmox/inventory/services/infra-nucleoedge.yml`.
- Compose activo: `/opt/infra-nucleoedge/docker-compose.yml` + `healthcheck.native.yml`.
- No desplegar el Compose histórico sin contrastarlo con el activo.

## Documentation

`docs/inventory/614-LXC-INVENTORY.md`, desde `terraform/proxmox/`: arquitectura, configuración, diagnóstico y recuperación.

## Known Issues

- Bootstrap recuperado el 06/11/2026 tras probable caducidad; healthcheck Node nativo aplicado. Prevención automática pendiente.
- Disco real 10 GiB, declarado 16 GiB; discrepancia documentada, sin corregir.
- Entrega GA4 extremo a extremo pendiente de validación.
- GitHub Issue #1: https://github.com/eduardo152030/mailerblend-platform-infra/issues/1

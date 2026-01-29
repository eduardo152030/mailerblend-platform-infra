Restarting Services and Containers

Mailerblend Platform – Proxmox + Docker (Runbook)

Purpose

This document explains how to restart a service or container correctly in the Mailerblend platform.

The goal is to ensure that:

Restarts are replicable

No manual, non-tracked changes are made

The procedure works today and months from now

Examples use Prometheus + Alertmanager, but the same logic applies to any service (Grafana, cAdvisor, Node Exporter, NocoDB, etc.).

Important Architecture Principles (Read First)

Docker does NOT run on the Proxmox host

Docker runs inside each LXC / VM

All services are managed from the infra repository

Services are deployed using scripts, not manual docker compose up

👉 Never run docker from your local machine or Proxmox host

Service Structure (Standard)

Each service follows this pattern:

services/       
infra-grafana
│   ├── compose
│   │   └── docker-compose.yml
│   ├── config
│   │   ├── dashboards
│   │   │   ├── Docker_cAdvisor_Slim_Mailerblend_v6_REIMPORTABLE.json
│   │   │   ├── Node_Exporter_Slim.json
│   │   │   ├── node-exporter-full.json
│   │   │   ├── node-exporter-slim.json
│   │   │   └── prometheus-2-stats.json
│   │   └── provisioning
│   │       ├── alerting
│   │       ├── dashboards
│   │       │   ├── default.yml
│   │       │   └── provider.yml
│   │       ├── datasources
│   │       │   └── datasource.yml
│   │       └── plugins
│   └── useful-commands-restart-services.md



Recommended Method (SAFE & REPLICABLE)
Restart a Service (Example: grafana)

From the infra repository root:

./scripts/deploy-service.sh infra-grafana 192.168.1.111

What this does internally

Syncs services/infra-grafana → /opt/infra-grafana

Pulls updated images if needed

Recreates containers if required

Starts:

grafana

alertmanager

✔ Idempotent
✔ Replicable
✔ Source-controlled

👉 This is the preferred way

Verify the Service Is Running
Check containers
ssh root@192.168.1.111 "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"


Expected:

grafana     Up
alertmanager   Up

Check Prometheus health
curl http://192.168.1.110:9090/-/ready


Expected:

Prometheus is Ready.

Check Alertmanager health
curl http://192.168.1.110:9093/-/ready


Expected:

OK

Alternative Method (DEBUG ONLY)

⚠️ Use only for troubleshooting, never as standard workflow.

ssh root@192.168.1.110
cd /opt/infra-prom
docker compose restart


This:

Restarts containers

Does not re-sync configuration

Can drift from Git state

Restart a Single Container (Advanced / Debug)

Example: restart only Prometheus

ssh root@192.168.1.110 "docker restart prometheus"

docker compose up -d --force-recreate alertmanager
ssh root@192.168.1.110 "cd /opt/infra-prom && docker compose up -d --force-recreate alertmanager"
⚠️ Not recommended for routine operations

Restarting Any Other Service

The same pattern applies to any service.

Example: Grafana
./scripts/deploy-service.sh infra-grafana 192.168.1.111

Example: NocoDB (future)
./scripts/deploy-service.sh infra-nocodb 192.168.1.120

What NOT To Do (Common Mistakes)

❌ Run Docker locally:

docker compose up


❌ Run Docker on Proxmox host

❌ Modify containers manually without updating:

services/<service-name>/


❌ Restart services without Git-tracked config

Summary (Golden Rule)

If you want something to be reproducible, it must go through the deploy scripts.

deploy-service.sh → correct

docker compose on host → wrong

manual fixes without Git → technical debt


check if the container is running 

ssh root@192.168.1.110 "docker ps --format 'table {{.Names}}\t{{.Status}}' | grep prometheus"

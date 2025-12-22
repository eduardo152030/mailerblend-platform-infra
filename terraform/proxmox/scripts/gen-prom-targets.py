#!/usr/bin/env python3
import glob, json, os, yaml

services = []
for path in sorted(glob.glob("inventory/services/*.yml")):
  with open(path, "r", encoding="utf-8") as f:
    doc = yaml.safe_load(f) or {}
  svc = doc.get("service", {})
  ip_cidr = svc.get("ip")
  name = svc.get("name")
  if not ip_cidr or not name:
    continue
  ip = ip_cidr.split("/")[0]
  services.append({"name": name, "ip": ip})

targets = [{
  "targets": [f"{s['ip']}:9100" for s in services],
  "labels": {"job": "node", "source": "inventory"},
}]

# Add per-target labels using multiple groups (Prometheus file_sd supports multiple groups)
groups = []
for s in services:
  groups.append({
    "targets": [f"{s['ip']}:9100"],
    "labels": {"job": "node", "source": "inventory", "service": s["name"]},
  })

out_path = "services/infra-prom/config/targets/node-exporter.json"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
  json.dump(groups, f, indent=2)

print(f"Wrote {out_path} with {len(services)} targets")

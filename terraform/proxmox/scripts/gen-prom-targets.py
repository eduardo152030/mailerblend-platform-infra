#!/usr/bin/env python3
import glob, json, os
import yaml

def load_services():
  services = []
  for path in sorted(glob.glob("inventory/services/*.yml")):
    with open(path, "r", encoding="utf-8") as f:
      doc = yaml.safe_load(f) or {}
    svc = doc.get("service", {})
    name = svc.get("name")
    ip_cidr = svc.get("ip")
    if not name or not ip_cidr:
      continue
    ip = ip_cidr.split("/")[0]
    services.append({"name": name, "ip": ip})
  return services

def write_file_sd(out_path, port, job, only_services=None):
  services = load_services()
  if only_services:
    only = set(only_services)
    services = [s for s in services if s["name"] in only]

  groups = []
  for s in services:
    groups.append({
      "targets": [f"{s['ip']}:{port}"],
      "labels": {"job": job, "source": "inventory", "service": s["name"]},
    })

  os.makedirs(os.path.dirname(out_path), exist_ok=True)
  with open(out_path, "w", encoding="utf-8") as f:
    json.dump(groups, f, indent=2)
  print(f"Wrote {out_path} with {len(services)} targets")

def main():
  write_file_sd("services/infra-prom/config/targets/node-exporter.json", 9100, "node_exporter")
  write_file_sd("services/infra-prom/config/targets/cadvisor.json", 8085, "cadvisor")
  # Grafana expone /metrics en el puerto 3010 (host port -> container 3000)
  write_file_sd("services/infra-prom/config/targets/grafana.json", 3010, "grafana", only_services=["infra-grafana"])

if __name__ == "__main__":
  main()
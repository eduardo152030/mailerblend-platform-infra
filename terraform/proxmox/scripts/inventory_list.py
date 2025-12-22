#!/usr/bin/env python3
import glob, yaml

def main():
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
    services.append((name, ip))
  for name, ip in services:
    print(f"{name} {ip}")

if __name__ == "__main__":
  main()

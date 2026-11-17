#!/usr/bin/env python3
"""Calcula el siguiente paso de la escalera de swap de un LXC.

Escalera fija (MiB, la unidad que usa PVE):
    N GiB  ->  N GiB + 717 MiB  ->  (N+1) GiB  ->  (N+1) GiB + 717 MiB  -> ...
es decir: 512, 1229, 1024, 1741, 2048, 2765, 3072, 3789, 4096, ...

El valor "medio" de cada par es 717 MiB por encima del GiB inferior
(1024 + 717 = 1741), punto medio redondeado hacia arriba (1536 -> 1741,
valor canónico observado en 631).

Tope de seguridad (fail closed): el nuevo swap NO puede superar
  - 2 x RAM del CT, ni
  - 4096 MiB.
Si el siguiente paso supera el tope, el script detiene y explica.

Uso:
    python3 scripts/next-swap-step.py --service infra-webui
    python3 scripts/next-swap-step.py --ct 631
    python3 scripts/next-swap-step.py --current 1024 --memory 4096
    python3 scripts/next-swap-step.py --current 1741 --memory 4096 --json

Solo lectura: no modifica nada. La fuente de verdad es
inventory/services/<service>.yml (resources.swap / resources.memory).
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICES_DIR = ROOT / "inventory" / "services"

# Escalera canónica (MiB). Regla N GiB -> N GiB+717 -> (N+1) GiB, hasta el tope.
LADDER = [512, 1229, 1024, 1741, 2048, 2765, 3072, 3789, 4096]
MAX_SWAP_MIB = 4096


def load_service(service: str) -> dict:
    path = SERVICES_DIR / f"{service}.yml"
    if not path.exists():
        raise SystemExit(f"ERROR: no existe {path}")
    import yaml
    data = yaml.safe_load(path.read_text())
    res = data.get("resources", {})
    return {
        "service": service,
        "vmid": data.get("service", {}).get("vmid"),
        "memory": res.get("memory"),
        "swap": res.get("swap"),
    }


def find_service_by_ct(ct: int) -> dict:
    import yaml
    for path in sorted(SERVICES_DIR.glob("*.yml")):
        data = yaml.safe_load(path.read_text())
        if data.get("service", {}).get("vmid") == ct:
            res = data.get("resources", {})
            return {
                "service": path.stem,
                "vmid": ct,
                "memory": res.get("memory"),
                "swap": res.get("swap"),
            }
    raise SystemExit(f"ERROR: ningún servicio declara vmid {ct}")


def next_step(current: int, memory: int) -> dict:
    """Devuelve el siguiente paso de la escalera y su validación de seguridad."""
    if current not in LADDER:
        # Valor actual fuera de la escalera: proponemos el peldaño mayor.
        candidates = [v for v in LADDER if v > current]
        if not candidates:
            return {
                "current": current, "next": None, "status": "AT_MAX",
                "reason": f"El swap actual ({current} MiB) ya está en o por encima del tope de {MAX_SWAP_MIB} MiB.",
            }
        nxt, off_ladder = candidates[0], True
    else:
        idx = LADDER.index(current)
        if idx + 1 >= len(LADDER):
            return {
                "current": current, "next": None, "status": "AT_MAX",
                "reason": f"El swap actual ({current} MiB) es el último peldaño de la escalera ({MAX_SWAP_MIB} MiB).",
            }
        nxt, off_ladder = LADDER[idx + 1], False

    # Tope de seguridad: 2 x RAM y 4096 MiB.
    cap_ram = memory * 2 if memory else None
    cap = min([c for c in (cap_ram, MAX_SWAP_MIB) if c is not None])
    if nxt > cap:
        return {
            "current": current, "next": None, "status": "BLOCKED",
            "reason": (
                f"El siguiente paso ({nxt} MiB) supera el tope de seguridad "
                f"({cap} MiB = min(2xRAM={cap_ram} MiB, {MAX_SWAP_MIB} MiB)). "
                "No se propone aumento; revisar RAM o solicitar excepción explícita."
            ),
            "cap_mib": cap, "cap_ram_mib": cap_ram,
        }
    return {
        "current": current, "next": nxt, "status": "OK",
        "off_ladder": off_ladder, "cap_mib": cap, "cap_ram_mib": cap_ram, "reason": None,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--service", help="Nombre del servicio (archivo del inventario sin extensión)")
    p.add_argument("--ct", type=int, help="vmid del CT")
    p.add_argument("--current", type=int, help="Swap actual en MiB (si no se resuelve por service/ct)")
    p.add_argument("--memory", type=int, help="RAM en MiB (si no se resuelve por service/ct)")
    p.add_argument("--json", action="store_true", help="Salida en JSON")
    a = p.parse_args()

    service = vmid = memory = current = None
    if a.service:
        d = load_service(a.service)
        service, vmid, memory, current = d["service"], d["vmid"], d["memory"], d["swap"]
    elif a.ct is not None:
        d = find_service_by_ct(a.ct)
        service, vmid, memory, current = d["service"], d["vmid"], d["memory"], d["swap"]
    else:
        current, memory = a.current, a.memory

    if current is None:
        raise SystemExit("ERROR: falta el swap actual (usa --service, --ct o --current)")
    if memory is None:
        raise SystemExit("ERROR: falta la RAM (usa --service, --ct o --memory)")

    result = next_step(current, memory)
    result.update({"service": service, "vmid": vmid, "memory_mib": memory})

    if a.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"service : {service or '-'}")
        print(f"vmid    : {vmid or '-'}")
        print(f"ram     : {memory} MiB")
        print(f"swap    : {current} MiB")
        print(f"estado  : {result['status']}")
        if result["status"] == "OK":
            print(f"siguiente: {result['next']} MiB")
            if result.get("off_ladder"):
                print("aviso   : el valor actual no estaba en la escalera; se propone el peldaño mayor")
        else:
            print(f"motivo  : {result['reason']}")
        sys.exit(0 if result["status"] == "OK" else 2)


if __name__ == "__main__":
    main()

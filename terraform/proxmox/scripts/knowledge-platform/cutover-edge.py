#!/usr/bin/env python3
"""Prepare, apply, or roll back the explicitly approved CT633/CT109 cutover."""
import argparse
import json
from pathlib import Path
import socket
import subprocess

BASE = Path("/opt/infra-knowledge")
VHOST = Path("/etc/nginx/sites-available/doc.mailerblend.com.conf")
CA = Path("/etc/nginx/knowledge-platform/ct633-ca.pem")
OLD = "https://knowledge.test:18443"
NEW = "https://infra-doc.mailerblend.com"


def run(*args):
    subprocess.run(args, check=True, timeout=150)


def compose(edge, *args):
    files = ["docker-compose.yml", "private/compose.yml"]
    if edge:
        files.append("edge/compose.yml")
    command = ["docker", "compose", "--project-directory", str(BASE), "-p", "infra-knowledge"]
    for file in files:
        command += ["-f", str(BASE / file)]
    run(*command, *args)


def knowledge(action, staged):
    assert socket.gethostname() == "infra-knowledge"
    environment = BASE / ".env"
    dex = BASE / "private/dex.json"
    if action == "prepare":
        before = environment.read_text()
        config = json.loads(dex.read_text())
        assert before.count("OUTLINE_URL=" + OLD + "\n") == 1
        assert before.count("OIDC_ISSUER_URL=" + OLD + "/dex\n") == 1
        assert config["issuer"] == OLD + "/dex"
        assert len(config["staticClients"]) == 1
        client = config["staticClients"][0]
        assert client["redirectURIs"] == [OLD + "/auth/oidc.callback"]
        (staged / "env.before").write_text(before)
        (staged / "dex.before").write_bytes(dex.read_bytes())
        (staged / "env.after").write_text(before.replace("OUTLINE_URL=" + OLD, "OUTLINE_URL=" + NEW)
                                         .replace("OIDC_ISSUER_URL=" + OLD, "OIDC_ISSUER_URL=" + NEW))
        config["issuer"] = NEW + "/dex"
        client["redirectURIs"] = [NEW + "/auth/oidc.callback"]
        (staged / "dex.after").write_text(json.dumps(config, indent=2) + "\n")
        assert not (BASE / "edge").exists()
        (BASE / "edge").mkdir(mode=0o700)
        for file in ("compose.yml", "nginx.conf"):
            (BASE / "edge" / file).write_bytes((staged / file).read_bytes())
        compose(True, "config", "--quiet")
        compose(True, "run", "--rm", "--no-deps", "gateway", "nginx", "-t")
        return
    apply = action == "apply"
    originals = [(environment, "env"), (dex, "dex")]
    for destination, prefix in originals:
        before = (staged / f"{prefix}.before").read_bytes()
        after = (staged / f"{prefix}.after").read_bytes()
        allowed = (before,) if apply else (before, after)
        if destination.read_bytes() not in allowed:
            raise RuntimeError(f"Unexpected configuration drift: {prefix}")
    for destination, prefix in originals:
        destination.write_bytes((staged / f"{prefix}.{'after' if apply else 'before'}").read_bytes())
    compose(apply, "up", "-d", "--no-deps", "gateway", "dex")
    # Dex reads its bind-mounted configuration only on start.
    compose(apply, "restart", "dex")
    compose(apply, "up", "-d", "--no-deps", "outline")


def edge(action, staged):
    assert socket.gethostname() == "edge-router"
    if action == "prepare":
        current = VHOST.read_text()
        anchor = "    location / {\n        proxy_pass http://192.168.1.60:3000;\n"
        assert current.count(anchor) == 1 and current.count("server_name infra-doc.mailerblend.com;") == 2
        (staged / "vhost.before").write_text(current)
        candidate = current.replace(anchor, (staged / "edge-location.conf").read_text())
        (staged / "vhost.after").write_text(candidate)
        assert not CA.exists()
        CA.parent.mkdir(exist_ok=True)
        CA.write_bytes((staged / "ct633-ca.pem").read_bytes())
        CA.chmod(0o644)
        test_config = staged / "nginx-test.conf"
        test_config.write_text(f"events {{}}\nhttp {{ include {staged / 'vhost.after'}; }}\n")
        run("nginx", "-t", "-c", str(test_config))
        return
    apply = action == "apply"
    before = (staged / "vhost.before").read_bytes()
    after = (staged / "vhost.after").read_bytes()
    if VHOST.read_bytes() not in ((before,) if apply else (before, after)):
        raise RuntimeError("Unexpected edge vhost drift")
    VHOST.write_bytes(after if apply else before)
    run("nginx", "-t")
    run("systemctl", "reload", "nginx")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", choices=["knowledge", "edge"])
    parser.add_argument("action", choices=["prepare", "apply", "rollback"])
    parser.add_argument("staged", type=Path)
    args = parser.parse_args()
    (knowledge if args.host == "knowledge" else edge)(args.action, args.staged)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Install a verified static EVA bundle on the loopback origin."""

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import socket
import tarfile
import tempfile
from urllib.request import urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("sha256")
    args = parser.parse_args()
    if socket.gethostname().split(".")[0] != "infra-eva-ui":
        raise SystemExit("Expected infra-eva-ui")
    if hashlib.sha256(args.archive.read_bytes()).hexdigest() != args.sha256:
        raise SystemExit("Bundle checksum mismatch")

    root = Path("/srv/infra-eva-ui")
    if not root.is_dir() or root.is_symlink():
        raise SystemExit("Expected dedicated Nginx origin")
    with tempfile.TemporaryDirectory(prefix=".eva-ui-", dir=root.parent) as stage:
        candidate = Path(stage)
        candidate.chmod(0o755)
        with tarfile.open(args.archive, "r:gz") as archive:
            for member in archive:
                relative = Path(member.name)
                if relative.is_absolute() or ".." in relative.parts:
                    raise SystemExit("Unsafe archive path")
                target = candidate / relative
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with archive.extractfile(member) as source, target.open("xb") as destination:
                        shutil.copyfileobj(source, destination)
                    target.chmod(0o644)
                else:
                    raise SystemExit("Unsupported archive entry")

        index = candidate / "index.html"
        if not index.is_file() or not (candidate / "assets").is_dir():
            raise SystemExit("Expected Vite distribution")
        expected = index.read_bytes()
        if any(root.iterdir()):
            staged = {path.relative_to(candidate): path.read_bytes()
                      for path in candidate.rglob("*") if path.is_file()}
            deployed = {path.relative_to(root): path.read_bytes()
                        for path in root.rglob("*") if path.is_file()}
            if deployed != staged:
                raise SystemExit("Origin already contains a different release")
            with urlopen("http://127.0.0.1:8080/", timeout=5) as response:
                if response.status != 200 or response.read() != expected:
                    raise RuntimeError("Origin served unexpected content")
            print("Verified EVA distribution. No changes")
            return
        os.replace(candidate, root)
        try:
            with urlopen("http://127.0.0.1:8080/", timeout=5) as response:
                if response.status != 200 or response.read() != expected:
                    raise RuntimeError("Origin served unexpected content")
        except Exception:
            os.replace(root, candidate)
            root.mkdir(mode=0o755)
            raise

    print("Verified EVA distribution on the loopback origin")


if __name__ == "__main__":
    main()

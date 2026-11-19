#!/usr/bin/env bash
set -euo pipefail

if [[ $# != 1 || ! ${1:-} =~ ^[a-zA-Z0-9_-]+$ ]]; then
  printf 'Uso: bash scripts/prepare-lxc-notes-plan.sh <service>\n' >&2
  exit 2
fi
service=$1
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
if [[ ! -f "inventory/services/$service.yml" ]]; then
  printf 'Servicio ausente en inventory/services: %s\n' "$service" >&2
  exit 2
fi

umask 077
if ! notes_dir=$(mktemp -d); then
  printf 'ERROR: no se pudo crear el directorio privado del plan.\n' >&2
  exit 1
fi
printf 'Plan privado para %s: %s\n' "$service" "$notes_dir"

step='regeneración del inventario'
trap 'printf "ERROR en %s. Conserva los archivos privados en %s.\n" "$step" "$notes_dir" >&2' ERR
python3 scripts/generate-lxc-inventory.py > "$notes_dir/inventory.log" 2>&1
step='verificación de frescura'
python3 scripts/generate-lxc-inventory.py --check >> "$notes_dir/inventory.log" 2>&1
step='pruebas de inventario'
python3 -m unittest discover -s tests/inventory -q > "$notes_dir/tests.log" 2>&1
step='validación de Terraform'
terraform validate -no-color > "$notes_dir/validate.log" 2>&1

step='lectura de la CA de PVE mediante SSH estricto'
ssh -o ConnectTimeout=10 -o UserKnownHostsFile="$HOME/.ssh/known_hosts" \
  -o StrictHostKeyChecking=yes -o BatchMode=yes pve \
  'cat /etc/pve/pve-root-ca.pem' > "$notes_dir/pve-ca.pem" 2> "$notes_dir/ssh.log"
grep -q -- '-----BEGIN CERTIFICATE-----' "$notes_dir/pve-ca.pem"
export SSL_CERT_FILE="$notes_dir/pve-ca.pem"

step='plan acotado de Terraform con TLS estricto'
target="proxmox_virtual_environment_container.svc[\"$service\"]"
terraform plan -input=false -no-color -parallelism=1 \
  -var=proxmox_tls_insecure=false -target="$target" \
  -out="$notes_dir/notes.tfplan" > "$notes_dir/plan.log" 2>&1
step='exportación del plan a JSON'
terraform show -json "$notes_dir/notes.tfplan" > "$notes_dir/plan.json" 2> "$notes_dir/show.log"

step='validación del alcance del plan'
if ! python3 scripts/validate-lxc-notes-plan.py "$notes_dir/plan.json" \
  --report "$notes_dir/report.json" --service "$service" > "$notes_dir/report.log" 2>&1; then
  if [[ -s "$notes_dir/report.json" ]]; then
    cat -- "$notes_dir/report.json"
    exit 1
  fi
  printf 'ERROR en %s. Consulta el registro privado en %s.\n' "$step" "$notes_dir" >&2
  exit 1
fi
cat -- "$notes_dir/report.json"

#!/bin/bash

# Comprobar si la variable de entorno necesaria existe
if [ -z "$CRM_INGEST_SECRET" ]; then
    echo "❌ Error: La variable CRM_INGEST_SECRET no está definida."
    exit 1
fi

# Ejecutar el proceso de obtención y borrado
curl -sS "https://infra-svc01.mailerblend.com/_svc/v1/linkedin-sourcing/leads?limit=100" \
  -H "X-Api-Key: ${CRM_INGEST_SECRET}" | \
  python3 -c "
import sys, json, subprocess, os

try:
    data = json.load(sys.stdin)
except Exception as e:
    print(f'❌ Error al leer JSON: {e}')
    sys.exit(1)

leads = data.get('items', [])
api_key = os.environ.get('CRM_INGEST_SECRET')

if not leads:
    print('ℹ️ No se encontraron leads para borrar.')
    sys.exit(0)

print(f'🗑️  Borrando {len(leads)} leads...')
print()

for lead in leads:
    lead_id = lead.get('id')
    name = lead.get('full_name', 'Unknown')
    
    if not lead_id:
        continue

    result = subprocess.run([
        'curl', '-sS', '-X', 'DELETE',
        f'https://infra-svc01.mailerblend.com/_svc/v1/linkedin-sourcing/leads/{lead_id}',
        '-H', f'X-Api-Key: {api_key}'
    ], capture_output=True)
    
    if result.returncode == 0:
        print(f'✅ {name}')
    else:
        print(f'❌ Error: {name}')

print()
print('✅ Completado')
"
#chmod +x services/infra-excraper/notas_and_scripts/delete.sh
#./services/infra-excraper/notas_and_scripts/delete.sh
#!/bin/bash

# Script simple para eliminar solo leads con status NEW
# Más seguro que borrar todos
# chmod +x /services/infra-excraper/notas_and_scripts/delete_new_leads.sh
# ./services/infra-excraper/notas_and_scripts/delete_new_leads.sh

echo "🗑️  Eliminando leads con status: NEW"
echo ""

# Obtener leads NEW
RESPONSE=$(curl -sS "https://infra-svc01.mailerblend.com/_svc/v1/linkedin-sourcing/leads?status=NEW&limit=100" \
  -H "X-Api-Key: ${CRM_INGEST_SECRET}")

# Contar y mostrar
COUNT=$(echo "$RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('leads', [])))")

echo "📊 Encontrados: $COUNT leads con status NEW"

if [ "$COUNT" = "0" ]; then
    echo "✅ No hay leads NEW para eliminar"
    exit 0
fi

# Listar
echo "$RESPONSE" | python3 -c "
import sys, json
leads = json.load(sys.stdin).get('leads', [])
for i, lead in enumerate(leads, 1):
    print(f'{i}. {lead[\"full_name\"]} - {lead.get(\"company_name\", \"N/A\")}')
"

echo ""
read -p "⚠️  ¿Eliminar estos $COUNT leads? (SI/no): " confirm

if [ "$confirm" != "SI" ]; then
    echo "❌ Cancelado"
    exit 1
fi

echo ""
echo "🗑️  Eliminando..."

# Eliminar
echo "$RESPONSE" | python3 << 'PYTHON'
import sys, json, subprocess, os

api_key = os.environ.get('CRM_API_KEY')
leads = json.load(sys.stdin).get('leads', [])

for lead in leads:
    lead_id = lead['id']
    name = lead['full_name']
    
    result = subprocess.run([
        'curl', '-sS', '-X', 'DELETE',
        f'https://infra-svc01.mailerblend.com/_svc/v1/linkedin-sourcing/leads/{lead_id}',
        '-H', f'X-Api-Key: {api_key}'
    ], capture_output=True)
    
    if result.returncode == 0:
        print(f'✅ {name}')
PYTHON

echo ""
echo "✅ Completado"
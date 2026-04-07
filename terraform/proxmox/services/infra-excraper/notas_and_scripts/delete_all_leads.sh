#!/bin/bash

# Script para ELIMINAR todos los leads del CRM
# Usa este con CUIDADO - borrará TODOS los leads
# chmod +x services/infra-excraper/notas_and_scripts/delete_all_leads.sh
# ./services/infra-excraper/notas_and_scripts/delete_all_leads.sh
echo "🗑️  Obteniendo lista de leads..."

# Obtener todos los leads (máximo 100 por página)
LEADS=$(curl -sS "https://infra-svc01.mailerblend.com/_svc/v1/linkedin-sourcing/leads?limit=100" \
  -H "X-Api-Key: ${CRM_INGEST_SECRET}")

echo "$LEADS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
leads = data.get('leads', [])
print(f'📊 Total leads encontrados: {len(leads)}')
print()

if len(leads) == 0:
    print('✅ No hay leads para eliminar')
    sys.exit(0)

print('Leads a eliminar:')
for i, lead in enumerate(leads, 1):
    print(f'{i}. {lead[\"full_name\"]} ({lead[\"status\"]})')
"

# Preguntar confirmación
echo ""
read -p "⚠️  ¿Estás seguro de eliminar TODOS estos leads? (escribe 'SI' para confirmar): " confirm

if [ "$confirm" != "SI" ]; then
    echo "❌ Cancelado"
    exit 1
fi

echo ""
echo "🗑️  Eliminando leads..."

# Obtener IDs y eliminar uno por uno
echo "$LEADS" | python3 -c "
import sys, json, subprocess
data = json.load(sys.stdin)
leads = data.get('leads', [])

deleted = 0
failed = 0

for lead in leads:
    lead_id = lead['id']
    name = lead['full_name']
    
    result = subprocess.run([
        'curl', '-sS', '-X', 'DELETE',
        f'https://infra-svc01.mailerblend.com/_svc/v1/linkedin-sourcing/leads/{lead_id}',
        '-H', f'X-Api-Key: ${CRM_API_KEY}'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f'✅ Eliminado: {name}')
        deleted += 1
    else:
        print(f'❌ Error: {name}')
        failed += 1

print()
print(f'📊 Resumen:')
print(f'   ✅ Eliminados: {deleted}')
print(f'   ❌ Fallidos: {failed}')
"

echo ""
echo "✅ Proceso completado"
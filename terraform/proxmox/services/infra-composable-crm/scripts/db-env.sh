#!/bin/bash

#Lee las credenciales automáticamente desde services/infra-composable-crm/compose/supabase/.env
#Verifica que el archivo existe antes de leerlo 
# Valida que todas las variables necesarias se cargaron correctamente
# Mapea las variables de PostgreSQL a tus variables CRM:
#POSTGRES_USER → CRM_DB_USER
#POSTGRES_PASSWORD → CRM_DB_PASS
#POSTGRES_DB → CRM_DB_NAME
#✅ Hace el test de conexión
# Uso:
# source services/infra-composable-crm/scripts/db-env.sh

# Ruta al archivo .env
ENV_FILE="services/infra-composable-crm/compose/supabase/.env"

# Verificar que el archivo existe
if [ ! -f "$ENV_FILE" ]; then
    echo "✗ Error: No se encontró el archivo $ENV_FILE"
    return 1
fi

echo "Cargando variables desde: $ENV_FILE"
echo ""

# Leer las variables del archivo .env
export CRM_DB_USER=$(grep "^POSTGRES_USER=" "$ENV_FILE" | cut -d '=' -f2)
export CRM_DB_PASS=$(grep "^POSTGRES_PASSWORD=" "$ENV_FILE" | cut -d '=' -f2)
export CRM_DB_NAME=$(grep "^POSTGRES_DB=" "$ENV_FILE" | cut -d '=' -f2)

# Verificar que se cargaron las variables
if [ -z "$CRM_DB_USER" ] || [ -z "$CRM_DB_PASS" ] || [ -z "$CRM_DB_NAME" ]; then
    echo "✗ Error: No se pudieron cargar todas las variables del archivo .env"
    echo "  Asegúrate de que el archivo contenga:"
    echo "  - POSTGRES_USER"
    echo "  - POSTGRES_PASSWORD"
    echo "  - POSTGRES_DB"
    return 1
fi

echo "Variables exportadas:"
echo "  CRM_DB_USER: $CRM_DB_USER"
echo "  CRM_DB_NAME: $CRM_DB_NAME"
echo "  CRM_DB_PASS: ****"
echo ""

# Test de conexión
echo "Probando conexión a la base de datos..."
ssh root@192.168.1.118 \
  "docker exec -i supabase-db bash -c \"PGPASSWORD='${CRM_DB_PASS}' psql -U '${CRM_DB_USER}' -d '${CRM_DB_NAME}' -c 'SELECT version();'\"" 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Conexión exitosa a la base de datos!"
else
    echo ""
    echo "✗ Error al conectar a la base de datos"
    return 1
fi
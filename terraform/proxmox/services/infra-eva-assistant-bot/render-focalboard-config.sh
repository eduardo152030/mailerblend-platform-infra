#!/bin/bash

# --- Configuración ---
REMOTE_USER="root"
REMOTE_IP="192.168.1.122"
REMOTE_PATH="/opt/infra-eva-assistant-bot"
FOCALBOARD_DIR="${REMOTE_PATH}/focalboard"

echo "🚀 Iniciando reparación y renderizado de configuración de Focalboard..."

ssh ${REMOTE_USER}@${REMOTE_IP} 'bash -s' << ENDSSH
    set -e
    cd ${REMOTE_PATH}

    # 1. Limpieza preventiva
    # Si config.json existe pero es un directorio (error común de Docker), lo borramos
    if [ -d "${FOCALBOARD_DIR}/config.json" ]; then
        echo "⚠️ Detectado directorio erróneo en config.json. Limpiando..."
        rm -rf "${FOCALBOARD_DIR}/config.json"
    fi

    # 2. Cargar variables de entorno del servidor
    if [ -f .env ]; then
        echo "📖 Cargando variables desde .env..."
        set -a
        source .env
        set +a
    else
        echo "❌ Error: No se encontró el archivo .env en ${REMOTE_PATH}"
        exit 1
    fi

    # 3. Renderizar el template
    if [ -f "${FOCALBOARD_DIR}/config.json.tpl" ]; then
        echo "🛠️ Renderizando config.json desde el template..."
        envsubst < "${FOCALBOARD_DIR}/config.json.tpl" > "${FOCALBOARD_DIR}/config.json"
    else
        echo "❌ Error: No se encontró focalboard/config.json.tpl"
        exit 1
    fi

    # 4. Reiniciar servicio
    echo "🔄 Reiniciando contenedor focalboard..."
    docker compose restart focalboard

    # 5. Verificación
    echo "👀 Verificando logs (esperando 5s)..."
    sleep 5
    docker logs focalboard --tail 20
ENDSSH

echo "✅ Proceso finalizado."
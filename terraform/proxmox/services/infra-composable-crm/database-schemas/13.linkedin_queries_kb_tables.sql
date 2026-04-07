-- =====================================================
-- LinkedIn Queries Knowledge Base - Tables Creation
-- =====================================================
-- Fecha: 2026-02-28
-- Descripción: Crea tablas para gestión de queries con rotación y dedupe
-- Dependencias: pgcrypto extension
-- =====================================================

-- Habilitar extensión para gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =====================================================
-- Tabla principal: linkedin_queries_kb
-- =====================================================
-- Almacena las queries de búsqueda por pack con sistema de prioridad
CREATE TABLE IF NOT EXISTS linkedin_queries_kb (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pack TEXT NOT NULL,                -- GUARDIAN, MOTOR, FORTALEZA, ALL
    query TEXT NOT NULL,                -- Query de búsqueda de LinkedIn
    query_hash TEXT NOT NULL,           -- Hash único para dedupe
    meta JSONB DEFAULT '{}'::jsonb,     -- Metadata adicional
    priority INT DEFAULT 50,            -- Prioridad para ordenamiento
    is_active BOOLEAN DEFAULT TRUE,     -- Habilitada/deshabilitada
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índice único por hash (previene duplicados)
CREATE UNIQUE INDEX IF NOT EXISTS uq_linkedin_queries_kb_hash
    ON linkedin_queries_kb (query_hash);

-- Índice por pack para filtrado rápido
CREATE INDEX IF NOT EXISTS idx_linkedin_queries_kb_pack
    ON linkedin_queries_kb (pack);

-- Índice por pack + activas + prioridad (para queries rotativas)
CREATE INDEX IF NOT EXISTS idx_linkedin_queries_kb_pack_active_priority
    ON linkedin_queries_kb (pack, is_active, priority DESC)
    WHERE is_active = TRUE;

COMMENT ON TABLE linkedin_queries_kb IS 'Queries de búsqueda de LinkedIn por pack con sistema de rotación';
COMMENT ON COLUMN linkedin_queries_kb.query_hash IS 'Hash MD5 de la query para dedupe (calculado automáticamente)';
COMMENT ON COLUMN linkedin_queries_kb.meta IS 'Metadata: {tags, description, expected_results, etc}';
COMMENT ON COLUMN linkedin_queries_kb.priority IS 'Mayor prioridad = se usa más frecuentemente';

-- =====================================================
-- Tabla histórico: linkedin_query_history
-- =====================================================
-- Registra cada vez que se usa una query para evitar repeticiones
CREATE TABLE IF NOT EXISTS linkedin_query_history (
    id BIGSERIAL PRIMARY KEY,
    pack TEXT NOT NULL,
    query TEXT NOT NULL,
    query_hash TEXT NOT NULL,           -- Referencia al hash de linkedin_queries_kb
    used_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índice único por hash (solo 1 registro por query usada)
CREATE UNIQUE INDEX IF NOT EXISTS uq_linkedin_query_history_hash
    ON linkedin_query_history (query_hash);

-- Índice por fecha de uso (para cleanup y rotación)
CREATE INDEX IF NOT EXISTS idx_linkedin_query_history_used_at
    ON linkedin_query_history (used_at DESC);

-- Índice compuesto pack + fecha (para queries disponibles por pack)
CREATE INDEX IF NOT EXISTS idx_linkedin_query_history_pack_used
    ON linkedin_query_history (pack, used_at DESC);

COMMENT ON TABLE linkedin_query_history IS 'Historial de queries usadas para sistema de rotación y dedupe';
COMMENT ON COLUMN linkedin_query_history.query_hash IS 'Hash de la query usada (debe existir en linkedin_queries_kb)';

-- =====================================================
-- Función: Calcular hash automático
-- =====================================================
CREATE OR REPLACE FUNCTION linkedin_queries_kb_set_hash()
RETURNS TRIGGER AS $$
BEGIN
    -- Calcular hash MD5 de pack + query (normalizado)
    NEW.query_hash := md5(LOWER(TRIM(NEW.pack)) || '::' || LOWER(TRIM(NEW.query)));
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para calcular hash automáticamente
DROP TRIGGER IF EXISTS trg_linkedin_queries_kb_hash ON linkedin_queries_kb;
CREATE TRIGGER trg_linkedin_queries_kb_hash
    BEFORE INSERT OR UPDATE OF pack, query
    ON linkedin_queries_kb
    FOR EACH ROW
    EXECUTE FUNCTION linkedin_queries_kb_set_hash();

COMMENT ON FUNCTION linkedin_queries_kb_set_hash() IS 'Calcula hash automáticamente al insertar/actualizar query';

-- =====================================================
-- Función: Obtener queries disponibles (no usadas recientemente)
-- =====================================================
CREATE OR REPLACE FUNCTION get_available_linkedin_queries(
    p_pack TEXT,
    p_limit INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    pack TEXT,
    query TEXT,
    priority INT,
    meta JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        q.id,
        q.pack,
        q.query,
        q.priority,
        q.meta
    FROM linkedin_queries_kb q
    LEFT JOIN linkedin_query_history h ON q.query_hash = h.query_hash
    WHERE 
        q.pack = p_pack
        AND q.is_active = TRUE
        AND h.query_hash IS NULL  -- No está en el historial (nunca usada)
    ORDER BY q.priority DESC, q.created_at ASC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_available_linkedin_queries(TEXT, INT) IS 'Obtiene queries activas que no han sido usadas recientemente';

-- =====================================================
-- Función: Marcar query como usada
-- =====================================================
CREATE OR REPLACE FUNCTION mark_linkedin_query_used(
    p_query_hash TEXT
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO linkedin_query_history (pack, query, query_hash, used_at)
    SELECT pack, query, query_hash, NOW()
    FROM linkedin_queries_kb
    WHERE query_hash = p_query_hash
    ON CONFLICT (query_hash) DO UPDATE
    SET used_at = NOW();
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION mark_linkedin_query_used(TEXT) IS 'Marca una query como usada en el historial';

-- =====================================================
-- Función: Resetear historial (para permitir reutilización)
-- =====================================================
CREATE OR REPLACE FUNCTION reset_linkedin_query_history(
    p_pack TEXT DEFAULT NULL,
    p_older_than_days INT DEFAULT 30
)
RETURNS INT AS $$
DECLARE
    v_deleted INT;
BEGIN
    IF p_pack IS NULL THEN
        -- Resetear todo el historial antiguo
        DELETE FROM linkedin_query_history
        WHERE used_at < NOW() - (p_older_than_days || ' days')::INTERVAL;
    ELSE
        -- Resetear solo para un pack específico
        DELETE FROM linkedin_query_history
        WHERE pack = p_pack
        AND used_at < NOW() - (p_older_than_days || ' days')::INTERVAL;
    END IF;
    
    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RETURN v_deleted;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION reset_linkedin_query_history(TEXT, INT) IS 'Limpia historial antiguo para permitir reutilización de queries';

-- =====================================================
-- Grants (ajustar según tu usuario de aplicación)
-- =====================================================
-- GRANT SELECT, INSERT, UPDATE, DELETE ON linkedin_queries_kb TO your_app_user;
-- GRANT SELECT, INSERT, DELETE ON linkedin_query_history TO your_app_user;
-- GRANT USAGE ON SEQUENCE linkedin_query_history_id_seq TO your_app_user;

-- =====================================================
-- Verificación
-- =====================================================
DO $$
BEGIN
    RAISE NOTICE '✅ Tablas creadas correctamente:';
    RAISE NOTICE '   - linkedin_queries_kb';
    RAISE NOTICE '   - linkedin_query_history';
    RAISE NOTICE '✅ Funciones creadas:';
    RAISE NOTICE '   - linkedin_queries_kb_set_hash() [trigger]';
    RAISE NOTICE '   - get_available_linkedin_queries(pack, limit)';
    RAISE NOTICE '   - mark_linkedin_query_used(hash)';
    RAISE NOTICE '   - reset_linkedin_query_history(pack, days)';
END $$;
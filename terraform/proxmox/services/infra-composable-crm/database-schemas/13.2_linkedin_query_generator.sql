-- =====================================================
-- LinkedIn Query Generator - Sistema Dinámico
-- =====================================================
-- Fecha: 2026-02-28
-- Descripción: Sistema de generación infinita de queries usando templates + variables
-- Ventajas: 
--   - Infinitas combinaciones (roles × industrias × ciudades × templates)
--   - Variación humana natural
--   - Anti-detección LinkedIn
--   - Fácil expansión
-- =====================================================

-- =====================================================
-- Tabla: linkedin_query_generator_config
-- =====================================================
-- Almacena bloques configurables por pack para generar queries dinámicas
CREATE TABLE IF NOT EXISTS linkedin_query_generator_config (
    pack TEXT PRIMARY KEY,                          -- GUARDIAN, MOTOR, FORTALEZA
    roles JSONB NOT NULL,                           -- ["Founder", "CEO", "Director", ...]
    industries JSONB NOT NULL,                      -- ["clínica dental", "gimnasio", ...]
    cities JSONB NOT NULL,                          -- ["Madrid", "Barcelona", "España", ...]
    templates JSONB NOT NULL,                       -- ["{role} {industry} {city}", ...]
    weights JSONB DEFAULT '{}'::jsonb,              -- Opcional: pesos por rol/industria
    is_active BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE linkedin_query_generator_config IS 'Configuración para generación dinámica de queries LinkedIn';
COMMENT ON COLUMN linkedin_query_generator_config.templates IS 'Plantillas con variables: {role}, {industry}, {city}';
COMMENT ON COLUMN linkedin_query_generator_config.weights IS 'Pesos opcionales para priorizar ciertas combinaciones';

-- =====================================================
-- Seed Data - Configuración inicial por pack
-- =====================================================
INSERT INTO linkedin_query_generator_config (pack, roles, industries, cities, templates)
VALUES
-- GUARDIAN: Clínicas y servicios profesionales
('GUARDIAN',
 '["Founder", "CEO", "Propietario", "Gerente", "Director", "Dueño", "Responsable"]'::jsonb,
 '["clínica dental", "clínica estética", "centro médico", "fisioterapia", "academia", "gestoría", "asesoría", "despacho abogados", "consultoría", "centro formación"]'::jsonb,
 '["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao", "Zaragoza", "Málaga", "Murcia", "España"]'::jsonb,
 '[
   "{role} {industry} {city}",
   "{role} de {industry} en {city}",
   "{industry} {city} {role}",
   "{role} {industry} cerca de {city}",
   "{industry} {role} {city}",
   "{role} en {industry} {city}"
 ]'::jsonb
),

-- MOTOR: Talleres y automoción
('MOTOR',
 '["Owner", "Founder", "Gerente", "CEO", "Propietario", "Director", "Responsable"]'::jsonb,
 '["taller mecánico", "taller chapa y pintura", "neumáticos", "taller multimarca", "taller motos", "garage", "taller coches", "mecánica rápida", "ITV", "automoción"]'::jsonb,
 '["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao", "Zaragoza", "España"]'::jsonb,
 '[
   "{role} {industry} {city}",
   "{industry} {city} {role}",
   "{role} de {industry} en {city}",
   "{industry} {role} cerca de {city}",
   "{role} en {industry} {city}"
 ]'::jsonb
),

-- FORTALEZA: Gimnasios y fitness
('FORTALEZA',
 '["Owner", "CEO", "Gerente", "Director", "Propietario", "Fundador", "Responsable"]'::jsonb,
 '["gimnasio", "centro fitness", "box crossfit", "pilates", "centro deportivo", "yoga studio", "entrenamiento personal", "club deportivo", "fitness center"]'::jsonb,
 '["Madrid", "Barcelona", "Valencia", "Málaga", "Sevilla", "Bilbao", "Zaragoza", "España"]'::jsonb,
 '[
   "{role} {industry} {city}",
   "{industry} {city} {role}",
   "{role} de {industry} en {city}",
   "{industry} {role} {city}",
   "{role} en {industry} {city}"
 ]'::jsonb
)
ON CONFLICT (pack) DO UPDATE SET
    roles = EXCLUDED.roles,
    industries = EXCLUDED.industries,
    cities = EXCLUDED.cities,
    templates = EXCLUDED.templates,
    updated_at = NOW();

-- =====================================================
-- Función: Generar queries dinámicas
-- =====================================================
CREATE OR REPLACE FUNCTION generate_linkedin_queries(
    p_pack TEXT,
    p_count INT DEFAULT 10,
    p_exclude_recent_days INT DEFAULT 30
)
RETURNS TABLE (
    query TEXT,
    query_hash TEXT,
    meta JSONB
) AS $$
DECLARE
    v_config RECORD;
    v_role TEXT;
    v_industry TEXT;
    v_city TEXT;
    v_template TEXT;
    v_query TEXT;
    v_hash TEXT;
    v_attempts INT := 0;
    v_max_attempts INT := p_count * 10;  -- Máximo intentos para evitar loop infinito
BEGIN
    -- Obtener configuración del pack
    SELECT * INTO v_config
    FROM linkedin_query_generator_config
    WHERE pack = p_pack AND is_active = TRUE;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Pack % not found or not active in generator config', p_pack;
    END IF;
    
    -- Generar queries hasta alcanzar p_count o máximo de intentos
    WHILE (SELECT COUNT(*) FROM pg_temp.generated_queries) < p_count AND v_attempts < v_max_attempts LOOP
        v_attempts := v_attempts + 1;
        
        -- Seleccionar aleatoriamente: role, industry, city, template
        v_role := (SELECT jsonb_array_elements_text(v_config.roles) ORDER BY random() LIMIT 1);
        v_industry := (SELECT jsonb_array_elements_text(v_config.industries) ORDER BY random() LIMIT 1);
        v_city := (SELECT jsonb_array_elements_text(v_config.cities) ORDER BY random() LIMIT 1);
        v_template := (SELECT jsonb_array_elements_text(v_config.templates) ORDER BY random() LIMIT 1);
        
        -- Generar query reemplazando placeholders
        v_query := v_template;
        v_query := replace(v_query, '{role}', v_role);
        v_query := replace(v_query, '{industry}', v_industry);
        v_query := replace(v_query, '{city}', v_city);
        
        -- Calcular hash
        v_hash := md5(lower(p_pack || '::' || v_query));
        
        -- Verificar que NO esté en historial reciente
        IF NOT EXISTS (
            SELECT 1 FROM linkedin_query_history
            WHERE query_hash = v_hash
            AND used_at > NOW() - (p_exclude_recent_days || ' days')::INTERVAL
        ) THEN
            -- Guardar en tabla temporal
            CREATE TEMP TABLE IF NOT EXISTS pg_temp.generated_queries (
                query TEXT,
                query_hash TEXT,
                meta JSONB
            ) ON COMMIT DROP;
            
            INSERT INTO pg_temp.generated_queries (query, query_hash, meta)
            VALUES (
                v_query,
                v_hash,
                jsonb_build_object(
                    'role', v_role,
                    'industry', v_industry,
                    'city', v_city,
                    'template', v_template,
                    'pack', p_pack
                )
            );
        END IF;
    END LOOP;
    
    -- Retornar queries generadas
    RETURN QUERY
    SELECT g.query, g.query_hash, g.meta
    FROM pg_temp.generated_queries g;
    
    -- Limpiar tabla temporal
    DROP TABLE IF EXISTS pg_temp.generated_queries;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION generate_linkedin_queries(TEXT, INT, INT) IS 
'Genera N queries únicas combinando roles + industries + cities según templates del pack';

-- =====================================================
-- Función: Reservar query (marcar como usada)
-- =====================================================
-- Nota: Esta función ya existe en 13.1, pero la incluimos por completitud
CREATE OR REPLACE FUNCTION reserve_linkedin_query(
    p_pack TEXT,
    p_query TEXT
)
RETURNS TEXT AS $$
DECLARE
    v_hash TEXT;
BEGIN
    -- Calcular hash
    v_hash := md5(lower(p_pack || '::' || p_query));
    
    -- Insertar en historial (o actualizar si ya existe)
    INSERT INTO linkedin_query_history (pack, query, query_hash, used_at)
    VALUES (p_pack, p_query, v_hash, NOW())
    ON CONFLICT (query_hash) DO UPDATE
    SET used_at = NOW();
    
    RETURN v_hash;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION reserve_linkedin_query(TEXT, TEXT) IS 
'Marca una query como usada en el historial para evitar repetición';

-- =====================================================
-- Vista: Estadísticas de queries generables
-- =====================================================
CREATE OR REPLACE VIEW linkedin_query_stats AS
SELECT 
    pack,
    jsonb_array_length(roles) as total_roles,
    jsonb_array_length(industries) as total_industries,
    jsonb_array_length(cities) as total_cities,
    jsonb_array_length(templates) as total_templates,
    jsonb_array_length(roles) * 
    jsonb_array_length(industries) * 
    jsonb_array_length(cities) * 
    jsonb_array_length(templates) as total_possible_combinations,
    is_active,
    updated_at
FROM linkedin_query_generator_config;

COMMENT ON VIEW linkedin_query_stats IS 'Estadísticas de combinaciones posibles por pack';

-- =====================================================
-- Verificación
-- =====================================================
DO $$
DECLARE
    v_guardian_combos BIGINT;
    v_motor_combos BIGINT;
    v_fortaleza_combos BIGINT;
BEGIN
    -- Calcular combinaciones posibles
    SELECT total_possible_combinations INTO v_guardian_combos
    FROM linkedin_query_stats WHERE pack = 'GUARDIAN';
    
    SELECT total_possible_combinations INTO v_motor_combos
    FROM linkedin_query_stats WHERE pack = 'MOTOR';
    
    SELECT total_possible_combinations INTO v_fortaleza_combos
    FROM linkedin_query_stats WHERE pack = 'FORTALEZA';
    
    RAISE NOTICE '✅ Sistema de generación dinámica configurado';
    RAISE NOTICE '';
    RAISE NOTICE 'Combinaciones posibles:';
    RAISE NOTICE '  - GUARDIAN: % queries únicas', v_guardian_combos;
    RAISE NOTICE '  - MOTOR: % queries únicas', v_motor_combos;
    RAISE NOTICE '  - FORTALEZA: % queries únicas', v_fortaleza_combos;
    RAISE NOTICE '  - TOTAL: % queries únicas', v_guardian_combos + v_motor_combos + v_fortaleza_combos;
    RAISE NOTICE '';
    RAISE NOTICE 'Uso:';
    RAISE NOTICE '  SELECT * FROM generate_linkedin_queries(''GUARDIAN'', 10);';
    RAISE NOTICE '  SELECT reserve_linkedin_query(''GUARDIAN'', ''query text'');';
END $$;

-- Mostrar configuración actual
SELECT * FROM linkedin_query_stats ORDER BY pack;
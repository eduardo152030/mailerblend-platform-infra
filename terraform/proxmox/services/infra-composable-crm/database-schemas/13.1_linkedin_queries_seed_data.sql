-- =====================================================
-- LinkedIn Queries - Seed Data
-- =====================================================
-- Fecha: 2026-02-28
-- Descripción: Datos iniciales de queries por pack
-- =====================================================

-- =====================================================
-- Insertar queries iniciales (basadas en ICP actual)
-- =====================================================
-- Nota: El hash se calcula manualmente con md5(lower(pack || '::' || query))
-- para mantener compatibilidad con el trigger
INSERT INTO linkedin_queries_kb (pack, query, query_hash, meta) VALUES
-- PACK: GUARDIAN (Clínicas dentales)
('GUARDIAN', 'Founder clínica dental España', md5(lower('guardian::founder clínica dental españa')), '{"priority": 100, "tags": ["founder", "dental"]}'),
('GUARDIAN', 'Director centro formación Madrid', md5(lower('guardian::director centro formación madrid')), '{"priority": 90, "tags": ["director", "formacion"]}'),
('GUARDIAN', 'Propietario consultoría Barcelona', md5(lower('guardian::propietario consultoría barcelona')), '{"priority": 80, "tags": ["propietario", "consultoria"]}'),
('GUARDIAN', 'CEO servicios profesionales Valencia', md5(lower('guardian::ceo servicios profesionales valencia')), '{"priority": 70, "tags": ["ceo", "servicios"]}'),
('GUARDIAN', 'Director clínica dental Barcelona', md5(lower('guardian::director clínica dental barcelona')), '{"priority": 95, "tags": ["director", "dental", "barcelona"]}'),
('GUARDIAN', 'Propietario clínica odontológica España', md5(lower('guardian::propietario clínica odontológica españa')), '{"priority": 85, "tags": ["propietario", "dental"]}'),
('GUARDIAN', 'CEO dental clinic Spain', md5(lower('guardian::ceo dental clinic spain')), '{"priority": 75, "tags": ["ceo", "dental", "english"]}'),
('GUARDIAN', 'Gerente clínica dental Madrid', md5(lower('guardian::gerente clínica dental madrid')), '{"priority": 80, "tags": ["gerente", "dental"]}'),

-- PACK: MOTOR (Talleres mecánicos / Agencias digitales)
('MOTOR', 'CEO agencia digital España', md5(lower('motor::ceo agencia digital españa')), '{"priority": 100, "tags": ["ceo", "digital"]}'),
('MOTOR', 'Founder agencia marketing Madrid', md5(lower('motor::founder agencia marketing madrid')), '{"priority": 90, "tags": ["founder", "marketing"]}'),
('MOTOR', 'COO servicios digitales Barcelona', md5(lower('motor::coo servicios digitales barcelona')), '{"priority": 80, "tags": ["coo", "digital"]}'),
('MOTOR', 'Director General consultoría Valencia', md5(lower('motor::director general consultoría valencia')), '{"priority": 70, "tags": ["director", "consultoria"]}'),
('MOTOR', 'Propietario taller mecánico España', md5(lower('motor::propietario taller mecánico españa')), '{"priority": 95, "tags": ["propietario", "taller"]}'),
('MOTOR', 'Director taller coches Barcelona', md5(lower('motor::director taller coches barcelona')), '{"priority": 85, "tags": ["director", "taller"]}'),
('MOTOR', 'Gerente automoción Madrid', md5(lower('motor::gerente automoción madrid')), '{"priority": 75, "tags": ["gerente", "auto"]}'),
('MOTOR', 'CEO garage Spain', md5(lower('motor::ceo garage spain')), '{"priority": 70, "tags": ["ceo", "garage", "english"]}'),

-- PACK: FORTALEZA (Gimnasios / Logística)
('FORTALEZA', 'CEO empresa logística España', md5(lower('fortaleza::ceo empresa logística españa')), '{"priority": 100, "tags": ["ceo", "logistica"]}'),
('FORTALEZA', 'COO distribución Madrid', md5(lower('fortaleza::coo distribución madrid')), '{"priority": 90, "tags": ["coo", "distribucion"]}'),
('FORTALEZA', 'Director General eCommerce Barcelona', md5(lower('fortaleza::director general ecommerce barcelona')), '{"priority": 80, "tags": ["director", "ecommerce"]}'),
('FORTALEZA', 'CTO industria Valencia', md5(lower('fortaleza::cto industria valencia')), '{"priority": 70, "tags": ["cto", "industria"]}'),
('FORTALEZA', 'Propietario gimnasio España', md5(lower('fortaleza::propietario gimnasio españa')), '{"priority": 95, "tags": ["propietario", "gym"]}'),
('FORTALEZA', 'Director fitness center Barcelona', md5(lower('fortaleza::director fitness center barcelona')), '{"priority": 85, "tags": ["director", "fitness"]}'),
('FORTALEZA', 'Gerente centro deportivo Madrid', md5(lower('fortaleza::gerente centro deportivo madrid')), '{"priority": 80, "tags": ["gerente", "deporte"]}'),
('FORTALEZA', 'CEO gym Spain', md5(lower('fortaleza::ceo gym spain')), '{"priority": 75, "tags": ["ceo", "gym", "english"]}')
ON CONFLICT (query_hash) DO NOTHING;

-- =====================================================
-- Verificación
-- =====================================================
DO $$
DECLARE
    v_guardian_count INT;
    v_motor_count INT;
    v_fortaleza_count INT;
BEGIN
    SELECT COUNT(*) INTO v_guardian_count FROM linkedin_queries_kb WHERE pack = 'GUARDIAN';
    SELECT COUNT(*) INTO v_motor_count FROM linkedin_queries_kb WHERE pack = 'MOTOR';
    SELECT COUNT(*) INTO v_fortaleza_count FROM linkedin_queries_kb WHERE pack = 'FORTALEZA';
    
    RAISE NOTICE '✅ Queries insertadas:';
    RAISE NOTICE '   - GUARDIAN: % queries', v_guardian_count;
    RAISE NOTICE '   - MOTOR: % queries', v_motor_count;
    RAISE NOTICE '   - FORTALEZA: % queries', v_fortaleza_count;
    RAISE NOTICE '   - TOTAL: % queries', v_guardian_count + v_motor_count + v_fortaleza_count;
END $$;

-- Mostrar queries insertadas
SELECT pack, query, priority, meta->'tags' as tags
FROM linkedin_queries_kb
ORDER BY pack, priority DESC;
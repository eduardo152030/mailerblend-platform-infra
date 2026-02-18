-- ============================================================
-- 🔧 FIX FINAL: Índice para queries diarias
-- En vez de usar DATE(executed_at), usamos rangos
-- ============================================================

-- Crear índice compuesto simple (sin funciones)
CREATE INDEX IF NOT EXISTS idx_activity_type_executed 
ON linkedin_activity_log(activity_type, executed_at DESC);

COMMENT ON INDEX idx_activity_type_executed IS 'Índice para queries de actividad por tipo y fecha (usar rangos en WHERE)';

-- ============================================================
-- VERIFICACIÓN FINAL
-- ============================================================

DO $$
BEGIN
    RAISE NOTICE '═══════════════════════════════════════════════';
    RAISE NOTICE '✅ ÍNDICE CREADO CORRECTAMENTE';
    RAISE NOTICE '═══════════════════════════════════════════════';
    RAISE NOTICE '';
    
    IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_activity_type_executed') THEN
        RAISE NOTICE '✅ Índice idx_activity_type_executed: OK';
    ELSE
        RAISE NOTICE '❌ Índice idx_activity_type_executed: FALTA';
    END IF;
    
    RAISE NOTICE '';
    RAISE NOTICE '💡 USO DEL ÍNDICE:';
    RAISE NOTICE '   En vez de: WHERE DATE(executed_at) = CURRENT_DATE';
    RAISE NOTICE '   Usar:      WHERE executed_at >= CURRENT_DATE';
    RAISE NOTICE '              AND executed_at < CURRENT_DATE + INTERVAL ''1 day''';
    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════';
    RAISE NOTICE '🎯 SISTEMA 100% LISTO';
    RAISE NOTICE '═══════════════════════════════════════════════';
END $$;

-- Test de performance del índice
EXPLAIN (ANALYZE, BUFFERS) 
SELECT COUNT(*) 
FROM linkedin_activity_log 
WHERE activity_type = 'INVITE' 
  AND executed_at >= CURRENT_DATE 
  AND executed_at < CURRENT_DATE + INTERVAL '1 day';
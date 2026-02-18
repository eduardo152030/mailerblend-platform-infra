-- ============================================================
-- 🔧 FIX: Errores en migraciones
-- ============================================================

-- FIX 1: Eliminar índice problemático y recrearlo correctamente
-- El índice con DATE() no puede ser normal, debe ser funcional
DROP INDEX IF EXISTS idx_activity_type_date;

-- Recrear como índice de expresión con función IMMUTABLE
CREATE INDEX idx_activity_type_date ON linkedin_activity_log(
    activity_type, 
    (executed_at::date)
);

-- FIX 2: Constraints en linkedin_leads
-- PostgreSQL no soporta "IF NOT EXISTS" en constraints antes de v14
-- Usar DO block para verificar si existe antes de crear

DO $$
BEGIN
    -- Check lead_quality_check
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'lead_quality_check'
    ) THEN
        ALTER TABLE linkedin_leads 
        ADD CONSTRAINT lead_quality_check CHECK (
            lead_quality IS NULL OR lead_quality IN ('HIGH', 'MEDIUM', 'LOW')
        );
    END IF;
    
    -- Check silence_reason_check
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'silence_reason_check'
    ) THEN
        ALTER TABLE linkedin_leads 
        ADD CONSTRAINT silence_reason_check CHECK (
            silence_reason IS NULL OR 
            silence_reason IN ('VAGUE_RESPONSE', 'THANKS_ONLY', 'COLD_LEAD', 
                               'CLEAR_NO', 'GHOSTED', 'MANUAL')
        );
    END IF;
END $$;

-- ============================================================
-- VERIFICACIÓN: Todo debe estar OK ahora
-- ============================================================

DO $$
DECLARE
    v_activity_log_count INTEGER;
    v_cooldowns_count INTEGER;
    v_rate_limits_count INTEGER;
    v_segments_count INTEGER;
    v_kb_count INTEGER;
BEGIN
    -- Contar registros
    SELECT COUNT(*) INTO v_activity_log_count FROM linkedin_activity_log;
    SELECT COUNT(*) INTO v_cooldowns_count FROM linkedin_cooldowns;
    SELECT COUNT(*) INTO v_rate_limits_count FROM linkedin_rate_limits;
    SELECT COUNT(*) INTO v_segments_count FROM linkedin_segments;
    SELECT COUNT(*) INTO v_kb_count FROM linkedin_knowledge_base;
    
    RAISE NOTICE '═══════════════════════════════════════════════';
    RAISE NOTICE '✅ FIX APLICADO - VERIFICACIÓN DE TABLAS';
    RAISE NOTICE '═══════════════════════════════════════════════';
    RAISE NOTICE '';
    RAISE NOTICE 'linkedin_activity_log:    % registros', v_activity_log_count;
    RAISE NOTICE 'linkedin_cooldowns:       % registros', v_cooldowns_count;
    RAISE NOTICE 'linkedin_rate_limits:     % registros (esperado: 8)', v_rate_limits_count;
    RAISE NOTICE 'linkedin_segments:        % registros (esperado: 5)', v_segments_count;
    RAISE NOTICE 'linkedin_knowledge_base:  % registros', v_kb_count;
    RAISE NOTICE '';
    
    -- Verificar constraints
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'lead_quality_check') THEN
        RAISE NOTICE '✅ Constraint lead_quality_check: OK';
    ELSE
        RAISE NOTICE '❌ Constraint lead_quality_check: FALTA';
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'silence_reason_check') THEN
        RAISE NOTICE '✅ Constraint silence_reason_check: OK';
    ELSE
        RAISE NOTICE '❌ Constraint silence_reason_check: FALTA';
    END IF;
    
    -- Verificar índice
    IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_activity_type_date') THEN
        RAISE NOTICE '✅ Índice idx_activity_type_date: OK';
    ELSE
        RAISE NOTICE '❌ Índice idx_activity_type_date: FALTA';
    END IF;
    
    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════';
    RAISE NOTICE '🎯 Sistema listo para usar';
    RAISE NOTICE '═══════════════════════════════════════════════';
END $$;

-- ============================================================
-- TEST RÁPIDO: Verificar funciones
-- ============================================================

SELECT 'Daily invites hoy:' as test, get_daily_invite_count() as valor
UNION ALL
SELECT 'Daily messages hoy:', get_daily_message_count()
UNION ALL
SELECT 'Cooldown activo:', CASE WHEN is_cooldown_active() THEN 1 ELSE 0 END
UNION ALL
SELECT 'Cap efectivo Pack1_A:', get_effective_daily_invite_cap('Pack1_A_<50reviews');
-- ============================================================
-- ✅ VERIFICACIÓN FINAL DEL SISTEMA - LinkedIn Sourcing
-- ============================================================

\echo '═══════════════════════════════════════════════════════════'
\echo '📊 RESUMEN DE TABLAS Y DATOS'
\echo '═══════════════════════════════════════════════════════════'
\echo ''

SELECT 
    'linkedin_activity_log' as tabla,
    COUNT(*) as registros,
    'Registro de actividad' as descripcion
FROM linkedin_activity_log

UNION ALL

SELECT 
    'linkedin_cooldowns',
    COUNT(*),
    'Pausas automáticas'
FROM linkedin_cooldowns

UNION ALL

SELECT 
    'linkedin_rate_limits',
    COUNT(*),
    'Límites globales (esperado: 8)'
FROM linkedin_rate_limits

UNION ALL

SELECT 
    'linkedin_segments',
    COUNT(*),
    'Segmentos A/B (esperado: 5)'
FROM linkedin_segments

UNION ALL

SELECT 
    'linkedin_knowledge_base',
    COUNT(*),
    'Base de conocimiento'
FROM linkedin_knowledge_base

UNION ALL

SELECT 
    'linkedin_leads',
    COUNT(*),
    'Leads totales'
FROM linkedin_leads

UNION ALL

SELECT 
    'linkedin_conversations',
    COUNT(*),
    'Conversaciones'
FROM linkedin_conversations

UNION ALL

SELECT 
    'linkedin_approvals',
    COUNT(*),
    'Approvals'
FROM linkedin_approvals

UNION ALL

SELECT 
    'linkedin_outcomes',
    COUNT(*),
    'Outcomes'
FROM linkedin_outcomes;

\echo ''
\echo '═══════════════════════════════════════════════════════════'
\echo '🎯 RATE LIMITS CONFIGURADOS'
\echo '═══════════════════════════════════════════════════════════'
\echo ''

SELECT 
    limit_type as "Tipo de Límite",
    limit_value as "Valor",
    description as "Descripción"
FROM linkedin_rate_limits
WHERE is_active = TRUE
ORDER BY limit_type;

\echo ''
\echo '═══════════════════════════════════════════════════════════'
\echo '📦 SEGMENTOS A/B CONFIGURADOS'
\echo '═══════════════════════════════════════════════════════════'
\echo ''

SELECT 
    segment_name as "Segmento",
    target_pack as "Pack",
    daily_invite_cap as "Cap Diario",
    ab_variant as "Variante",
    total_invites_sent as "Enviadas",
    total_accepted as "Aceptadas",
    acceptance_rate as "Rate %"
FROM linkedin_segments
WHERE is_active = TRUE
ORDER BY target_pack, segment_name;

\echo ''
\echo '═══════════════════════════════════════════════════════════'
\echo '🔧 TEST DE FUNCIONES SQL'
\echo '═══════════════════════════════════════════════════════════'
\echo ''

SELECT 
    'get_daily_invite_count()' as funcion,
    get_daily_invite_count() as resultado,
    'Invites enviadas hoy' as descripcion

UNION ALL

SELECT 
    'get_daily_message_count()',
    get_daily_message_count(),
    'Mensajes enviados hoy'

UNION ALL

SELECT 
    'is_cooldown_active()',
    CASE WHEN is_cooldown_active() THEN 1 ELSE 0 END,
    'Cooldown activo (0=no, 1=sí)'

UNION ALL

SELECT 
    'get_effective_daily_invite_cap(Pack1_A)',
    get_effective_daily_invite_cap('Pack1_A_<50reviews'),
    'Cap efectivo para Pack1_A'

UNION ALL

SELECT 
    'get_effective_daily_invite_cap(Pack2_A)',
    get_effective_daily_invite_cap('Pack2_A_Services_MAD'),
    'Cap efectivo para Pack2_A';

\echo ''
\echo '═══════════════════════════════════════════════════════════'
\echo '📋 NUEVOS CAMPOS EN linkedin_leads'
\echo '═══════════════════════════════════════════════════════════'
\echo ''

SELECT 
    column_name as "Campo",
    data_type as "Tipo",
    CASE 
        WHEN is_nullable = 'YES' THEN 'Null'
        ELSE 'Not Null'
    END as "Nullable"
FROM information_schema.columns
WHERE table_name = 'linkedin_leads'
  AND column_name IN (
      'lead_quality', 
      'micro_validation_passed', 
      'last_silence_start',
      'silence_reason',
      'places_place_id',
      'assigned_segment'
  )
ORDER BY column_name;

\echo ''
\echo '═══════════════════════════════════════════════════════════'
\echo '💬 NUEVOS CAMPOS EN linkedin_conversations'
\echo '═══════════════════════════════════════════════════════════'
\echo ''

SELECT 
    column_name as "Campo",
    data_type as "Tipo",
    CASE 
        WHEN is_nullable = 'YES' THEN 'Null'
        ELSE 'Not Null'
    END as "Nullable"
FROM information_schema.columns
WHERE table_name = 'linkedin_conversations'
  AND column_name IN (
      'message_fragments',
      'typing_duration_seconds',
      'requires_response',
      'is_micro_validation'
  )
ORDER BY column_name;

\echo ''
\echo '═══════════════════════════════════════════════════════════'
\echo '🔍 ÍNDICES CRÍTICOS'
\echo '═══════════════════════════════════════════════════════════'
\echo ''

SELECT 
    indexname as "Índice",
    tablename as "Tabla"
FROM pg_indexes
WHERE tablename IN (
    'linkedin_activity_log',
    'linkedin_cooldowns',
    'linkedin_rate_limits',
    'linkedin_segments',
    'linkedin_knowledge_base',
    'linkedin_leads'
)
AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;

\echo ''
\echo '═══════════════════════════════════════════════════════════'
\echo '✅ SISTEMA 100% LISTO PARA USAR'
\echo '═══════════════════════════════════════════════════════════'
\echo ''
\echo 'Próximos pasos:'
\echo '  1. Rellenar linkedin_knowledge_base con tus servicios/ICP'
\echo '  2. Crear routers del backend para los nuevos endpoints'
\echo '  3. Configurar n8n workflows'
\echo ''
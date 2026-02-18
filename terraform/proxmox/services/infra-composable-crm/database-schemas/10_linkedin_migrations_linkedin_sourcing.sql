-- ============================================================
-- 🗄️ MIGRACIONES SQL - LinkedIn Sourcing System
-- Ejecutar en: supabase-db (192.168.1.118)
-- Database: postgres
-- ============================================================

-- ============================================================
-- TABLA 1: linkedin_activity_log
-- Registro de TODA actividad para detectar patrones y aplicar rate limiting
-- ============================================================

CREATE TABLE IF NOT EXISTS linkedin_activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Tipo de actividad
    activity_type VARCHAR(50) NOT NULL,
    -- INVITE, MESSAGE, PROFILE_VIEW, SEARCH, CONNECTION_ACCEPT, POST_ENGAGEMENT
    
    -- Metadata de la actividad
    metadata JSONB,
    -- Ejemplo: {"lead_id": "uuid", "segment": "Pack1_<50reviews", "pack": "GUARDIAN"}
    
    -- Detección de riesgo
    risk_level VARCHAR(20) DEFAULT 'LOW',
    -- LOW, MEDIUM, HIGH
    
    cooldown_triggered BOOLEAN DEFAULT FALSE,
    -- TRUE si esta actividad disparó un cooldown
    
    -- Timestamps
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Índices para queries rápidas
    CONSTRAINT activity_type_check CHECK (
        activity_type IN ('INVITE', 'MESSAGE', 'PROFILE_VIEW', 'SEARCH', 
                         'CONNECTION_ACCEPT', 'POST_ENGAGEMENT', 'LINK_CLICK')
    ),
    
    CONSTRAINT risk_level_check CHECK (
        risk_level IN ('LOW', 'MEDIUM', 'HIGH')
    )
);

CREATE INDEX idx_activity_executed ON linkedin_activity_log(executed_at DESC);
CREATE INDEX idx_activity_type ON linkedin_activity_log(activity_type);
CREATE INDEX idx_activity_type_date ON linkedin_activity_log(activity_type, DATE(executed_at));

COMMENT ON TABLE linkedin_activity_log IS 'Registro de toda actividad en LinkedIn para rate limiting y detección de patrones';

-- ============================================================
-- TABLA 2: linkedin_cooldowns
-- Control de pausas automáticas por patrones o señales de riesgo
-- ============================================================

CREATE TABLE IF NOT EXISTS linkedin_cooldowns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Razón del cooldown
    trigger_reason VARCHAR(100) NOT NULL,
    -- WEEKLY_DEAD_DAY, NEGATIVE_RESPONSES_SPIKE, MAX_CONVERSATIONS_REACHED, 
    -- DAILY_INVITE_CAP_REACHED, DAILY_MESSAGE_CAP_REACHED, MANUAL, etc.
    
    -- Duración
    cooldown_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cooldown_end TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Estado
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata adicional
    metadata JSONB,
    -- Ejemplo: {"negative_count": 3, "created_by": "auto"}
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_cooldown_active ON linkedin_cooldowns(is_active, cooldown_end);
CREATE INDEX idx_cooldown_reason ON linkedin_cooldowns(trigger_reason);

COMMENT ON TABLE linkedin_cooldowns IS 'Pausas automáticas para proteger la cuenta de LinkedIn';

-- ============================================================
-- TABLA 3: linkedin_rate_limits
-- Configuración global de límites (editable desde UI)
-- ============================================================

CREATE TABLE IF NOT EXISTS linkedin_rate_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Tipo de límite
    limit_type VARCHAR(50) NOT NULL UNIQUE,
    -- DAILY_INVITES_GLOBAL, DAILY_MESSAGES_GLOBAL, 
    -- HOURLY_PROFILE_VIEWS, WEEKLY_DEAD_DAYS, etc.
    
    -- Valor del límite
    limit_value INTEGER NOT NULL,
    
    -- Metadata
    description TEXT,
    
    -- Control
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insertar límites por defecto (perfil BAJO PERFIL)
INSERT INTO linkedin_rate_limits (limit_type, limit_value, description) VALUES
    ('DAILY_INVITES_GLOBAL', 20, 'Máximo de invitaciones por día (perfil bajo: 15-25)'),
    ('DAILY_MESSAGES_GLOBAL', 50, 'Máximo de mensajes por día'),
    ('HOURLY_PROFILE_VIEWS', 15, 'Máximo de perfiles vistos por hora'),
    ('MAX_CONCURRENT_CONVERSATIONS', 5, 'Máximo de conversaciones activas simultáneas'),
    ('WEEKLY_DEAD_DAYS_COUNT', 2, 'Días muertos por semana (0 actividad)'),
    ('NEGATIVE_RESPONSES_THRESHOLD', 3, 'Respuestas negativas para disparar cooldown 48h'),
    ('MESSAGE_FRAGMENT_MIN_DELAY_SEC', 3, 'Delay mínimo entre fragmentos de mensaje (segundos)'),
    ('MESSAGE_FRAGMENT_MAX_DELAY_SEC', 8, 'Delay máximo entre fragmentos de mensaje (segundos)')
ON CONFLICT (limit_type) DO NOTHING;

COMMENT ON TABLE linkedin_rate_limits IS 'Límites globales configurables para rate limiting';

-- ============================================================
-- TABLA 4: linkedin_segments
-- Segmentos A/B testing con caps individuales
-- ============================================================

CREATE TABLE IF NOT EXISTS linkedin_segments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Nombre del segmento
    segment_name VARCHAR(100) NOT NULL UNIQUE,
    -- Ejemplo: "Pack1_A_<50reviews", "Pack2_B_Services_MAD"
    
    -- Pack asociado
    target_pack VARCHAR(50),
    -- GUARDIAN, MOTOR, FORTALEZA
    
    -- Cap diario de invites ESPECÍFICO para este segmento
    daily_invite_cap INTEGER DEFAULT 10,
    -- Overridea el global si es menor
    
    -- Descripción
    description TEXT,
    
    -- A/B testing metadata
    ab_variant VARCHAR(10),
    -- A, B, C, CONTROL
    
    test_hypothesis TEXT,
    -- "Hipótesis: Agencias <50 reviews tienen mejor acceptance rate"
    
    -- Activo/inactivo
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Stats acumuladas (se actualizan vía triggers o n8n)
    total_invites_sent INTEGER DEFAULT 0,
    total_accepted INTEGER DEFAULT 0,
    acceptance_rate DECIMAL(5,2) DEFAULT 0.0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT segment_pack_check CHECK (
        target_pack IS NULL OR 
        target_pack IN ('GUARDIAN', 'MOTOR', 'FORTALEZA')
    )
);

-- Insertar segmentos de ejemplo
INSERT INTO linkedin_segments (segment_name, target_pack, daily_invite_cap, description, ab_variant) VALUES
    ('Pack1_A_<50reviews', 'GUARDIAN', 10, 'GUARDIAN - Agencias/ecommerce con <50 reviews', 'A'),
    ('Pack1_B_50-200reviews', 'GUARDIAN', 8, 'GUARDIAN - Empresas con 50-200 reviews', 'B'),
    ('Pack2_A_Services_MAD', 'MOTOR', 6, 'MOTOR - Agencias de servicios en Madrid', 'A'),
    ('Pack2_B_SaaS_BCN', 'MOTOR', 5, 'MOTOR - SaaS en Barcelona', 'B'),
    ('Pack3_Logistics', 'FORTALEZA', 4, 'FORTALEZA - Empresas de logística', 'A')
ON CONFLICT (segment_name) DO NOTHING;

CREATE INDEX idx_segment_active ON linkedin_segments(is_active);
CREATE INDEX idx_segment_pack ON linkedin_segments(target_pack);

COMMENT ON TABLE linkedin_segments IS 'Segmentos para A/B testing con caps de invites individuales';

-- ============================================================
-- TABLA 5: linkedin_knowledge_base
-- Base de conocimiento: servicios, ICP, objeciones, FAQs
-- ============================================================

CREATE TABLE IF NOT EXISTS linkedin_knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Categoría de conocimiento
    category VARCHAR(100) NOT NULL,
    -- SERVICES, ICP_DEFINITION, PAIN_POINTS, OBJECTIONS, 
    -- FAQ, CASE_STUDIES, PRICING, VALUE_PROPS, DIFFERENTIATORS
    
    -- Subcategoría (para servicios, pack específico, etc.)
    subcategory VARCHAR(100),
    
    -- Título corto
    title VARCHAR(200) NOT NULL,
    
    -- Contenido estructurado (JSON con toda la info)
    content JSONB NOT NULL,
    
    -- Para qué pack aplica
    target_pack VARCHAR(50),
    -- GUARDIAN, MOTOR, FORTALEZA, ALL
    
    -- Prioridad para ranking en respuestas
    priority INTEGER DEFAULT 50,
    -- 1-100, mayor = más importante
    
    -- Activo/inactivo
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT kb_category_check CHECK (
        category IN ('SERVICES', 'ICP_DEFINITION', 'PAIN_POINTS', 
                     'OBJECTIONS', 'FAQ', 'CASE_STUDIES', 'PRICING', 
                     'VALUE_PROPS', 'DIFFERENTIATORS', 'GOOGLE_MAPS_STRATEGY')
    ),
    
    CONSTRAINT kb_target_pack_check CHECK (
        target_pack IS NULL OR 
        target_pack IN ('GUARDIAN', 'MOTOR', 'FORTALEZA', 'ALL')
    )
);

CREATE INDEX idx_kb_category ON linkedin_knowledge_base(category);
CREATE INDEX idx_kb_active ON linkedin_knowledge_base(is_active);
CREATE INDEX idx_kb_target_pack ON linkedin_knowledge_base(target_pack);
CREATE INDEX idx_kb_priority ON linkedin_knowledge_base(priority DESC);

COMMENT ON TABLE linkedin_knowledge_base IS 'Base de conocimiento estructurada para IA (servicios, ICP, objeciones, etc.)';

-- ============================================================
-- TABLA 6: Modificar linkedin_leads (añadir campos nuevos)
-- ============================================================

-- Lead quality (post-conversación)
ALTER TABLE linkedin_leads 
ADD COLUMN IF NOT EXISTS lead_quality VARCHAR(20);

-- Micro-validación antes de CTA
ALTER TABLE linkedin_leads 
ADD COLUMN IF NOT EXISTS micro_validation_passed BOOLEAN DEFAULT FALSE;

-- Silencio inteligente
ALTER TABLE linkedin_leads 
ADD COLUMN IF NOT EXISTS last_silence_start TIMESTAMP WITH TIME ZONE;

ALTER TABLE linkedin_leads 
ADD COLUMN IF NOT EXISTS silence_reason VARCHAR(100);

-- Google Maps data
ALTER TABLE linkedin_leads 
ADD COLUMN IF NOT EXISTS places_place_id VARCHAR(200);

-- Segment asignado (para A/B testing)
ALTER TABLE linkedin_leads 
ADD COLUMN IF NOT EXISTS assigned_segment VARCHAR(100);

-- Constraints
ALTER TABLE linkedin_leads 
ADD CONSTRAINT IF NOT EXISTS lead_quality_check CHECK (
    lead_quality IS NULL OR lead_quality IN ('HIGH', 'MEDIUM', 'LOW')
);

ALTER TABLE linkedin_leads 
ADD CONSTRAINT IF NOT EXISTS silence_reason_check CHECK (
    silence_reason IS NULL OR 
    silence_reason IN ('VAGUE_RESPONSE', 'THANKS_ONLY', 'COLD_LEAD', 
                       'CLEAR_NO', 'GHOSTED', 'MANUAL')
);

-- Índices nuevos
CREATE INDEX IF NOT EXISTS idx_leads_quality ON linkedin_leads(lead_quality);
CREATE INDEX IF NOT EXISTS idx_leads_segment ON linkedin_leads(assigned_segment);
CREATE INDEX IF NOT EXISTS idx_leads_silence ON linkedin_leads(last_silence_start) 
    WHERE last_silence_start IS NOT NULL;

COMMENT ON COLUMN linkedin_leads.lead_quality IS 'Calidad del lead evaluada post-conversación (HIGH/MEDIUM/LOW)';
COMMENT ON COLUMN linkedin_leads.micro_validation_passed IS 'TRUE si respondió afirmativamente a micro-validación antes del CTA';
COMMENT ON COLUMN linkedin_leads.assigned_segment IS 'Segmento A/B testing asignado';

-- ============================================================
-- TABLA 7: Modificar linkedin_conversations (añadir campos nuevos)
-- ============================================================

-- Fragmentación de mensajes
ALTER TABLE linkedin_conversations 
ADD COLUMN IF NOT EXISTS message_fragments JSONB;

-- Duración de escritura simulada
ALTER TABLE linkedin_conversations 
ADD COLUMN IF NOT EXISTS typing_duration_seconds INTEGER;

-- ¿Requiere respuesta?
ALTER TABLE linkedin_conversations 
ADD COLUMN IF NOT EXISTS requires_response BOOLEAN DEFAULT TRUE;

-- ¿Es micro-validación?
ALTER TABLE linkedin_conversations 
ADD COLUMN IF NOT EXISTS is_micro_validation BOOLEAN DEFAULT FALSE;

COMMENT ON COLUMN linkedin_conversations.message_fragments IS 'Array de fragmentos para envío progresivo simulando escritura humana';
COMMENT ON COLUMN linkedin_conversations.typing_duration_seconds IS 'Segundos que "tardó en escribir" el mensaje (simulado)';
COMMENT ON COLUMN linkedin_conversations.requires_response IS 'FALSE si es mensaje que no merece respuesta (gracias, vago, etc.)';
COMMENT ON COLUMN linkedin_conversations.is_micro_validation IS 'TRUE si es pregunta de micro-validación antes del CTA';

-- ============================================================
-- VISTA: Daily Activity Stats (para rate limiting)
-- ============================================================

CREATE OR REPLACE VIEW linkedin_daily_activity_stats AS
SELECT
    DATE(executed_at) as activity_date,
    activity_type,
    COUNT(*) as count,
    MAX(executed_at) as last_activity_at
FROM linkedin_activity_log
WHERE executed_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(executed_at), activity_type
ORDER BY activity_date DESC, activity_type;

COMMENT ON VIEW linkedin_daily_activity_stats IS 'Estadísticas diarias de actividad para monitorear rate limiting';

-- ============================================================
-- FUNCIÓN: Get current daily invite count
-- ============================================================

CREATE OR REPLACE FUNCTION get_daily_invite_count()
RETURNS INTEGER AS $$
    SELECT COUNT(*)::INTEGER
    FROM linkedin_activity_log
    WHERE activity_type = 'INVITE'
      AND DATE(executed_at) = CURRENT_DATE;
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION get_daily_invite_count IS 'Cuenta invitaciones enviadas hoy';

-- ============================================================
-- FUNCIÓN: Get current daily message count
-- ============================================================

CREATE OR REPLACE FUNCTION get_daily_message_count()
RETURNS INTEGER AS $$
    SELECT COUNT(*)::INTEGER
    FROM linkedin_activity_log
    WHERE activity_type = 'MESSAGE'
      AND DATE(executed_at) = CURRENT_DATE;
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION get_daily_message_count IS 'Cuenta mensajes enviados hoy';

-- ============================================================
-- FUNCIÓN: Check if cooldown is active
-- ============================================================

CREATE OR REPLACE FUNCTION is_cooldown_active()
RETURNS BOOLEAN AS $$
    SELECT EXISTS(
        SELECT 1
        FROM linkedin_cooldowns
        WHERE is_active = TRUE
          AND cooldown_end > NOW()
    );
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION is_cooldown_active IS 'Verifica si hay algún cooldown activo en este momento';

-- ============================================================
-- FUNCIÓN: Get effective daily invite cap
-- Para un segmento específico, retorna el cap efectivo
-- (mínimo entre global y segment-specific)
-- ============================================================

CREATE OR REPLACE FUNCTION get_effective_daily_invite_cap(p_segment VARCHAR)
RETURNS INTEGER AS $$
DECLARE
    v_global_cap INTEGER;
    v_segment_cap INTEGER;
BEGIN
    -- Obtener cap global
    SELECT limit_value INTO v_global_cap
    FROM linkedin_rate_limits
    WHERE limit_type = 'DAILY_INVITES_GLOBAL'
      AND is_active = TRUE;
    
    -- Si no hay global, usar 20 por defecto
    IF v_global_cap IS NULL THEN
        v_global_cap := 20;
    END IF;
    
    -- Obtener cap del segmento
    SELECT daily_invite_cap INTO v_segment_cap
    FROM linkedin_segments
    WHERE segment_name = p_segment
      AND is_active = TRUE;
    
    -- Si el segmento no existe o no tiene cap, usar el global
    IF v_segment_cap IS NULL THEN
        RETURN v_global_cap;
    END IF;
    
    -- Retornar el mínimo entre global y segment
    RETURN LEAST(v_global_cap, v_segment_cap);
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_effective_daily_invite_cap IS 'Calcula el cap efectivo de invites diarias: min(global, segment)';

-- ============================================================
-- TRIGGER: Update segment stats on lead status change
-- ============================================================

CREATE OR REPLACE FUNCTION update_segment_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Si el lead cambió a ACCEPTED y tiene segment asignado
    IF NEW.status = 'ACCEPTED' AND OLD.status != 'ACCEPTED' AND NEW.assigned_segment IS NOT NULL THEN
        UPDATE linkedin_segments
        SET
            total_accepted = total_accepted + 1,
            acceptance_rate = ROUND((total_accepted + 1.0) / NULLIF(total_invites_sent, 0) * 100, 2),
            updated_at = NOW()
        WHERE segment_name = NEW.assigned_segment;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_segment_stats
    AFTER UPDATE OF status ON linkedin_leads
    FOR EACH ROW
    EXECUTE FUNCTION update_segment_stats();

COMMENT ON FUNCTION update_segment_stats IS 'Actualiza estadísticas de segmento cuando un lead es aceptado';

-- ============================================================
-- VERIFICACIÓN FINAL
-- ============================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migraciones completadas exitosamente';
    RAISE NOTICE '';
    RAISE NOTICE 'Tablas creadas:';
    RAISE NOTICE '  - linkedin_activity_log';
    RAISE NOTICE '  - linkedin_cooldowns';
    RAISE NOTICE '  - linkedin_rate_limits (con valores por defecto)';
    RAISE NOTICE '  - linkedin_segments (con segmentos de ejemplo)';
    RAISE NOTICE '  - linkedin_knowledge_base';
    RAISE NOTICE '';
    RAISE NOTICE 'Campos añadidos a linkedin_leads:';
    RAISE NOTICE '  - lead_quality, micro_validation_passed, last_silence_start';
    RAISE NOTICE '  - silence_reason, places_place_id, assigned_segment';
    RAISE NOTICE '';
    RAISE NOTICE 'Campos añadidos a linkedin_conversations:';
    RAISE NOTICE '  - message_fragments, typing_duration_seconds';
    RAISE NOTICE '  - requires_response, is_micro_validation';
    RAISE NOTICE '';
    RAISE NOTICE 'Funciones creadas:';
    RAISE NOTICE '  - get_daily_invite_count()';
    RAISE NOTICE '  - get_daily_message_count()';
    RAISE NOTICE '  - is_cooldown_active()';
    RAISE NOTICE '  - get_effective_daily_invite_cap(segment)';
    RAISE NOTICE '';
    RAISE NOTICE '🎯 Rate limits configurados:';
    RAISE NOTICE '  - Daily invites: 20 (perfil bajo)';
    RAISE NOTICE '  - Daily messages: 50';
    RAISE NOTICE '  - Max concurrent conversations: 5';
END $$;
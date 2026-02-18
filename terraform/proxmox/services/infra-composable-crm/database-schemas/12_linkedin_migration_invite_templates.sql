-- ============================================================
-- TABLA: linkedin_invite_templates
-- Propósito: Templates de mensajes de invitación para A/B testing
-- ============================================================

CREATE TABLE IF NOT EXISTS linkedin_invite_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identificación del template
    template_name VARCHAR(100) NOT NULL UNIQUE, -- "professional_neutral_v1", "micro_contextual_v1"
    template_type VARCHAR(50) NOT NULL, -- "PROFESSIONAL_NEUTRAL", "MICRO_CONTEXTUAL", "CUSTOM"
    display_name VARCHAR(200) NOT NULL, -- "Profesional Neutral - Conexión Simple"
    
    -- Template con variables
    template_text TEXT NOT NULL,
    -- Ejemplo: "Hola {{nombre}}, estoy conectando con perfiles de {{rol}} en {{ciudad}}. Me encantaría sumar tu perspectiva."
    
    -- Variables requeridas (JSON array)
    required_variables JSONB DEFAULT '[]'::jsonb,
    -- ["nombre", "rol", "ciudad"]
    
    -- Pack objetivo
    target_pack VARCHAR(50), -- "GUARDIAN", "MOTOR", "FORTALEZA", "ALL"
    
    -- A/B Testing
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false, -- Solo 1 puede ser default por pack
    weight INTEGER DEFAULT 50, -- Peso para distribución (0-100, total debe ser 100)
    
    -- Métricas
    times_sent INTEGER DEFAULT 0,
    times_accepted INTEGER DEFAULT 0,
    acceptance_rate DECIMAL(5,2) DEFAULT 0.00, -- Calculado automáticamente
    
    -- Metadata
    description TEXT, -- "Mensaje corto y profesional sin pitch de venta"
    notes TEXT, -- "Funciona bien con founders de PYMEs"
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100),
    
    -- Constraints
    CONSTRAINT valid_weight CHECK (weight >= 0 AND weight <= 100),
    CONSTRAINT valid_acceptance_rate CHECK (acceptance_rate >= 0 AND acceptance_rate <= 100)
);

-- Índices
CREATE INDEX idx_invite_templates_active ON linkedin_invite_templates(is_active);
CREATE INDEX idx_invite_templates_pack ON linkedin_invite_templates(target_pack);
CREATE INDEX idx_invite_templates_type ON linkedin_invite_templates(template_type);
CREATE INDEX idx_invite_templates_acceptance ON linkedin_invite_templates(acceptance_rate DESC);

-- Trigger para actualizar acceptance_rate automáticamente
CREATE OR REPLACE FUNCTION update_template_acceptance_rate()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.times_sent > 0 THEN
        NEW.acceptance_rate := (NEW.times_accepted::DECIMAL / NEW.times_sent::DECIMAL) * 100;
    ELSE
        NEW.acceptance_rate := 0.00;
    END IF;
    
    NEW.updated_at := NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_template_acceptance_rate
    BEFORE UPDATE OF times_sent, times_accepted ON linkedin_invite_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_template_acceptance_rate();

-- ============================================================
-- POBLAR CON LOS 2 TEMPLATES INICIALES
-- ============================================================

-- Template 1: Profesional Neutral
INSERT INTO linkedin_invite_templates (
    template_name,
    template_type,
    display_name,
    template_text,
    required_variables,
    target_pack,
    is_active,
    is_default,
    weight,
    description,
    notes
) VALUES (
    'professional_neutral_v1',
    'PROFESSIONAL_NEUTRAL',
    'Profesional Neutral - Conexión Simple',
    'Hola {{nombre}}, estoy conectando con perfiles de {{rol}} en {{ciudad}}. Me encantaría sumar tu perspectiva.',
    '["nombre", "rol", "ciudad"]'::jsonb,
    'ALL',
    true,
    true,
    50,
    'Mensaje corto y profesional sin pitch de venta. Honesto, contextual, no activa defensas.',
    'Funciona bien como default para todos los packs. Acceptance rate esperado: 25-35%'
);

-- Template 2: Micro-contextual
INSERT INTO linkedin_invite_templates (
    template_name,
    template_type,
    display_name,
    template_text,
    required_variables,
    target_pack,
    is_active,
    is_default,
    weight,
    description,
    notes
) VALUES (
    'micro_contextual_v1',
    'MICRO_CONTEXTUAL',
    'Micro-contextual - Mención de Empresa',
    'Hola {{nombre}}, vi que trabajas en {{empresa}} y me pareció interesante lo que estáis haciendo. Encantado de conectar.',
    '["nombre", "empresa"]'::jsonb,
    'ALL',
    true,
    false,
    50,
    'Personalización ligera basada en la empresa. No exagera, no inventa dolor.',
    'Requiere empresa conocida. Acceptance rate esperado: 30-40% si la empresa es relevante.'
);

-- ============================================================
-- FUNCIÓN: get_template_for_lead (A/B testing automático)
-- ============================================================

CREATE OR REPLACE FUNCTION get_template_for_lead(
    p_pack VARCHAR(50) DEFAULT 'ALL'
)
RETURNS TABLE (
    template_id UUID,
    template_name VARCHAR,
    template_text TEXT,
    required_variables JSONB
) AS $$
DECLARE
    v_random INTEGER;
    v_total_weight INTEGER;
BEGIN
    -- Calcular peso total de templates activos para este pack
    SELECT SUM(weight) INTO v_total_weight
    FROM linkedin_invite_templates
    WHERE is_active = TRUE
      AND (target_pack = p_pack OR target_pack = 'ALL');
    
    -- Si no hay templates activos, usar el default
    IF v_total_weight IS NULL OR v_total_weight = 0 THEN
        RETURN QUERY
        SELECT 
            t.id,
            t.template_name,
            t.template_text,
            t.required_variables
        FROM linkedin_invite_templates t
        WHERE is_default = TRUE
        LIMIT 1;
        RETURN;
    END IF;
    
    -- Generar número random basado en el peso total
    v_random := floor(random() * v_total_weight)::INTEGER;
    
    -- Seleccionar template según peso (A/B testing weighted)
    RETURN QUERY
    WITH weighted_templates AS (
        SELECT 
            id,
            template_name,
            template_text,
            required_variables,
            SUM(weight) OVER (ORDER BY id) as cumulative_weight
        FROM linkedin_invite_templates
        WHERE is_active = TRUE
          AND (target_pack = p_pack OR target_pack = 'ALL')
    )
    SELECT 
        id,
        template_name,
        template_text,
        required_variables
    FROM weighted_templates
    WHERE cumulative_weight > v_random
    ORDER BY cumulative_weight
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- FUNCIÓN: increment_template_stats (para tracking)
-- ============================================================

CREATE OR REPLACE FUNCTION increment_template_stats(
    p_template_id UUID,
    p_stat_type VARCHAR -- "sent" o "accepted"
)
RETURNS VOID AS $$
BEGIN
    IF p_stat_type = 'sent' THEN
        UPDATE linkedin_invite_templates
        SET times_sent = times_sent + 1
        WHERE id = p_template_id;
    ELSIF p_stat_type = 'accepted' THEN
        UPDATE linkedin_invite_templates
        SET times_accepted = times_accepted + 1
        WHERE id = p_template_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- AÑADIR COLUMNA A linkedin_leads PARA TRACKING
-- ============================================================

ALTER TABLE linkedin_leads
ADD COLUMN IF NOT EXISTS invite_template_id UUID REFERENCES linkedin_invite_templates(id),
ADD COLUMN IF NOT EXISTS invite_template_name VARCHAR(100);

CREATE INDEX IF NOT EXISTS idx_leads_invite_template ON linkedin_leads(invite_template_id);

-- ============================================================
-- COMENTARIOS
-- ============================================================

COMMENT ON TABLE linkedin_invite_templates IS 'Templates de mensajes de invitación con A/B testing';
COMMENT ON COLUMN linkedin_invite_templates.template_name IS 'Identificador único del template (slug)';
COMMENT ON COLUMN linkedin_invite_templates.template_type IS 'Tipo de estrategia: PROFESSIONAL_NEUTRAL, MICRO_CONTEXTUAL, CUSTOM';
COMMENT ON COLUMN linkedin_invite_templates.template_text IS 'Texto con variables {{nombre}}, {{empresa}}, etc';
COMMENT ON COLUMN linkedin_invite_templates.required_variables IS 'Array JSON de variables requeridas';
COMMENT ON COLUMN linkedin_invite_templates.weight IS 'Peso para A/B testing (0-100). Suma debe ser 100 para templates activos';
COMMENT ON COLUMN linkedin_invite_templates.acceptance_rate IS 'Porcentaje de aceptación calculado automáticamente';

-- ============================================================
-- VERIFICACIÓN
-- ============================================================

SELECT 
    template_name,
    display_name,
    template_type,
    weight,
    is_active,
    is_default,
    times_sent,
    times_accepted,
    acceptance_rate
FROM linkedin_invite_templates
ORDER BY template_type, created_at;

-- Test función A/B
SELECT * FROM get_template_for_lead('GUARDIAN');
SELECT * FROM get_template_for_lead('MOTOR');
SELECT * FROM get_template_for_lead('ALL');
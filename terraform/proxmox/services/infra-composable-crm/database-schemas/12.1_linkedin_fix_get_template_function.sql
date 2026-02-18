-- ============================================================
-- FIX: get_template_for_lead - Corregir ambigüedad de nombres
-- ============================================================

DROP FUNCTION IF EXISTS get_template_for_lead(VARCHAR);

CREATE OR REPLACE FUNCTION get_template_for_lead(
    p_pack VARCHAR(50) DEFAULT 'ALL'
)
RETURNS TABLE (
    template_id UUID,
    template_name_out VARCHAR,
    template_text_out TEXT,
    required_variables_out JSONB
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
            t.id as template_id,
            t.template_name as template_name_out,
            t.template_text as template_text_out,
            t.required_variables as required_variables_out
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
            t.id,
            t.template_name,
            t.template_text,
            t.required_variables,
            SUM(t.weight) OVER (ORDER BY t.id) as cumulative_weight
        FROM linkedin_invite_templates t
        WHERE t.is_active = TRUE
          AND (t.target_pack = p_pack OR t.target_pack = 'ALL')
    )
    SELECT 
        wt.id as template_id,
        wt.template_name as template_name_out,
        wt.template_text as template_text_out,
        wt.required_variables as required_variables_out
    FROM weighted_templates wt
    WHERE wt.cumulative_weight > v_random
    ORDER BY wt.cumulative_weight
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Test
SELECT * FROM get_template_for_lead('GUARDIAN');
SELECT * FROM get_template_for_lead('MOTOR');
SELECT * FROM get_template_for_lead('ALL');

-- Verificar que funciona varias veces (A/B testing random)
SELECT 
    template_name_out,
    COUNT(*) as selected_times
FROM (
    SELECT * FROM get_template_for_lead('ALL')
    FROM generate_series(1, 100)
) subq
GROUP BY template_name_out
ORDER BY selected_times DESC;
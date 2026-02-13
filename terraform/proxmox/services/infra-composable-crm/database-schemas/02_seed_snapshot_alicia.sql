cat > services/infra-composable-crm/database-schemas/04_seed_snapshot_alicia.sql <<'SQL'
-- Seed "con historia" para Snapshot 360º (Alicia)
-- Idempotente por keys naturales (quote_number / invoice_number) y por combinación estable de campos en tablas sin unique.
-- Contacto objetivo: Alicia (por email)
--
-- Tablas:
--  - parametros_utm (NOTNULL: contacto_id) + CHECK ads_platform
--  - formulario_web (NOTNULL: contacto_id, mensaje, servicio_relacionado) + CHECK servicio_relacionado, como_nos_conociste
--  - oportunidades (NOTNULL: contacto_id, deal_name) + CHECK estado, lead_tag, next_action, pack, prioridad, currency, probabilidad
--  - historial (NOTNULL: subject, type) + CHECK type, outcome + relationship check (contacto_id||oportunidad_id||linkedin_lead_id)
--  - pendientes (NOTNULL: title) + CHECK status, priority + relationship check
--  - presupuestos (NOTNULL: contacto_id, oportunidad_id, quote_number, quote_value, title) + CHECK currency, status
--  - facturas (NOTNULL: contacto_id, oportunidad_id, invoice_number, invoice_value, issue_date, due_date) + CHECK currency, status, payment_method

WITH
contact AS (
  SELECT id AS contacto_id
  FROM contactos
  WHERE email = 'alicia@pyme-tech.es'
  LIMIT 1
),

-- 1) UTM (1 fila)
ins_utm AS (
  INSERT INTO parametros_utm (
    contacto_id,
    ads_platform,
    first_visit_at,
    created_at,
    utm_source,
    utm_medium,
    utm_campaign,
    gclid
  )
  SELECT
    c.contacto_id,
    'GOOGLE',
    now() - interval '5 days',
    now() - interval '5 days',
    'google',
    'cpc',
    'nt_cloud_devops_barcelona',
    'Cj0KCQiA_seed_gclid'
  FROM contact c
  WHERE NOT EXISTS (
    SELECT 1 FROM parametros_utm u
    WHERE u.contacto_id = c.contacto_id
      AND u.utm_campaign = 'nt_cloud_devops_barcelona'
      AND u.utm_source = 'google'
      AND u.utm_medium = 'cpc'
  )
  RETURNING id
),

-- 2) Formulario (1 submit)
ins_form AS (
  INSERT INTO formulario_web (
    contacto_id,
    submitted_at,
    servicio_relacionado,
    como_nos_conociste,
    mensaje
  )
  SELECT
    c.contacto_id,
    now() - interval '4 days',
    'Cloud & DevOps',
    'Google / Buscador',
    'Hola, necesitamos ayuda para estabilizar despliegues y observabilidad (Prometheus/Grafana) en nuestro entorno. Queremos una propuesta.'
  FROM contact c
  WHERE NOT EXISTS (
    SELECT 1 FROM formulario_web f
    WHERE f.contacto_id = c.contacto_id
      AND f.servicio_relacionado = 'Cloud & DevOps'
      AND f.mensaje LIKE 'Hola, necesitamos ayuda%'
  )
  RETURNING id
),

-- 3) Oportunidad (1)
ins_opp AS (
  INSERT INTO oportunidades (
    contacto_id,
    deal_name,
    estado,
    lead_tag,
    prioridad,
    probabilidad,
    currency,
    pack,
    next_action,
    next_action_date,
    expected_close_date,
    created_at,
    updated_at
  )
  SELECT
    c.contacto_id,
    'Diagnóstico + Plan Cloud & DevOps (Barcelona)',
    'En contacto',
    'Warm',
    'Alta',
    55,
    'EUR',
    'MOTOR',
    'BOOK_MEETING',
    (now() + interval '2 days')::date,
    (now() + interval '14 days')::date,
    now() - interval '3 days',
    now() - interval '3 days'
  FROM contact c
  WHERE NOT EXISTS (
    SELECT 1 FROM oportunidades o
    WHERE o.contacto_id = c.contacto_id
      AND o.deal_name = 'Diagnóstico + Plan Cloud & DevOps (Barcelona)'
  )
  RETURNING id AS oportunidad_id
),

-- 4) Historial (2 eventos) - requiere subject,type y relationship check: usamos contacto_id y oportunidad_id
ins_hist_1 AS (
  INSERT INTO historial (
    contacto_id,
    oportunidad_id,
    type,
    subject,
    outcome,
    activity_date,
    created_at
  )
  SELECT
    c.contacto_id,
    o.oportunidad_id,
    'EMAIL',
    'Primer contacto enviado (propuesta de diagnóstico)',
    'Exitoso',
    now() - interval '3 days',
    now() - interval '3 days'
  FROM contact c
  JOIN ins_opp o ON true
  WHERE NOT EXISTS (
    SELECT 1 FROM historial h
    WHERE h.contacto_id = c.contacto_id
      AND h.subject = 'Primer contacto enviado (propuesta de diagnóstico)'
      AND h.type = 'EMAIL'
  )
  RETURNING id
),
ins_hist_2 AS (
  INSERT INTO historial (
    contacto_id,
    oportunidad_id,
    type,
    subject,
    outcome,
    activity_date,
    created_at
  )
  SELECT
    c.contacto_id,
    o.oportunidad_id,
    'CALL',
    'Llamada de descubrimiento (15 min)',
    'Reprogramar',
    now() - interval '2 days',
    now() - interval '2 days'
  FROM contact c
  JOIN ins_opp o ON true
  WHERE NOT EXISTS (
    SELECT 1 FROM historial h
    WHERE h.contacto_id = c.contacto_id
      AND h.subject = 'Llamada de descubrimiento (15 min)'
      AND h.type = 'CALL'
  )
  RETURNING id
),

-- 5) Pendiente (1 task) - requiere title + relationship check (contacto_id u oportunidad_id)
ins_task AS (
  INSERT INTO pendientes (
    contacto_id,
    oportunidad_id,
    title,
    status,
    priority,
    due_date,
    reminder_datetime,
    created_at
  )
  SELECT
    c.contacto_id,
    o.oportunidad_id,
    'Enviar agenda + enlace Cal.com para diagnóstico',
    'TODO',
    'HIGH',
    (now() + interval '1 day')::date,
    now() + interval '18 hours',
    now() - interval '1 day'
  FROM contact c
  JOIN ins_opp o ON true
  WHERE NOT EXISTS (
    SELECT 1 FROM pendientes p
    WHERE p.contacto_id = c.contacto_id
      AND p.title = 'Enviar agenda + enlace Cal.com para diagnóstico'
  )
  RETURNING id
),

-- 6) Presupuesto (1) - NOT NULL: contacto_id, oportunidad_id, quote_number, quote_value, title
ins_quote AS (
  INSERT INTO presupuestos (
    contacto_id,
    oportunidad_id,
    quote_number,
    title,
    quote_value,
    currency,
    status,
    sent_at,
    valid_until,
    created_at
  )
  SELECT
    c.contacto_id,
    o.oportunidad_id,
    'Q-2026-0001',
    'Propuesta: Cloud & DevOps (Pack MOTOR)',
    1200.00,
    'EUR',
    'Sent',
    now() - interval '1 day',
    (now() + interval '14 days')::date,
    now() - interval '1 day'
  FROM contact c
  JOIN ins_opp o ON true
  WHERE NOT EXISTS (
    SELECT 1 FROM presupuestos q
    WHERE q.quote_number = 'Q-2026-0001'
  )
  RETURNING id AS presupuesto_id
),

-- 7) Factura (1) - NOT NULL: contacto_id, oportunidad_id, invoice_number, invoice_value, issue_date, due_date
ins_invoice AS (
  INSERT INTO facturas (
    contacto_id,
    oportunidad_id,
    invoice_number,
    invoice_value,
    currency,
    status,
    payment_method,
    issue_date,
    due_date,
    created_at
  )
  SELECT
    c.contacto_id,
    o.oportunidad_id,
    'F-2026-0001',
    1200.00,
    'EUR',
    'PENDING',
    'Transferencia',
    (now() - interval '12 hours')::date,
    (now() + interval '15 days')::date,
    now() - interval '12 hours'
  FROM contact c
  JOIN ins_opp o ON true
  WHERE NOT EXISTS (
    SELECT 1 FROM facturas f
    WHERE f.invoice_number = 'F-2026-0001'
  )
  RETURNING id
)

SELECT 'ok' AS seed_status;
SQL

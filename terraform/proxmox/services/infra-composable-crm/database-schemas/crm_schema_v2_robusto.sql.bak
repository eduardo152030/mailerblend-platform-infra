-- ═══════════════════════════════════════════════════════════════════════════
-- CRM PROFESIONAL + LINKEDIN STEALTH SOURCING - SCHEMA POSTGRESQL
-- ═══════════════════════════════════════════════════════════════════════════
-- Diseño para: Budibase + Supabase
-- Objetivo: CRM completo + preparado para prospección LinkedIn (sin implementar)
-- Filosofía: Solo tablas duras, extensible, sin modificaciones futuras
-- ═══════════════════════════════════════════════════════════════════════════

-- Habilitar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- Búsquedas fuzzy

-- ═══════════════════════════════════════════════════════════════════════════
-- CORE: CONTACTOS (Base central unificada)
-- ═══════════════════════════════════════════════════════════════════════════
-- PROPÓSITO: Base de datos central de personas y empresas
-- FUENTES: Web form, manual, LinkedIn, importaciones
-- DEDUPLICACIÓN: email O linkedin_url O teléfono
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE contactos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Información personal básica
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    telefono VARCHAR(50),
    cargo VARCHAR(150),
    
    -- Información de empresa
    company_name VARCHAR(255),
    tipo_empresa VARCHAR(50) CHECK (tipo_empresa IN ('Pyme', 'Agencia', 'Emprendedor', 'Startup')),
    company_size VARCHAR(50), -- "1-10", "11-50", "51-200", "201-500", "500+"
    industry VARCHAR(100),
    website VARCHAR(500),
    
    -- LinkedIn (preparado para sourcing)
    linkedin_url VARCHAR(500) UNIQUE, -- CRÍTICO: único para evitar duplicados
    linkedin_profile_data JSONB, -- Guardar snapshot del perfil
    
    -- Localización
    ciudad VARCHAR(100),
    pais VARCHAR(100) DEFAULT 'España',
    direccion TEXT,
    
    -- Google Maps/Places (preparado para sourcing)
    places_place_id VARCHAR(255),
    places_name VARCHAR(255),
    places_rating DECIMAL(2,1),
    places_user_ratings_total INTEGER,
    places_types TEXT[], -- array de categorías
    places_website VARCHAR(500),
    places_phone VARCHAR(50),
    places_address TEXT,
    places_last_checked_at TIMESTAMPTZ,
    places_signal_hash VARCHAR(64), -- MD5 de datos relevantes para detectar cambios
    
    -- Pack asignado (preparado para sourcing)
    pack_asignado VARCHAR(50) CHECK (pack_asignado IN (
        'GUARDIAN',     -- Pack 1: Soporte operativo
        'MOTOR',        -- Pack 2: Socio tecnológico
        'FORTALEZA',    -- Pack 3: CTO & Infraestructura crítica
        'NO_ASIGNADO'
    )) DEFAULT 'NO_ASIGNADO',
    
    -- Lead scoring (preparado para sourcing)
    lead_score INTEGER CHECK (lead_score >= 0 AND lead_score <= 100),
    score_breakdown JSONB, -- Desglose de cómo se calculó el score
    score_calculated_at TIMESTAMPTZ,
    
    -- Origen del contacto
    origen VARCHAR(50) CHECK (origen IN (
        'FORMULARIO_WEB',
        'MANUAL',
        'LINKEDIN_SOURCING',
        'IMPORTACION',
        'REFERIDO',
        'EVENTO'
    )),
    
    -- Compliance
    gdpr_consent BOOLEAN DEFAULT FALSE,
    gdpr_consent_date TIMESTAMPTZ,
    marketing_consent BOOLEAN DEFAULT FALSE,
    
    -- Web signals (preparado para sourcing)
    web_last_scraped_at TIMESTAMPTZ,
    web_signal_hash VARCHAR(64), -- Para detectar cambios en la web
    web_tech_stack TEXT[], -- ["WordPress", "Shopify", etc.]
    
    -- Estado del contacto
    estado VARCHAR(50) DEFAULT 'ACTIVO' CHECK (estado IN (
        'ACTIVO',
        'INACTIVO',
        'DESCALIFICADO',
        'BLOQUEADO'
    )),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100),
    
    -- Notas generales
    notas TEXT
);

-- Índices para búsqueda y deduplicación
CREATE INDEX idx_contactos_email ON contactos(email) WHERE email IS NOT NULL;
CREATE INDEX idx_contactos_telefono ON contactos(telefono) WHERE telefono IS NOT NULL;
CREATE INDEX idx_contactos_linkedin_url ON contactos(linkedin_url) WHERE linkedin_url IS NOT NULL;
CREATE INDEX idx_contactos_company ON contactos(company_name);
CREATE INDEX idx_contactos_pack ON contactos(pack_asignado);
CREATE INDEX idx_contactos_origen ON contactos(origen);
CREATE INDEX idx_contactos_created ON contactos(created_at DESC);
CREATE INDEX idx_contactos_lead_score ON contactos(lead_score DESC) WHERE lead_score IS NOT NULL;

-- Búsqueda fuzzy
CREATE INDEX idx_contactos_nombre_trgm ON contactos USING gin (nombre gin_trgm_ops);
CREATE INDEX idx_contactos_company_trgm ON contactos USING gin (company_name gin_trgm_ops);

COMMENT ON TABLE contactos IS 'Base central unificada de contactos. Soporta origen web + LinkedIn sourcing. Deduplicación por email/linkedin_url/teléfono.';

-- ═══════════════════════════════════════════════════════════════════════════
-- SOURCING: LINKEDIN_LEADS (Específico para prospección)
-- ═══════════════════════════════════════════════════════════════════════════
-- PROPÓSITO: Gestión del proceso de LinkedIn Sourcing
-- ESTADOS: Desde prospect inicial hasta aceptación/descarte
-- RELACIÓN: Se vincula a contactos cuando hay aceptación
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE linkedin_leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contacto_id UUID REFERENCES contactos(id) ON DELETE SET NULL,
    
    -- LinkedIn básico
    linkedin_url VARCHAR(500) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    company VARCHAR(255),
    location VARCHAR(255),
    
    -- Segmentación y pack
    pack_candidate VARCHAR(50) CHECK (pack_candidate IN (
        'GUARDIAN',
        'MOTOR', 
        'FORTALEZA',
        'NONE'
    )),
    segment VARCHAR(100), -- ej: "A_<50reviews", "B_>200reviews", "Pack2_Services_BCN"
    
    -- Scoring
    lead_score INTEGER CHECK (lead_score >= 0 AND lead_score <= 100),
    score_breakdown JSONB,
    
    -- Estado del flujo de sourcing
    status VARCHAR(50) NOT NULL DEFAULT 'NEW' CHECK (status IN (
        'NEW',              -- Identificado como prospect
        'SCORING',          -- En proceso de scoring
        'INVITE_QUEUED',    -- En cola para invitar
        'INVITE_SENT',      -- Invitación enviada
        'PENDING',          -- Esperando aceptación
        'ACCEPTED',         -- Aceptó invitación
        'NO_ACCEPT',        -- No aceptó en ventana
        'RECYCLE_RETRY',    -- Reintento por señal nueva
        'ENGAGE_LATER',     -- Contactar por otro canal
        'ARCHIVED',         -- Descartado/archivado
        'CONVERTED'         -- Convertido a oportunidad
    )),
    
    -- Timing y ventanas
    invite_sent_at TIMESTAMPTZ,
    accepted_at TIMESTAMPTZ,
    wait_window_days INTEGER DEFAULT 14,
    next_action_at TIMESTAMPTZ,
    
    -- Señales web
    web_signal_hash VARCHAR(64),
    web_last_checked_at TIMESTAMPTZ,
    
    -- Señales Places
    places_place_id VARCHAR(255),
    places_rating DECIMAL(2,1),
    places_user_ratings_total INTEGER,
    places_types TEXT[],
    places_website VARCHAR(500),
    places_address TEXT,
    places_last_checked_at TIMESTAMPTZ,
    places_signal_hash VARCHAR(64),
    
    -- Tracking de cambios (para reciclaje inteligente)
    signal_changed BOOLEAN DEFAULT FALSE,
    last_signal_check_at TIMESTAMPTZ,
    
    -- A/B testing
    ab_test_group VARCHAR(50), -- "A", "B", "Control", etc.
    
    -- Research multi-fuente
    research_data JSONB, -- Resultados del research profundo
    research_depth VARCHAR(20) CHECK (research_depth IN ('NONE', 'BASIC', 'MEDIUM', 'DEEP')),
    research_completed_at TIMESTAMPTZ,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Stats
    total_attempts INTEGER DEFAULT 0,
    last_attempt_at TIMESTAMPTZ
);

CREATE INDEX idx_linkedin_leads_contacto ON linkedin_leads(contacto_id);
CREATE INDEX idx_linkedin_leads_status ON linkedin_leads(status);
CREATE INDEX idx_linkedin_leads_pack ON linkedin_leads(pack_candidate);
CREATE INDEX idx_linkedin_leads_segment ON linkedin_leads(segment);
CREATE INDEX idx_linkedin_leads_score ON linkedin_leads(lead_score DESC);
CREATE INDEX idx_linkedin_leads_next_action ON linkedin_leads(next_action_at) WHERE next_action_at IS NOT NULL;
CREATE INDEX idx_linkedin_leads_pending ON linkedin_leads(status, invite_sent_at) WHERE status = 'PENDING';

COMMENT ON TABLE linkedin_leads IS 'Gestión de LinkedIn Sourcing. Estados desde prospect hasta conversión. Vincula a contactos cuando acepta.';

-- ═══════════════════════════════════════════════════════════════════════════
-- SOURCING: LINKEDIN_ATTEMPTS (Historial de intentos)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE linkedin_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    linkedin_lead_id UUID NOT NULL REFERENCES linkedin_leads(id) ON DELETE CASCADE,
    
    attempt_type VARCHAR(50) NOT NULL CHECK (attempt_type IN (
        'INVITE',
        'MESSAGE',
        'RESEARCH',
        'SIGNAL_CHECK',
        'SCORE_UPDATE'
    )),
    
    result VARCHAR(50) CHECK (result IN (
        'SENT',
        'SKIPPED',
        'FAILED',
        'BLOCKED',
        'DUPLICATE',
        'COMPLETED'
    )),
    
    reason TEXT, -- ej: "duplicate", "window_active", "no_signal", "stop_loss"
    metadata JSONB,
    
    attempted_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_linkedin_attempts_lead ON linkedin_attempts(linkedin_lead_id);
CREATE INDEX idx_linkedin_attempts_type ON linkedin_attempts(attempt_type);
CREATE INDEX idx_linkedin_attempts_date ON linkedin_attempts(attempted_at DESC);

COMMENT ON TABLE linkedin_attempts IS 'Historial de todos los intentos de interacción con LinkedIn leads.';

-- ═══════════════════════════════════════════════════════════════════════════
-- SOURCING: LINKEDIN_APPROVALS (Control humano vía Telegram)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE linkedin_approvals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    linkedin_lead_id UUID NOT NULL REFERENCES linkedin_leads(id) ON DELETE CASCADE,
    
    -- Draft generado por IA
    draft_message TEXT NOT NULL,
    ai_rationale TEXT, -- "Por qué" este mensaje
    
    -- Mensaje final (aprobado/editado)
    final_message TEXT,
    
    -- Feedback humano
    approved BOOLEAN,
    angle VARCHAR(50) CHECK (angle IN ('Bueno', 'Regular', 'Incorrecto')),
    pain_assessment VARCHAR(50) CHECK (pain_assessment IN ('Real', 'Superficial', 'Inventado')),
    human_note TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    approved_at TIMESTAMPTZ,
    approved_by VARCHAR(100)
);

CREATE INDEX idx_linkedin_approvals_lead ON linkedin_approvals(linkedin_lead_id);
CREATE INDEX idx_linkedin_approvals_approved ON linkedin_approvals(approved);
CREATE INDEX idx_linkedin_approvals_date ON linkedin_approvals(created_at DESC);

COMMENT ON TABLE linkedin_approvals IS 'Control humano (Telegram). Aprobación/edición de mensajes generados por IA.';

-- ═══════════════════════════════════════════════════════════════════════════
-- CRM: PARAMETROS_UTM (Tracking de campañas web)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE parametros_utm (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contacto_id UUID NOT NULL REFERENCES contactos(id) ON DELETE CASCADE,
    
    -- UTM básicos
    utm_source VARCHAR(255),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(255),
    utm_content VARCHAR(255),
    utm_term VARCHAR(255),
    
    -- UTM extendidos
    adgroup VARCHAR(255),
    device VARCHAR(50),
    placement VARCHAR(255),
    keyword VARCHAR(255),
    creative VARCHAR(255),
    
    -- Click IDs (para conversiones offline)
    gclid VARCHAR(255),
    msclkid VARCHAR(255),
    li_fat_id VARCHAR(255),
    fbclid VARCHAR(255),
    
    -- Metadata
    ads_platform VARCHAR(50) CHECK (ads_platform IN ('GOOGLE', 'BING', 'LINKEDIN', 'FACEBOOK', 'OTRO')),
    landing_url TEXT,
    referrer_url TEXT,
    
    -- Timestamps
    first_visit_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_contact_utm UNIQUE (contacto_id, gclid, msclkid, li_fat_id)
);

CREATE INDEX idx_utm_contacto ON parametros_utm(contacto_id);
CREATE INDEX idx_utm_gclid ON parametros_utm(gclid) WHERE gclid IS NOT NULL;
CREATE INDEX idx_utm_msclkid ON parametros_utm(msclkid) WHERE msclkid IS NOT NULL;
CREATE INDEX idx_utm_li_fat_id ON parametros_utm(li_fat_id) WHERE li_fat_id IS NOT NULL;
CREATE INDEX idx_utm_source ON parametros_utm(utm_source);
CREATE INDEX idx_utm_campaign ON parametros_utm(utm_campaign);

COMMENT ON TABLE parametros_utm IS 'Tracking UTM completo. Atribución de campañas web. Click IDs para conversiones offline.';

-- ═══════════════════════════════════════════════════════════════════════════
-- CRM: FORMULARIO_WEB (Respuestas del formulario)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE formulario_web (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contacto_id UUID NOT NULL REFERENCES contactos(id) ON DELETE CASCADE,
    
    -- Campos base
    servicio_relacionado VARCHAR(100) NOT NULL CHECK (servicio_relacionado IN (
        'No lo tengo claro',
        'Desarrollo web y software a medida',
        'Cloud & DevOps',
        'SRE / Observabilidad',
        'Infraestructura gestionada',
        'Integraciones / Automatización',
        'Outsourcing IT / CAU'
    )),
    
    como_nos_conociste VARCHAR(100) CHECK (como_nos_conociste IN (
        'Google / Buscador',
        'Recomendación',
        'Redes sociales',
        'LinkedIn',
        'Evento / Conferencia',
        'Prensa / Blog',
        'Cliente existente',
        'Otro'
    )),
    
    -- Campos dinámicos
    tipo_solucion VARCHAR(100),
    situacion_infraestructura VARCHAR(100),
    problema_fiabilidad VARCHAR(150),
    parte_infraestructura VARCHAR(100),
    herramientas_conectar TEXT,
    tipo_soporte VARCHAR(150),
    
    -- Mensaje (siempre presente)
    mensaje TEXT NOT NULL,
    
    -- Metadata
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    origen VARCHAR(50) DEFAULT 'Formulario web',
    ip_address INET,
    user_agent TEXT
);

CREATE INDEX idx_formulario_contacto ON formulario_web(contacto_id);
CREATE INDEX idx_formulario_servicio ON formulario_web(servicio_relacionado);
CREATE INDEX idx_formulario_submitted ON formulario_web(submitted_at DESC);

COMMENT ON TABLE formulario_web IS 'Respuestas del formulario web con campos dinámicos según servicio.';

-- ═══════════════════════════════════════════════════════════════════════════
-- CRM: OPORTUNIDADES (Pipeline de ventas)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE oportunidades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contacto_id UUID NOT NULL REFERENCES contactos(id) ON DELETE RESTRICT,
    formulario_id UUID REFERENCES formulario_web(id) ON DELETE SET NULL,
    linkedin_lead_id UUID REFERENCES linkedin_leads(id) ON DELETE SET NULL, -- Vinculación con sourcing
    
    -- Identificación
    deal_name VARCHAR(255) NOT NULL,
    
    -- Pack (sincronizado con contacto)
    pack VARCHAR(50) CHECK (pack IN ('GUARDIAN', 'MOTOR', 'FORTALEZA', 'NO_ASIGNADO')),
    
    -- Estado del pipeline
    estado VARCHAR(50) NOT NULL DEFAULT 'Nuevo' CHECK (estado IN (
        'Nuevo',
        'En contacto',
        'Presupuesto enviado',
        'Negociación',
        'Ganado',
        'Perdido'
    )),
    
    -- Calificación
    prioridad VARCHAR(20) DEFAULT 'Media' CHECK (prioridad IN ('Alta', 'Media', 'Baja')),
    lead_tag VARCHAR(50) CHECK (lead_tag IN ('Hot', 'Warm', 'Cold', 'Qualified', 'Unqualified')),
    
    -- Valor comercial
    deal_value DECIMAL(12, 2),
    currency VARCHAR(3) DEFAULT 'EUR' CHECK (currency IN ('EUR', 'USD')),
    probabilidad INTEGER CHECK (probabilidad >= 0 AND probabilidad <= 100),
    
    -- Acciones
    next_action VARCHAR(50) DEFAULT 'NO_ACTION' CHECK (next_action IN (
        'SEND_EMAIL',
        'CALL',
        'BOOK_MEETING',
        'SEND_PROPOSAL',
        'FOLLOW_UP',
        'NO_ACTION'
    )),
    next_action_date DATE,
    
    -- Responsable
    owner VARCHAR(100),
    team VARCHAR(100),
    
    -- Fechas
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expected_close_date DATE,
    won_at TIMESTAMPTZ,
    lost_at TIMESTAMPTZ,
    
    -- Razón de pérdida
    lost_reason VARCHAR(50) CHECK (lost_reason IN (
        'Precio alto',
        'No responde',
        'Eligió competidor',
        'No tiene presupuesto',
        'Timing incorrecto',
        'No es fit',
        'Otro'
    )),
    lost_reason_notes TEXT,
    
    -- Notas
    notas_internas TEXT,
    
    -- Tags
    tags TEXT[]
);

CREATE INDEX idx_oportunidades_contacto ON oportunidades(contacto_id);
CREATE INDEX idx_oportunidades_linkedin ON oportunidades(linkedin_lead_id);
CREATE INDEX idx_oportunidades_estado ON oportunidades(estado);
CREATE INDEX idx_oportunidades_pack ON oportunidades(pack);
CREATE INDEX idx_oportunidades_owner ON oportunidades(owner);
CREATE INDEX idx_oportunidades_created ON oportunidades(created_at DESC);
CREATE INDEX idx_oportunidades_expected_close ON oportunidades(expected_close_date);
CREATE INDEX idx_oportunidades_tags ON oportunidades USING gin(tags);

COMMENT ON TABLE oportunidades IS 'Pipeline de ventas. Puede originarse de formulario web O LinkedIn sourcing.';

-- ═══════════════════════════════════════════════════════════════════════════
-- CRM: HISTORIAL (Timeline de actividades)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE historial (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contacto_id UUID REFERENCES contactos(id) ON DELETE CASCADE,
    oportunidad_id UUID REFERENCES oportunidades(id) ON DELETE CASCADE,
    linkedin_lead_id UUID REFERENCES linkedin_leads(id) ON DELETE CASCADE, -- También sourcing
    
    -- Tipo de actividad
    type VARCHAR(50) NOT NULL CHECK (type IN (
        'CALL',
        'EMAIL',
        'MEETING',
        'NOTE',
        'WHATSAPP',
        'SMS',
        'LINKEDIN_MESSAGE',
        'LINKEDIN_INVITE',
        'LINKEDIN_CONVERSATION'
    )),
    
    -- Contenido
    subject VARCHAR(255) NOT NULL,
    notes TEXT,
    outcome VARCHAR(50) CHECK (outcome IN (
        'Exitoso',
        'No contesta',
        'Buzón de voz',
        'Reprogramar',
        'Otro'
    )),
    
    -- Metadata
    activity_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    duration_minutes INTEGER,
    created_by VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Archivos adjuntos
    attachments TEXT[],
    
    CONSTRAINT check_relationship CHECK (
        contacto_id IS NOT NULL OR 
        oportunidad_id IS NOT NULL OR 
        linkedin_lead_id IS NOT NULL
    )
);

CREATE INDEX idx_historial_contacto ON historial(contacto_id);
CREATE INDEX idx_historial_oportunidad ON historial(oportunidad_id);
CREATE INDEX idx_historial_linkedin ON historial(linkedin_lead_id);
CREATE INDEX idx_historial_type ON historial(type);
CREATE INDEX idx_historial_date ON historial(activity_date DESC);

COMMENT ON TABLE historial IS 'Timeline de actividades. Soporta CRM tradicional + LinkedIn sourcing.';

-- ═══════════════════════════════════════════════════════════════════════════
-- CRM: PENDIENTES (Tareas)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE pendientes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contacto_id UUID REFERENCES contactos(id) ON DELETE CASCADE,
    oportunidad_id UUID REFERENCES oportunidades(id) ON DELETE CASCADE,
    linkedin_lead_id UUID REFERENCES linkedin_leads(id) ON DELETE CASCADE,
    
    -- Tarea
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Estado
    status VARCHAR(50) DEFAULT 'TODO' CHECK (status IN (
        'TODO',
        'IN_PROGRESS',
        'DONE',
        'CANCELLED'
    )),
    
    priority VARCHAR(20) DEFAULT 'MEDIUM' CHECK (priority IN ('HIGH', 'MEDIUM', 'LOW')),
    
    -- Asignación
    assigned_to VARCHAR(100),
    
    -- Fechas
    due_date DATE,
    due_time TIME,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100),
    
    -- Recordatorios
    reminder_enabled BOOLEAN DEFAULT FALSE,
    reminder_datetime TIMESTAMPTZ,
    
    CONSTRAINT check_task_relationship CHECK (
        contacto_id IS NOT NULL OR 
        oportunidad_id IS NOT NULL OR 
        linkedin_lead_id IS NOT NULL
    )
);

CREATE INDEX idx_pendientes_contacto ON pendientes(contacto_id);
CREATE INDEX idx_pendientes_oportunidad ON pendientes(oportunidad_id);
CREATE INDEX idx_pendientes_linkedin ON pendientes(linkedin_lead_id);
CREATE INDEX idx_pendientes_status ON pendientes(status);
CREATE INDEX idx_pendientes_assigned ON pendientes(assigned_to);
CREATE INDEX idx_pendientes_due_date ON pendientes(due_date);
CREATE INDEX idx_pendientes_open_due_date ON pendientes(due_date) WHERE status != 'DONE' AND due_date IS NOT NULL;

COMMENT ON TABLE pendientes IS 'Tareas pendientes. Soporta flujos CRM + LinkedIn sourcing.';

-- ═══════════════════════════════════════════════════════════════════════════
-- CRM: PRESUPUESTOS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE presupuestos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contacto_id UUID NOT NULL REFERENCES contactos(id) ON DELETE RESTRICT,
    oportunidad_id UUID NOT NULL REFERENCES oportunidades(id) ON DELETE RESTRICT,
    
    -- Identificación
    quote_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    version INTEGER DEFAULT 1,
    
    -- Valor
    quote_value DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR' CHECK (currency IN ('EUR', 'USD')),
    
    -- Ítems (flexible)
    line_items JSONB,
    
    -- Estado
    status VARCHAR(50) DEFAULT 'Draft' CHECK (status IN (
        'Draft',
        'Sent',
        'Accepted',
        'Rejected',
        'Expired'
    )),
    
    -- Fechas
    created_at TIMESTAMPTZ DEFAULT NOW(),
    sent_at TIMESTAMPTZ,
    valid_until DATE,
    accepted_at TIMESTAMPTZ,
    rejected_at TIMESTAMPTZ,
    
    -- PDF
    pdf_url TEXT,
    
    -- Notas
    notes TEXT,
    internal_notes TEXT
);

CREATE INDEX idx_presupuestos_contacto ON presupuestos(contacto_id);
CREATE INDEX idx_presupuestos_oportunidad ON presupuestos(oportunidad_id);
CREATE INDEX idx_presupuestos_status ON presupuestos(status);
CREATE INDEX idx_presupuestos_sent ON presupuestos(sent_at DESC);

COMMENT ON TABLE presupuestos IS 'Presupuestos comerciales. Múltiples versiones por oportunidad.';

-- ═══════════════════════════════════════════════════════════════════════════
-- CRM: FACTURAS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE facturas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contacto_id UUID NOT NULL REFERENCES contactos(id) ON DELETE RESTRICT,
    oportunidad_id UUID NOT NULL REFERENCES oportunidades(id) ON DELETE RESTRICT,
    presupuesto_id UUID REFERENCES presupuestos(id) ON DELETE SET NULL,
    
    -- Identificación
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Valor
    invoice_value DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR' CHECK (currency IN ('EUR', 'USD')),
    
    -- Estado
    status VARCHAR(50) DEFAULT 'PENDING' CHECK (status IN (
        'PENDING',
        'PAID',
        'OVERDUE',
        'CANCELLED',
        'PARTIALLY_PAID'
    )),
    
    -- Fechas
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    paid_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Pago
    payment_method VARCHAR(50) CHECK (payment_method IN (
        'Transferencia',
        'Tarjeta',
        'PayPal',
        'Stripe',
        'Efectivo',
        'Otro'
    )),
    payment_reference VARCHAR(100),
    
    -- PDF
    pdf_url TEXT,
    
    -- Notas
    notes TEXT
);

CREATE INDEX idx_facturas_contacto ON facturas(contacto_id);
CREATE INDEX idx_facturas_oportunidad ON facturas(oportunidad_id);
CREATE INDEX idx_facturas_status ON facturas(status);
CREATE INDEX idx_facturas_due_date ON facturas(due_date);
CREATE INDEX idx_facturas_pending_due_date ON facturas(due_date) WHERE status = 'PENDING' AND due_date IS NOT NULL;

COMMENT ON TABLE facturas IS 'Facturas emitidas. Gestión de cobros.';

-- ═══════════════════════════════════════════════════════════════════════════
-- CRM: CONVERSIONES_OFFLINE (Feedback a Ads)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE conversiones_offline (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    oportunidad_id UUID NOT NULL REFERENCES oportunidades(id) ON DELETE CASCADE,
    parametros_utm_id UUID REFERENCES parametros_utm(id) ON DELETE SET NULL,
    
    -- Plataforma
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('GOOGLE', 'BING', 'LINKEDIN', 'FACEBOOK')),
    
    -- Evento
    event_name VARCHAR(50) NOT NULL CHECK (event_name IN (
        'Lead_Submitted',
        'Lead_Qualified',
        'Lead_Won',
        'Purchase',
        'Custom'
    )),
    
    -- Valor
    conversion_value DECIMAL(12, 2),
    currency VARCHAR(3) DEFAULT 'EUR',
    
    -- Click ID (CRÍTICO)
    click_id VARCHAR(255) NOT NULL,
    
    -- Timestamp
    conversion_time TIMESTAMPTZ NOT NULL,
    
    -- Estado de sync
    sync_status VARCHAR(50) DEFAULT 'PENDING' CHECK (sync_status IN (
        'PENDING',
        'SENT',
        'FAILED',
        'SKIPPED'
    )),
    sent_at TIMESTAMPTZ,
    
    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_conversiones_oportunidad ON conversiones_offline(oportunidad_id);
CREATE INDEX idx_conversiones_utm ON conversiones_offline(parametros_utm_id);
CREATE INDEX idx_conversiones_platform ON conversiones_offline(platform);
CREATE INDEX idx_conversiones_status ON conversiones_offline(sync_status);
CREATE INDEX idx_conversiones_pending ON conversiones_offline(sync_status, created_at) WHERE sync_status = 'PENDING';

COMMENT ON TABLE conversiones_offline IS 'Conversiones offline para Google/Bing/LinkedIn Ads.';

-- ═══════════════════════════════════════════════════════════════════════════
-- SOURCING: LINKEDIN_CONVERSATIONS (Mensajes LinkedIn)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE linkedin_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    linkedin_lead_id UUID NOT NULL REFERENCES linkedin_leads(id) ON DELETE CASCADE,
    
    -- Mensaje
    message_text TEXT NOT NULL,
    direction VARCHAR(10) CHECK (direction IN ('SENT', 'RECEIVED')),
    
    -- Metadata
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    sent_by VARCHAR(100), -- "SYSTEM", "USER", o nombre del usuario
    
    -- Análisis (opcional, para futuro)
    sentiment VARCHAR(20), -- "POSITIVE", "NEUTRAL", "NEGATIVE"
    intent VARCHAR(50), -- "INTERESTED", "NOT_INTERESTED", "QUESTION", etc.
    
    -- Tracking
    read_at TIMESTAMPTZ,
    replied_at TIMESTAMPTZ
);

CREATE INDEX idx_linkedin_conversations_lead ON linkedin_conversations(linkedin_lead_id);
CREATE INDEX idx_linkedin_conversations_direction ON linkedin_conversations(direction);
CREATE INDEX idx_linkedin_conversations_sent ON linkedin_conversations(sent_at DESC);

COMMENT ON TABLE linkedin_conversations IS 'Historial completo de conversaciones LinkedIn. Mensajes enviados y recibidos.';

-- ═══════════════════════════════════════════════════════════════════════════
-- SOURCING: LINKEDIN_OUTCOMES (Resultados finales)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE linkedin_outcomes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    linkedin_lead_id UUID NOT NULL REFERENCES linkedin_leads(id) ON DELETE CASCADE,
    oportunidad_id UUID REFERENCES oportunidades(id) ON DELETE SET NULL,
    
    -- Outcome final
    outcome VARCHAR(50) NOT NULL CHECK (outcome IN (
        'BOOKED',           -- Agendó sesión Cal.com
        'INTERESTED_LATER', -- Interesado pero no ahora
        'NOT_FIT',          -- No es fit
        'GHOSTED',          -- No respondió más
        'CONVERTED'         -- Se convirtió en oportunidad
    )),
    
    -- Cal.com (si aplicable)
    calendar_event_id VARCHAR(255),
    calendar_event_url TEXT,
    scheduled_at TIMESTAMPTZ,
    
    -- Notas del outcome
    outcome_notes TEXT,
    
    -- Timestamps
    outcome_at TIMESTAMPTZ DEFAULT NOW(),
    recorded_by VARCHAR(100)
);

CREATE INDEX idx_linkedin_outcomes_lead ON linkedin_outcomes(linkedin_lead_id);
CREATE INDEX idx_linkedin_outcomes_outcome ON linkedin_outcomes(outcome);
CREATE INDEX idx_linkedin_outcomes_date ON linkedin_outcomes(outcome_at DESC);

COMMENT ON TABLE linkedin_outcomes IS 'Resultados finales del proceso de LinkedIn sourcing. Tracking de conversiones.';

-- ═══════════════════════════════════════════════════════════════════════════
-- TRIGGERS: Updated_at automático
-- ═══════════════════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_contactos_updated_at
    BEFORE UPDATE ON contactos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_oportunidades_updated_at
    BEFORE UPDATE ON oportunidades
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_linkedin_leads_updated_at
    BEFORE UPDATE ON linkedin_leads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ═══════════════════════════════════════════════════════════════════════════
-- FIN DEL SCHEMA
-- ═══════════════════════════════════════════════════════════════════════════

COMMENT ON SCHEMA public IS 'CRM completo + LinkedIn Stealth Sourcing. Diseñado para Budibase + Supabase. Solo tablas duras, sin vistas.';

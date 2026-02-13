# CRM + LinkedIn Stealth Sourcing - Diagrama ERD

## 📊 Diagrama Entidad-Relación Completo

```mermaid
erDiagram
    %% ═══════════════════════════════════════════════════════════
    %% CORE: CONTACTOS (Centro del sistema)
    %% ═══════════════════════════════════════════════════════════
    
    CONTACTOS ||--o{ PARAMETROS_UTM : "tracking web"
    CONTACTOS ||--o{ FORMULARIO_WEB : "envía"
    CONTACTOS ||--o{ OPORTUNIDADES : "genera"
    CONTACTOS ||--o{ HISTORIAL : "timeline"
    CONTACTOS ||--o{ PENDIENTES : "tareas"
    CONTACTOS ||--o{ PRESUPUESTOS : "recibe"
    CONTACTOS ||--o{ FACTURAS : "recibe"
    CONTACTOS ||--o| LINKEDIN_LEADS : "vincula"
    
    %% ═══════════════════════════════════════════════════════════
    %% CRM FLOW
    %% ═══════════════════════════════════════════════════════════
    
    FORMULARIO_WEB ||--o| OPORTUNIDADES : "crea"
    
    OPORTUNIDADES ||--o{ HISTORIAL : "registra"
    OPORTUNIDADES ||--o{ PENDIENTES : "genera"
    OPORTUNIDADES ||--o{ PRESUPUESTOS : "tiene"
    OPORTUNIDADES ||--o{ FACTURAS : "genera"
    OPORTUNIDADES ||--o{ CONVERSIONES_OFFLINE : "envía"
    
    PRESUPUESTOS ||--o| FACTURAS : "se convierte"
    
    PARAMETROS_UTM ||--o{ CONVERSIONES_OFFLINE : "usa click_id"
    
    %% ═══════════════════════════════════════════════════════════
    %% LINKEDIN SOURCING FLOW
    %% ═══════════════════════════════════════════════════════════
    
    LINKEDIN_LEADS ||--o| OPORTUNIDADES : "convierte"
    LINKEDIN_LEADS ||--o{ LINKEDIN_ATTEMPTS : "registra"
    LINKEDIN_LEADS ||--o{ LINKEDIN_APPROVALS : "aprobación humana"
    LINKEDIN_LEADS ||--o{ LINKEDIN_CONVERSATIONS : "mensajes"
    LINKEDIN_LEADS ||--o| LINKEDIN_OUTCOMES : "resultado final"
    LINKEDIN_LEADS ||--o{ HISTORIAL : "actividades"
    LINKEDIN_LEADS ||--o{ PENDIENTES : "seguimientos"
    
    LINKEDIN_OUTCOMES ||--o| OPORTUNIDADES : "crea si convierte"
    
    %% ═══════════════════════════════════════════════════════════
    %% DEFINICIONES DE TABLAS
    %% ═══════════════════════════════════════════════════════════
    
    CONTACTOS {
        uuid id PK
        string nombre
        string email UK
        string telefono UK
        string linkedin_url UK
        string company_name
        enum tipo_empresa
        string cargo
        string website
        string pack_asignado
        int lead_score
        jsonb score_breakdown
        enum origen
        string places_place_id
        decimal places_rating
        int places_user_ratings_total
        bool gdpr_consent
        timestamp created_at
        timestamp updated_at
    }
    
    LINKEDIN_LEADS {
        uuid id PK
        uuid contacto_id FK
        string linkedin_url UK
        string full_name
        string title
        string company
        string location
        enum pack_candidate
        string segment
        int lead_score
        jsonb score_breakdown
        enum status
        timestamp invite_sent_at
        timestamp accepted_at
        int wait_window_days
        timestamp next_action_at
        string web_signal_hash
        string places_place_id
        decimal places_rating
        int places_user_ratings_total
        bool signal_changed
        string ab_test_group
        jsonb research_data
        enum research_depth
        timestamp created_at
    }
    
    LINKEDIN_ATTEMPTS {
        uuid id PK
        uuid linkedin_lead_id FK
        enum attempt_type
        enum result
        text reason
        jsonb metadata
        timestamp attempted_at
    }
    
    LINKEDIN_APPROVALS {
        uuid id PK
        uuid linkedin_lead_id FK
        text draft_message
        text ai_rationale
        text final_message
        bool approved
        enum angle
        enum pain_assessment
        text human_note
        timestamp approved_at
    }
    
    LINKEDIN_CONVERSATIONS {
        uuid id PK
        uuid linkedin_lead_id FK
        text message_text
        enum direction
        timestamp sent_at
        string sent_by
        string sentiment
        string intent
        timestamp read_at
    }
    
    LINKEDIN_OUTCOMES {
        uuid id PK
        uuid linkedin_lead_id FK
        uuid oportunidad_id FK
        enum outcome
        string calendar_event_id
        text calendar_event_url
        timestamp scheduled_at
        text outcome_notes
        timestamp outcome_at
    }
    
    PARAMETROS_UTM {
        uuid id PK
        uuid contacto_id FK
        string utm_source
        string utm_medium
        string utm_campaign
        string utm_content
        string utm_term
        string adgroup
        string device
        string placement
        string gclid
        string msclkid
        string li_fat_id
        enum ads_platform
        text landing_url
        timestamp first_visit_at
    }
    
    FORMULARIO_WEB {
        uuid id PK
        uuid contacto_id FK
        enum servicio_relacionado
        enum como_nos_conociste
        string tipo_solucion
        string situacion_infraestructura
        string problema_fiabilidad
        text mensaje
        timestamp submitted_at
    }
    
    OPORTUNIDADES {
        uuid id PK
        uuid contacto_id FK
        uuid formulario_id FK
        uuid linkedin_lead_id FK
        string deal_name
        enum pack
        enum estado
        enum prioridad
        enum lead_tag
        decimal deal_value
        string currency
        int probabilidad
        enum next_action
        string owner
        date expected_close_date
        timestamp won_at
        timestamp lost_at
        text notas_internas
    }
    
    HISTORIAL {
        uuid id PK
        uuid contacto_id FK
        uuid oportunidad_id FK
        uuid linkedin_lead_id FK
        enum type
        string subject
        text notes
        timestamp activity_date
        int duration_minutes
        string created_by
    }
    
    PENDIENTES {
        uuid id PK
        uuid contacto_id FK
        uuid oportunidad_id FK
        uuid linkedin_lead_id FK
        string title
        text description
        enum status
        enum priority
        string assigned_to
        date due_date
        timestamp completed_at
    }
    
    PRESUPUESTOS {
        uuid id PK
        uuid contacto_id FK
        uuid oportunidad_id FK
        string quote_number UK
        string title
        decimal quote_value
        jsonb line_items
        enum status
        timestamp sent_at
        date valid_until
    }
    
    FACTURAS {
        uuid id PK
        uuid contacto_id FK
        uuid oportunidad_id FK
        uuid presupuesto_id FK
        string invoice_number UK
        decimal invoice_value
        enum status
        date issue_date
        date due_date
        date paid_date
    }
    
    CONVERSIONES_OFFLINE {
        uuid id PK
        uuid oportunidad_id FK
        uuid parametros_utm_id FK
        enum platform
        enum event_name
        decimal conversion_value
        string click_id
        timestamp conversion_time
        enum sync_status
        text error_message
    }
```

## 🔄 Flujo Dual: CRM Tradicional + LinkedIn Sourcing

```mermaid
graph TB
    subgraph "🌐 CAPTACIÓN WEB (CRM tradicional)"
        WEB[Usuario Web] --> FORM[📝 Formulario Web]
        WEB --> UTM[🔗 UTM Tracking]
        FORM --> CONT1[👤 Contacto]
        UTM --> CONT1
    end
    
    subgraph "🔍 LINKEDIN SOURCING (Prospección activa)"
        PROSPECT[👤 Prospect LinkedIn] --> SCORE[🎯 Scoring por Pack]
        SCORE --> INVITE[📨 Invitación]
        INVITE --> ACCEPT{Acepta?}
        ACCEPT -->|Sí| RESEARCH[🔬 Research]
        ACCEPT -->|No| WAIT[⏳ Ventana espera]
        WAIT --> SIGNAL{Señal nueva?}
        SIGNAL -->|Sí| INVITE
        SIGNAL -->|No| ARCHIVE[📦 Archivo]
        RESEARCH --> DRAFT[✍️ Draft IA]
        DRAFT --> APPROVAL[✅ Aprobación humana]
        APPROVAL --> CONVO[💬 Conversación]
        CONVO --> OUTCOME[🎯 Outcome]
        OUTCOME --> CONT2[👤 Contacto]
    end
    
    subgraph "💼 PIPELINE UNIFICADO"
        CONT1 --> OPP[💼 Oportunidad]
        CONT2 --> OPP
        OPP --> QUOTE[📄 Presupuesto]
        QUOTE --> INV[🧾 Factura]
    end
    
    subgraph "📊 SEGUIMIENTO"
        OPP --> HIST[🧾 Historial]
        OPP --> TASK[✅ Tareas]
        CONT1 --> HIST
        CONT2 --> HIST
    end
    
    subgraph "🎯 OPTIMIZACIÓN"
        UTM --> CONV[🎯 Conversiones Offline]
        OPP --> CONV
    end
    
    style CONT1 fill:#e1f5ff
    style CONT2 fill:#e1f5ff
    style OPP fill:#fff4e1
    style INV fill:#e8f5e9
    style CONV fill:#f3e5f5
    style APPROVAL fill:#ffeb3b
```

## 📈 Flujo LinkedIn Sourcing (Detallado)

```mermaid
sequenceDiagram
    participant LI as 🔍 LinkedIn
    participant SYS as 🤖 Sistema
    participant AI as 🧠 IA (Claude)
    participant TG as 💬 Telegram
    participant HUMAN as 👤 Humano
    participant DB as 💾 Database
    
    LI->>SYS: Prospect identificado
    SYS->>SYS: Clasificar Pack (GUARDIAN/MOTOR/FORTALEZA)
    
    alt Pack = NONE
        SYS->>DB: ARCHIVED
    else Pack válido
        SYS->>SYS: Calcular Lead Score
        
        alt Score bajo
            SYS->>DB: ENGAGE_LATER
        else Score alto
            SYS->>LI: Enviar invitación
            SYS->>DB: Status = INVITE_SENT
            
            alt Acepta en 7-14 días
                LI->>SYS: Aceptación
                SYS->>DB: Status = ACCEPTED
                
                Note over SYS: ACTIVAR SISTEMA COMPLETO
                
                SYS->>SYS: Research Web + Places
                SYS->>AI: Generar draft + rationale
                AI->>SYS: Draft message + explicación
                SYS->>TG: Solicitar aprobación
                TG->>HUMAN: Mostrar draft + contexto
                
                alt Humano aprueba
                    HUMAN->>TG: ✅ Aprobar
                    TG->>SYS: Mensaje aprobado
                    SYS->>LI: Enviar mensaje
                    SYS->>DB: Guardar conversación
                    
                    LI->>SYS: Respuesta prospect
                    SYS->>AI: Analizar respuesta
                    AI->>SYS: Siguiente mensaje
                    SYS->>TG: Revisión humana
                    
                    alt Interesado
                        SYS->>LI: CTA Cal.com
                        LI->>SYS: Reserva sesión
                        SYS->>DB: Outcome = BOOKED
                        SYS->>DB: Crear OPORTUNIDAD
                    else No interesado
                        SYS->>DB: Outcome = NOT_FIT
                    end
                    
                else Humano edita
                    HUMAN->>TG: ✏️ Editar mensaje
                    TG->>SYS: Mensaje editado
                    SYS->>LI: Enviar editado
                    
                else Humano descarta
                    HUMAN->>TG: ❌ Descartar
                    TG->>SYS: Descartado
                    SYS->>DB: Status = ARCHIVED
                end
                
            else NO acepta en ventana
                SYS->>DB: Status = NO_ACCEPT
                SYS->>SYS: Verificar señales (web, Places)
                
                alt Señal cambió
                    SYS->>DB: Status = RECYCLE_RETRY
                    SYS->>LI: Reintentar invitación
                else Sin cambios
                    SYS->>DB: Status = ENGAGE_LATER
                end
            end
        end
    end
```

## 🎯 Estados del LinkedIn Lead

```mermaid
stateDiagram-v2
    [*] --> NEW: Prospect identificado
    
    NEW --> SCORING: Clasificar Pack
    
    SCORING --> ARCHIVED: Pack = NONE
    SCORING --> ENGAGE_LATER: Score bajo
    SCORING --> INVITE_QUEUED: Score alto
    
    INVITE_QUEUED --> INVITE_SENT: Invitación enviada
    
    INVITE_SENT --> PENDING: Esperando respuesta
    
    PENDING --> ACCEPTED: Aceptó en ventana
    PENDING --> NO_ACCEPT: Expiró ventana
    
    NO_ACCEPT --> SIGNAL_CHECK: Verificar señales
    SIGNAL_CHECK --> RECYCLE_RETRY: Señal nueva
    SIGNAL_CHECK --> ENGAGE_LATER: Sin cambios
    SIGNAL_CHECK --> ARCHIVED: No fit
    
    RECYCLE_RETRY --> INVITE_SENT: Reintentar
    
    ACCEPTED --> RESEARCH: Research profundo
    RESEARCH --> DRAFT: IA genera mensaje
    DRAFT --> APPROVAL: Telegram aprobación
    
    APPROVAL --> CONVERSATION: Aprobado
    APPROVAL --> ARCHIVED: Descartado
    
    CONVERSATION --> OUTCOME: Resultado final
    
    OUTCOME --> CONVERTED: Booked/Interested
    OUTCOME --> ARCHIVED: Not fit/Ghosted
    
    CONVERTED --> [*]: → OPORTUNIDAD
    ARCHIVED --> [*]
    ENGAGE_LATER --> [*]
```

## 🔑 Tablas Core (Imprescindibles para Budibase)

### 1. **CONTACTOS** 👤
- **Centro del sistema**
- Unifica leads web + LinkedIn
- Deduplicación: email OR linkedin_url OR teléfono
- Soporta: pack_asignado, lead_score, Places data

### 2. **OPORTUNIDADES** 💼
- **Pipeline unificado**
- Origen dual: formulario_id OR linkedin_lead_id
- Estados: Nuevo → Ganado/Perdido
- Pack sincronizado con contacto

### 3. **HISTORIAL** 🧾
- **Timeline universal**
- Soporta: contacto_id, oportunidad_id, linkedin_lead_id
- Tipos incluyen: LINKEDIN_MESSAGE, LINKEDIN_INVITE

### 4. **PENDIENTES** ✅
- **Tareas universales**
- Soporta: contacto_id, oportunidad_id, linkedin_lead_id
- Critical para seguimientos LinkedIn

## 🎨 Tablas LinkedIn Sourcing (Preparadas para futuro)

### 5. **LINKEDIN_LEADS** 🔍
- **Gestión completa del proceso**
- Estados: NEW → ACCEPTED → CONVERTED
- Scoring por pack, A/B testing, señales web/Places
- Ventana de espera, reciclaje inteligente

### 6. **LINKEDIN_ATTEMPTS** 📝
- **Auditoría completa**
- Todos los intentos: invite, message, research, signal_check
- Resultados: sent, skipped, failed, blocked

### 7. **LINKEDIN_APPROVALS** ✅
- **Control humano (Telegram)**
- Draft IA + rationale
- Feedback estructurado: angle, pain, note

### 8. **LINKEDIN_CONVERSATIONS** 💬
- **Historial de mensajes**
- Dirección: SENT / RECEIVED
- Análisis futuro: sentiment, intent

### 9. **LINKEDIN_OUTCOMES** 🎯
- **Resultados finales**
- BOOKED / INTERESTED_LATER / NOT_FIT / GHOSTED
- Tracking de Cal.com events

## 📋 Pantallas Budibase Recomendadas

### 🏠 Dashboard Principal
**Objetivo:** Vista 360° del negocio

**Widgets:**
- 📊 Pipeline por estado (gráfico embudo)
- 💰 Revenue mes actual vs anterior
- ✅ Mis tareas de hoy (vencidas en rojo)
- 📈 Funnel: Leads → Oportunidades → Ganados
- 🎯 (Futuro) LinkedIn: Invites sent → Acceptance rate → Booked

### 👥 Contactos
**Objetivo:** Base de datos central

**Features:**
- 🔍 Búsqueda fuzzy (nombre, empresa, email)
- 🏷️ Filtros: tipo_empresa, pack_asignado, origen
- 📊 Vista detalle:
  - Datos básicos + LinkedIn + Places
  - Timeline unificado (historial + formularios)
  - Oportunidades relacionadas
  - UTM tracking (si origen web)
  - (Futuro) LinkedIn lead status

### 💼 Pipeline (Kanban)
**Objetivo:** Gestión visual de oportunidades

**Columnas:**
- Nuevo
- En contacto
- Presupuesto enviado
- Negociación
- Ganado
- Perdido

**Features:**
- Drag & drop para cambiar estado
- Filtros: owner, pack, valor
- Color por prioridad
- Detalle: contacto, valor, next_action, fechas

### 📅 Calendario
**Objetivo:** Tareas y reuniones

**Features:**
- Vista mensual/semanal
- Código de colores por prioridad
- Alertas de vencimientos
- Filtro por assigned_to
- (Futuro) Cal.com events integrados

### 📄 Presupuestos
**Objetivo:** Generación y tracking

**Features:**
- Generador con plantilla
- Estado visual: Draft/Sent/Accepted/Rejected
- Versiones múltiples por oportunidad
- Alerta de expiración
- Generación PDF (Supabase Storage)

### 🧾 Facturas
**Objetivo:** Control de cobros

**Features:**
- Dashboard: Pending/Paid/Overdue
- Alertas de vencimiento (push notifications)
- Filtros: estado, cliente, fecha
- Gráfico: Revenue mensual
- DSO (Days Sales Outstanding)

### 📊 Analytics
**Objetivo:** Inteligencia de negocio

**Dashboards:**
- **Funnel:**
  - Formularios → Oportunidades → Ganados
  - Tasas de conversión por servicio
  - (Futuro) LinkedIn: Invites → Accepts → Booked

- **Atribución:**
  - Revenue por campaña (UTM)
  - ROI por fuente (Google/Bing/LinkedIn)
  - Cost per lead vs LTV

- **Performance:**
  - Win rate por owner
  - Tiempo promedio de cierre
  - Ticket promedio por pack

## 🔐 Row Level Security (RLS) - Supabase

```sql
-- Solo el owner puede ver sus oportunidades
CREATE POLICY "Users can view own opportunities"
ON oportunidades FOR SELECT
USING (owner = auth.jwt() ->> 'email');

-- Solo el assigned_to puede ver sus tareas
CREATE POLICY "Users can view own tasks"
ON pendientes FOR SELECT
USING (assigned_to = auth.jwt() ->> 'email');

-- Admin puede ver todo
CREATE POLICY "Admins can view all"
ON oportunidades FOR SELECT
USING (
    (SELECT role FROM users WHERE email = auth.jwt() ->> 'email') = 'ADMIN'
);
```

## ✅ Checklist de Implementación

### Fase 1: CRM Base (Ahora)
- [ ] Ejecutar schema SQL en Supabase
- [ ] Conectar Budibase a Supabase
- [ ] Crear pantalla Dashboard
- [ ] Crear pantalla Contactos (lista + detalle)
- [ ] Crear pantalla Pipeline (Kanban)
- [ ] Crear pantalla Calendario
- [ ] Crear pantalla Presupuestos
- [ ] Crear pantalla Facturas
- [ ] Configurar RLS básico
- [ ] Importar datos de prueba (formulario web)

### Fase 2: Analytics (Próximo)
- [ ] Dashboard de Analytics
- [ ] Tracking de conversiones offline
- [ ] Reportes automáticos

### Fase 3: LinkedIn Sourcing (Futuro)
- [ ] Integrar n8n + Playwright
- [ ] Configurar Telegram bot
- [ ] Implementar scoring por pack
- [ ] Research web + Places API
- [ ] IA (Claude) para drafts
- [ ] A/B testing de segmentos
- [ ] Dashboard LinkedIn (invites, acceptance rate)
- [ ] Automatización completa del flujo

## 🎯 Ventajas del Diseño

### ✅ Extensible sin modificaciones
- Tablas LinkedIn ya existen (desactivadas)
- Solo activar cuando esté listo
- No rompe nada del CRM actual

### ✅ Deduplicación robusta
- Email OR linkedin_url OR teléfono
- Permite leads web sin LinkedIn
- Permite leads LinkedIn sin email
- Unificación cuando se conectan

### ✅ Origen dual
- formulario_id OR linkedin_lead_id en oportunidades
- Historial y tareas soportan ambos
- Métricas separadas pero unificables

### ✅ Pack-first approach
- Contacto tiene pack_asignado
- LinkedIn lead tiene pack_candidate
- Oportunidad hereda pack
- Scoring contextual por pack

### ✅ Señales preparadas
- Places API: place_id, rating, reviews
- Web signals: hash, tech_stack
- Research data: JSONB flexible
- Signal_changed para reciclaje

---

## 🚀 ¡Empieza con CRM, crece a Sourcing!

El diseño te permite:
1. **Hoy:** CRM profesional completo con Budibase
2. **Mañana:** Activar LinkedIn Sourcing sin tocar el schema
3. **Futuro:** Escalar a Concierge premium o SaaS

**Todo en una sola base de datos. Cero migraciones.**

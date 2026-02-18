-- ============================================================
-- 📚 POBLAR KNOWLEDGE BASE - Núcleo Tecnológico
-- Servicios, ICP, Pain Points
-- ============================================================

-- ============================================================
-- 🟢 PACK GUARDIAN (El Guardián)
-- ============================================================

INSERT INTO linkedin_knowledge_base (
    category, subcategory, title, content, target_pack, priority
) VALUES (
    'SERVICES',
    'GUARDIAN',
    'Pack GUARDIAN - El Guardián: Soporte Operativo & Continuidad',
    '{
        "short_description": "Soporte tecnológico proactivo para que la operación del día a día funcione sin pensar en IT",
        
        "detailed_description": "Pack diseñado para empresas que necesitan que la tecnología funcione sin tener que pensar en ella. Nos responsabilizamos del soporte operativo, actualizaciones, onboarding de nuevos usuarios y resolución de problemas críticos. Ideal para quien odia perder tiempo por fallos técnicos y valora la estabilidad sobre la innovación.",
        
        "what_includes": [
            "✔ Que los ordenadores y programas funcionen",
            "✔ Que las actualizaciones no rompan nada",
            "✔ Que los nuevos empleados entren sin caos",
            "✔ Que los problemas críticos se resuelvan",
            "✔ Que alguien controle el estado de los equipos",
            "✔ Monitorización proactiva de sistemas",
            "✔ Gestión de actualizaciones de seguridad",
            "✔ Soporte técnico en horario laboral (9-18h)"
        ],
        
        "what_NOT_includes": [
            "❌ Formación en software",
            "❌ Desarrollo o cambios funcionales",
            "❌ Proyectos grandes",
            "❌ Soporte ilimitado presencial",
            "❌ \"Me ayudas con esto rápido\" fuera de alcance"
        ],
        
        "pricing": {
            "base_monthly": "400-800 EUR/mes",
            "scaling_factor": "Escalable según número de usuarios/puestos",
            "billing": "Mensual, sin permanencia inicial",
            "setup_fee": "0 EUR"
        },
        
        "tagline": "Nos encargamos de que la tecnología de tu empresa funcione sin que tengas que pensar en ello"
    }'::jsonb,
    'GUARDIAN',
    100
);

INSERT INTO linkedin_knowledge_base (
    category, subcategory, title, content, target_pack, priority
) VALUES (
    'ICP_DEFINITION',
    'GUARDIAN',
    'ICP Pack GUARDIAN - Cliente Ideal',
    '{
        "company_profile": {
            "type": "Empresa local o digital sencilla, servicios profesionales, clínicas, centros, academias",
            "size": "1-10 empleados, 5-15 equipos",
            "revenue": "150k - 600k EUR/año",
            "it_maturity": "Sin IT interno - El dueño hace de IT improvisado",
            "stage": "Negocio ya en marcha, no recién creado"
        },
        
        "decision_maker": {
            "title": ["Founder", "CEO", "Director", "Propietario"],
            "mindset": [
                "No quiero pensar en ordenadores",
                "Solo quiero que funcione",
                "Odia perder tiempo por fallos tontos",
                "Valora confianza más que tecnología",
                "No quiere innovar - Quiere estabilidad"
            ],
            "technical_knowledge": "Muy bajo - usuario final"
        },
        
        "trigger_symptoms": [
            "Cada mes pasa algo con los ordenadores",
            "Cuando entra alguien nuevo es un caos",
            "Siempre vamos tarde con actualizaciones",
            "El antivirus molesta o no sabemos si funciona",
            "No tenemos claro qué equipos tenemos"
        ],
        
        "buying_signals_linkedin": [
            "Menciona problemas de continuidad operativa",
            "Publicó sobre crecimiento del equipo",
            "Anuncia nuevas contrataciones",
            "Quejándose de problemas técnicos",
            "Busca alguien que se responsabilice del IT"
        ],
        
        "what_really_buys": [
            "Que el día a día no se rompa",
            "Que alguien se responsabilice",
            "Que no le llamen por tonterías",
            "Confianza y tranquilidad"
        ],
        
        "disqualifiers": [
            "Autónomos solos",
            "Empresas que comparan precios al céntimo",
            "Solo cuando pasa algo - no preventivo",
            "¿Y si solo te llamo cuando lo necesito?",
            "Budget < 300 EUR/mes"
        ],
        
        "google_maps_search_terms": [
            "clínica dental {ciudad}",
            "centro médico {ciudad}",
            "academia formación {ciudad}",
            "consultoría {ciudad}",
            "asesoría {ciudad}",
            "despacho profesional {ciudad}"
        ],
        
        "linkedin_search_queries": [
            "Founder clínica dental España",
            "Director centro formación Madrid",
            "Propietario consultoría Barcelona",
            "CEO servicios profesionales Valencia"
        ]
    }'::jsonb,
    'GUARDIAN',
    100
);

INSERT INTO linkedin_knowledge_base (
    category, subcategory, title, content, target_pack, priority
) VALUES (
    'PAIN_POINTS',
    'GUARDIAN',
    'Pain Points Pack GUARDIAN',
    '{
        "critical_pains": [
            {
                "pain": "Cada mes pasa algo con los ordenadores",
                "implication": "Pérdida de productividad, frustración del equipo",
                "our_solution": "Monitorización proactiva que detecta problemas antes de que afecten"
            },
            {
                "pain": "Cuando entra alguien nuevo es un caos",
                "implication": "Mal onboarding = tiempo perdido + mala experiencia empleado",
                "our_solution": "Proceso estandarizado de alta de nuevos usuarios"
            },
            {
                "pain": "No tenemos claro qué equipos tenemos",
                "implication": "Sobrecostes, licencias duplicadas, riesgo de seguridad",
                "our_solution": "Inventario centralizado y actualizado automáticamente"
            }
        ]
    }'::jsonb,
    'GUARDIAN',
    80
);

-- ============================================================
-- 🔵 PACK MOTOR (El Motor)
-- ============================================================

INSERT INTO linkedin_knowledge_base (
    category, subcategory, title, content, target_pack, priority
) VALUES (
    'SERVICES',
    'MOTOR',
    'Pack MOTOR - El Motor: Socio Tecnológico & Eficiencia',
    '{
        "short_description": "Conectamos tus herramientas, automatizamos procesos repetitivos y tomamos decisiones técnicas con criterio",
        
        "detailed_description": "Pack para empresas que usan múltiples herramientas SaaS pero todo va por su lado. Actuamos como tu CTO externo: conectamos sistemas, automatizamos tareas manuales, mejoramos rendimiento y priorizamos lo que realmente importa. Ideal para agencias y empresas de servicios que necesitan eficiencia y orden.",
        
        "what_includes": [
            "✔ Conectar herramientas (integraciones API, webhooks, n8n)",
            "✔ Automatizar tareas repetitivas",
            "✔ Mejorar rendimiento del software",
            "✔ Decidir qué herramientas sobran (auditoría de stack)",
            "✔ Prioridad real cuando hay problemas",
            "✔ Sesiones de estrategia técnica mensuales",
            "✔ Todo lo del Pack GUARDIAN incluido"
        ],
        
        "what_NOT_includes": [
            "❌ Limpieza manual de datos (lo automatizamos, no lo hacemos a mano)",
            "❌ Marketing o ventas",
            "❌ Proyectos infinitos sin scope",
            "❌ Desarrollo de apps desde cero",
            "❌ Soporte reactivo sin límite"
        ],
        
        "pricing": {
            "base_monthly": "1,000-1,600 EUR/mes",
            "scaling_factor": "Según complejidad de integraciones y número de herramientas",
            "billing": "Mensual, contrato mínimo 3 meses",
            "setup_fee": "500 EUR (análisis inicial de stack)"
        },
        
        "tagline": "Ayudamos a empresas de servicios a eliminar trabajo manual y hacer que sus herramientas trabajen juntas"
    }'::jsonb,
    'MOTOR',
    100
);

INSERT INTO linkedin_knowledge_base (
    category, subcategory, title, content, target_pack, priority
) VALUES (
    'ICP_DEFINITION',
    'MOTOR',
    'ICP Pack MOTOR - Cliente Ideal',
    '{
        "company_profile": {
            "type": "Agencia, empresa de servicios digitales, negocio con procesos repetitivos",
            "size": "8-25 empleados, 10-30 herramientas SaaS",
            "revenue": "500k - 2M EUR/año",
            "it_maturity": "No tiene CTO - El dueño sigue decidiendo tecnología",
            "stage": "Crecimiento activo, pero caótico"
        },
        
        "decision_maker": {
            "title": ["Founder", "CEO", "COO", "Director General"],
            "mindset": [
                "Sabe que algo no va bien",
                "Odia el trabajo manual",
                "Quiere eficiencia",
                "Acepta pagar por orden y criterio",
                "No quiere parches - Quiere que todo encaje"
            ],
            "technical_knowledge": "Medio - entiende conceptos pero no ejecuta"
        },
        
        "trigger_symptoms": [
            "Copiamos datos entre sistemas",
            "La info nunca está en el mismo sitio",
            "El CRM va lento",
            "Cada herramienta va por su lado",
            "Estamos creciendo pero es un caos"
        ],
        
        "buying_signals_linkedin": [
            "Publicó sobre crecimiento rápido",
            "Anuncia expansión de servicios",
            "Quejándose de procesos manuales",
            "Busca optimización",
            "Menciona múltiples herramientas en posts"
        ],
        
        "what_really_buys": [
            "Tiempo (recuperar horas perdidas en manual)",
            "Orden (que todo esté conectado)",
            "Decisiones con criterio (alguien que piense el sistema completo)",
            "Escalabilidad sin caos"
        ],
        
        "disqualifiers": [
            "Hazme esta automatización puntual (quieren freelance, no partner)",
            "Solo quiero Zapier (no entienden el valor estratégico)",
            "Startups técnicas con CTO interno",
            "CTOs que quieren discutir cada decisión"
        ],
        
        "google_maps_search_terms": [
            "agencia marketing digital {ciudad}",
            "agencia diseño {ciudad}",
            "empresa servicios digitales {ciudad}",
            "consultoría tecnológica {ciudad}",
            "software empresarial {ciudad}"
        ],
        
        "linkedin_search_queries": [
            "CEO agencia digital España",
            "Founder agencia marketing Madrid",
            "COO servicios digitales Barcelona",
            "Director General consultoría Valencia"
        ]
    }'::jsonb,
    'MOTOR',
    100
);

INSERT INTO linkedin_knowledge_base (
    category, subcategory, title, content, target_pack, priority
) VALUES (
    'PAIN_POINTS',
    'MOTOR',
    'Pain Points Pack MOTOR',
    '{
        "critical_pains": [
            {
                "pain": "Copiamos datos entre sistemas",
                "implication": "5-10h/semana perdidas, errores humanos, datos desactualizados",
                "our_solution": "Integraciones automáticas vía API/webhooks - datos fluyen solos"
            },
            {
                "pain": "Cada herramienta va por su lado",
                "implication": "Información fragmentada, decisiones sin datos completos",
                "our_solution": "Stack integrado donde todo habla con todo"
            },
            {
                "pain": "Estamos creciendo pero es un caos",
                "implication": "No pueden escalar sin contratar más gente para tareas manuales",
                "our_solution": "Automatización que escala sin costes lineales"
            }
        ]
    }'::jsonb,
    'MOTOR',
    80
);

-- ============================================================
-- 🟣 PACK FORTALEZA (La Fortaleza)
-- ============================================================

INSERT INTO linkedin_knowledge_base (
    category, subcategory, title, content, target_pack, priority
) VALUES (
    'SERVICES',
    'FORTALEZA',
    'Pack FORTALEZA - La Fortaleza: CTO & Infraestructura Crítica',
    '{
        "short_description": "Nos responsabilizamos de que la infraestructura crítica sea estable, segura y escalable. CTO virtual incluido.",
        
        "detailed_description": "Pack para empresas cuya operación depende 100% de IT. Actuamos como CTO externo: monitorización 24/7, infraestructura cloud escalable, backups automáticos, seguridad continua y acompañamiento estratégico. Ideal para industria, logística, eCommerce serio donde una caída = pérdida directa de dinero.",
        
        "what_includes": [
            "✔ Monitorización proactiva 24/7",
            "✔ Infraestructura cloud escalable (AWS/Azure/GCP)",
            "✔ Backups y recuperación automática",
            "✔ Seguridad continua (pentesting, auditorías)",
            "✔ Acompañamiento tipo CTO (decisiones de arquitectura)",
            "✔ SLA de 2h en incidencias críticas",
            "✔ Informes ejecutivos mensuales",
            "✔ Todo lo del Pack MOTOR incluido"
        ],
        
        "what_NOT_includes": [
            "❌ Consumo cloud (factura aparte)",
            "❌ Hardware físico",
            "❌ Marketing o producto",
            "❌ Desarrollo de producto desde cero"
        ],
        
        "pricing": {
            "base_monthly": "1,700-2,500 EUR/mes",
            "scaling_factor": "Según criticidad y complejidad de infraestructura",
            "billing": "Mensual, contrato anual",
            "setup_fee": "1,500 EUR (análisis de riesgo e infraestructura)"
        },
        
        "tagline": "Nos responsabilizamos de que la infraestructura crítica de tu empresa sea estable, segura y escalable"
    }'::jsonb,
    'FORTALEZA',
    100
);

INSERT INTO linkedin_knowledge_base (
    category, subcategory, title, content, target_pack, priority
) VALUES (
    'ICP_DEFINITION',
    'FORTALEZA',
    'ICP Pack FORTALEZA - Cliente Ideal',
    '{
        "company_profile": {
            "type": "Industria, logística, eCommerce serio, operación dependiente de IT",
            "size": "20-80 empleados, sistemas críticos, infraestructura compleja",
            "revenue": "+1M EUR/año",
            "it_maturity": "Sin CTO interno sólido o CTO sobrecargado",
            "stage": "Empresa establecida con operación crítica 24/7"
        },
        
        "decision_maker": {
            "title": ["CEO", "COO", "Director General", "CTO (sobrecargado)"],
            "mindset": [
                "Piensa en riesgo",
                "Le preocupa seguridad y continuidad",
                "No quiere improvisar",
                "Valora contratos y SLA",
                "Entiende que barato sale caro"
            ],
            "technical_knowledge": "Alto - pero no tiene tiempo o equipo"
        },
        
        "trigger_symptoms": [
            "Si el sistema cae, perdemos dinero",
            "No sabemos si estamos bien protegidos",
            "Tenemos miedo a escalar",
            "Dependemos demasiado de una persona",
            "Tuvimos una caída importante recientemente"
        ],
        
        "buying_signals_linkedin": [
            "Anunció expansión internacional",
            "Publicó sobre incidente de seguridad/caída",
            "Busca CTO y no encuentra",
            "Menciona certificaciones (ISO, SOC2, etc.)",
            "Ronda de financiación reciente"
        ],
        
        "what_really_buys": [
            "Tranquilidad total",
            "Prevención (no reacción)",
            "Responsabilidad con SLA",
            "Visión técnica alineada con negocio"
        ],
        
        "disqualifiers": [
            "Startups (no tienen criticidad real todavía)",
            "Empresas vamos viendo (quieren probar)",
            "Clientes que discuten seguridad (no lo entienden)",
            "Esto nunca ha pasado (mentalidad reactiva)"
        ],
        
        "google_maps_search_terms": [
            "empresa logística {ciudad}",
            "distribuidora {ciudad}",
            "ecommerce {ciudad}",
            "plataforma digital {ciudad}",
            "industria {ciudad}"
        ],
        
        "linkedin_search_queries": [
            "CEO empresa logística España",
            "COO distribución Madrid",
            "Director General eCommerce Barcelona",
            "CTO industria Valencia"
        ]
    }'::jsonb,
    'FORTALEZA',
    100
);

INSERT INTO linkedin_knowledge_base (
    category, subcategory, title, content, target_pack, priority
) VALUES (
    'PAIN_POINTS',
    'FORTALEZA',
    'Pain Points Pack FORTALEZA',
    '{
        "critical_pains": [
            {
                "pain": "Si el sistema cae, perdemos dinero",
                "implication": "Facturación parada, clientes afectados, reputación dañada",
                "our_solution": "Monitorización 24/7 con SLA de 2h - detectamos y actuamos antes"
            },
            {
                "pain": "No sabemos si estamos bien protegidos",
                "implication": "Riesgo de brecha de seguridad, incumplimiento GDPR, multas",
                "our_solution": "Auditorías continuas + pentesting + monitorización de amenazas"
            },
            {
                "pain": "Tenemos miedo a escalar",
                "implication": "No pueden crecer porque la infraestructura no aguanta",
                "our_solution": "Arquitectura cloud escalable que crece con el negocio"
            }
        ]
    }'::jsonb,
    'FORTALEZA',
    80
);

-- ============================================================
-- VERIFICACIÓN
-- ============================================================

SELECT 
    target_pack as "Pack",
    category as "Categoría",
    title as "Título",
    priority as "Prioridad"
FROM linkedin_knowledge_base
WHERE is_active = TRUE
ORDER BY target_pack, category, priority DESC;

\echo ''
\echo '✅ Knowledge Base poblada con 3 packs:'
\echo '   🟢 GUARDIAN (400-800€): Soporte & Continuidad'
\echo '   🔵 MOTOR (1,000-1,600€): Eficiencia & Integraciones'
\echo '   🟣 FORTALEZA (1,700-2,500€): CTO & Infraestructura Crítica'
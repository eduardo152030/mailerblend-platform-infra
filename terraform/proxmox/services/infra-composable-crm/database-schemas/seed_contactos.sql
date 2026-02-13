-- Seed mínimo para CRM (contactos)
-- Checks relevantes:
--   estado: ACTIVO|INACTIVO|DESCALIFICADO|BLOQUEADO
--   origen: FORMULARIO_WEB|MANUAL|LINKEDIN_SOURCING|IMPORTACION|REFERIDO|EVENTO
-- Idempotente por email sin UNIQUE(email)
/*
  jainer@Jainer:~/work/mailerblend-platform-infra/terraform/proxmox$ python3 services/infra-composable-crm/database-schemas/cleanup_seed_contacts.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🧹 Limpiando contactos seed del CRM (Postgres)
  🧩 Target: 192.168.1.118:supabase-db db=postgres user=pgadmin2026f
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📧 Contactos a eliminar:
   • maria.garcia@pyme-tech.es
   • carlos@agenciadigital.com
   • laura@startup-ai.io
   • javier@comercio-online.es
   • ana.torres@fintech-startup.com
   • roberto@consultoria-it.es
   • elena@emprendedora.com

⚠️  ¿Estás seguro de eliminar estos contactos y todas sus dependencias? [y/N]: y

🗑️  Ejecutando limpieza...

✅ Limpieza completada exitosamente

📊 Registros eliminados:
   • Contactos:           7
   • Parámetros UTM:      7
   • Formularios Web:     7
   • Facturas:            0
   • Presupuestos:        0
   • Pendientes:          0
   • Historial:           0
   • Oportunidades:       0

   📌 Total dependencias: 14
   📌 Total general:      21

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Base de datos limpia
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

jainer@Jainer:~/work/mailerblend-platform-infra/terraform/proxmox$ 
*/


WITH seed(
  nombre, email, telefono, cargo, company_name, tipo_empresa, company_size, industry,
  website, linkedin_url, ciudad, pais, direccion, origen, estado,
  gdpr_consent, gdpr_consent_date, marketing_consent
) AS (
  VALUES
    ('Alicia García', 'alicia@pyme-tech.es', '+34 600 111 222', 'Operations Manager',
     'PYME Tech Solutions', 'Pyme', '11-50', 'IT Services',
     'https://pyme-tech.es', 'https://www.linkedin.com/in/alicia-garcia/', 'Barcelona', 'ES',
     'Barcelona, España', 'MANUAL', 'ACTIVO', true, now(), false),

    ('Carlos Martínez', 'carlos@agenciadigital.com', '+34 600 222 333', 'Founder',
     'Agencia Digital Creativa', 'Agencia', '1-10', 'Marketing',
     'https://agenciadigital.com', 'https://www.linkedin.com/in/carlos-martinez/', 'Barcelona', 'ES',
     'Barcelona, España', 'MANUAL', 'ACTIVO', true, now(), true),

    ('Laura Sánchez', 'laura@startup-ai.io', '+34 600 333 444', 'CTO',
     'Startup AI Solutions', 'Startup', '1-10', 'Software',
     'https://startup-ai.io', 'https://www.linkedin.com/in/laura-sanchez/', 'Barcelona', 'ES',
     'Barcelona, España', 'MANUAL', 'ACTIVO', true, now(), true)
)
INSERT INTO contactos (
  nombre, email, telefono, cargo, company_name, tipo_empresa, company_size, industry,
  website, linkedin_url, ciudad, pais, direccion, origen, estado,
  gdpr_consent, gdpr_consent_date, marketing_consent,
  created_at, updated_at, pack_asignado
)
SELECT
  s.nombre, s.email, s.telefono, s.cargo, s.company_name, s.tipo_empresa, s.company_size, s.industry,
  s.website, s.linkedin_url, s.ciudad, s.pais, s.direccion, s.origen, s.estado,
  s.gdpr_consent, s.gdpr_consent_date, s.marketing_consent,
  now(), now(), 'NO_ASIGNADO'
FROM seed s
WHERE NOT EXISTS (
  SELECT 1 FROM contactos c WHERE c.email = s.email
);

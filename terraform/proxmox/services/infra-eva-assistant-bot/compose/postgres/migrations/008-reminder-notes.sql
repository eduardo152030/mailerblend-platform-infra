-- 008-reminder-notes.sql
-- Añade campo notes a reminders para guardar contexto adicional

ALTER TABLE reminders ADD COLUMN IF NOT EXISTS notes TEXT;

COMMENT ON COLUMN reminders.notes IS 'Contexto opcional del usuario: por qué se pospone, con quién confirmar, etc.';
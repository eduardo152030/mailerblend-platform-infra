-- 012-reminder-enrichment.sql
-- Añade campos enriquecidos a reminders

ALTER TABLE reminders ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE reminders ADD COLUMN IF NOT EXISTS url TEXT;
ALTER TABLE reminders ADD COLUMN IF NOT EXISTS tags TEXT;

COMMENT ON COLUMN reminders.description IS 'Descripción WYSIWYG en HTML (TipTap)';
COMMENT ON COLUMN reminders.url IS 'URL asociada a la tarea';
COMMENT ON COLUMN reminders.tags IS 'Hashtags: #NT #personal #mailerblend #contenido #sage';

-- Tabla de adjuntos (si no existe)
CREATE TABLE IF NOT EXISTS task_attachments (
    id          SERIAL PRIMARY KEY,
    reminder_id INTEGER NOT NULL REFERENCES reminders(id) ON DELETE CASCADE,
    filename    TEXT NOT NULL,
    original_name TEXT NOT NULL,
    mime_type   TEXT NOT NULL,
    size_bytes  INTEGER NOT NULL DEFAULT 0,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_task_attachments_reminder_id ON task_attachments(reminder_id);
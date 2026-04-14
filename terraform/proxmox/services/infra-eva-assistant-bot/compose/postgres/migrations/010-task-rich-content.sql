-- 010-task-rich-content.sql
-- Añade descripción WYSIWYG y adjuntos a reminders

ALTER TABLE reminders ADD COLUMN IF NOT EXISTS description TEXT;
COMMENT ON COLUMN reminders.description IS 'Descripción WYSIWYG en formato HTML (TipTap)';

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
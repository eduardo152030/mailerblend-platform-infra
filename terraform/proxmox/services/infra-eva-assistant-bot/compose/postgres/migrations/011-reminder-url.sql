-- 011-reminder-url.sql
ALTER TABLE reminders ADD COLUMN IF NOT EXISTS url TEXT;
ALTER TABLE reminders ADD COLUMN IF NOT EXISTS description TEXT;
COMMENT ON COLUMN reminders.url IS 'URL asociada a la tarea';
COMMENT ON COLUMN reminders.description IS 'Descripción WYSIWYG en HTML (TipTap)';
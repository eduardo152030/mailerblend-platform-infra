-- 012-reminder-tags.sql
ALTER TABLE reminders ADD COLUMN IF NOT EXISTS tags TEXT;
COMMENT ON COLUMN reminders.tags IS 'Hashtags: #NT #personal #mailerblend #contenido';
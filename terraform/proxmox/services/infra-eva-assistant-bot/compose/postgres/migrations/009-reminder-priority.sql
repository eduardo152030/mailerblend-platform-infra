-- 009-reminder-priority.sql
-- Añade campo priority a reminders (P0-P4, default P3)

ALTER TABLE reminders ADD COLUMN IF NOT EXISTS priority TEXT DEFAULT 'P3';

COMMENT ON COLUMN reminders.priority IS 'Prioridad P0-P4: P0=Critical, P1=High, P2=Moderate, P3=Low, P4=Negligible';
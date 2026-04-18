-- 015-undated-tasks-reminder.sql

-- Configuración del sistema de recordatorios por tareas sin fecha
CREATE TABLE IF NOT EXISTS undated_tasks_config (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Valores por defecto
INSERT INTO undated_tasks_config (key, value) VALUES
    ('enabled',                      'true'),
    ('days_threshold',               '7'),
    ('minimum_tasks_for_summary',    '3'),
    ('send_individual_alerts',       'true'),
    ('send_summary_alert',           'true'),
    ('max_items_in_summary',         '5')
ON CONFLICT (key) DO NOTHING;

-- Historial de alertas enviadas (anti-spam)
CREATE TABLE IF NOT EXISTS undated_task_alerts (
    id          SERIAL PRIMARY KEY,
    reminder_id INTEGER NOT NULL REFERENCES reminders(id) ON DELETE CASCADE,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_undated_task_alerts_reminder_id
    ON undated_task_alerts(reminder_id);
CREATE INDEX IF NOT EXISTS idx_undated_task_alerts_created_at
    ON undated_task_alerts(created_at);
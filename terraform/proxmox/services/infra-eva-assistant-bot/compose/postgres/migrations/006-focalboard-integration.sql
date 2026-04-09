-- 006-focalboard-integration.sql
-- Añade soporte para sincronización bidireccional con Focalboard
-- Compatible con el esquema existente de EVA

-- ── 1. Vincular reminders con tarjetas de Focalboard ──────────────────────
ALTER TABLE reminders
  ADD COLUMN IF NOT EXISTS focalboard_card_id TEXT DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS focalboard_synced_at TIMESTAMPTZ DEFAULT NULL;

CREATE INDEX IF NOT EXISTS idx_reminders_focalboard_card
  ON reminders (focalboard_card_id)
  WHERE focalboard_card_id IS NOT NULL;

-- ── 2. Tabla de proyectos (mapea a boards de Focalboard) ──────────────────
CREATE TABLE IF NOT EXISTS projects (
  id               SERIAL PRIMARY KEY,
  user_id          INTEGER REFERENCES users(id) ON DELETE CASCADE,
  name             TEXT NOT NULL,
  focalboard_board_id TEXT DEFAULT NULL,
  color            TEXT DEFAULT 'blue',
  is_active        BOOLEAN NOT NULL DEFAULT TRUE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_projects_user ON projects (user_id);
CREATE INDEX IF NOT EXISTS idx_projects_board ON projects (focalboard_board_id)
  WHERE focalboard_board_id IS NOT NULL;

-- ── 3. Tabla de tareas (más flexible que reminders, mapea a cards) ─────────
CREATE TABLE IF NOT EXISTS tasks (
  id               SERIAL PRIMARY KEY,
  user_id          INTEGER REFERENCES users(id) ON DELETE CASCADE,
  project_id       INTEGER REFERENCES projects(id) ON DELETE SET NULL,
  reminder_id      INTEGER REFERENCES reminders(id) ON DELETE SET NULL,
  title            TEXT NOT NULL,
  description      TEXT DEFAULT NULL,
  status           TEXT NOT NULL DEFAULT 'pending',
                   -- pending | in_progress | done | cancelled
  priority         TEXT NOT NULL DEFAULT 'normal',
                   -- low | normal | high | urgent
  due_at           TIMESTAMPTZ DEFAULT NULL,
  focalboard_card_id TEXT DEFAULT NULL,
  focalboard_synced_at TIMESTAMPTZ DEFAULT NULL,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tasks_user     ON tasks (user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_project  ON tasks (project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_reminder ON tasks (reminder_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status   ON tasks (status);
CREATE INDEX IF NOT EXISTS idx_tasks_focalboard ON tasks (focalboard_card_id)
  WHERE focalboard_card_id IS NOT NULL;

-- ── 4. Log de sincronización (auditoría de cada sync) ─────────────────────
CREATE TABLE IF NOT EXISTS sync_log (
  id               SERIAL PRIMARY KEY,
  entity_type      TEXT NOT NULL,  -- 'reminder' | 'task' | 'project'
  entity_id        INTEGER NOT NULL,
  direction        TEXT NOT NULL,  -- 'eva_to_fb' | 'fb_to_eva'
  action           TEXT NOT NULL,  -- 'create' | 'update' | 'delete'
  focalboard_id    TEXT DEFAULT NULL,
  payload          JSONB NOT NULL DEFAULT '{}',
  error            TEXT DEFAULT NULL,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sync_log_entity ON sync_log (entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_sync_log_created ON sync_log (created_at DESC);

-- ── 5. Trigger: actualizar updated_at en tasks automáticamente ─────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tasks_updated_at ON tasks;
CREATE TRIGGER tasks_updated_at
  BEFORE UPDATE ON tasks
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ── 6. Vista útil: recordatorios con su tarjeta de Focalboard ──────────────
CREATE OR REPLACE VIEW reminders_with_sync AS
  SELECT
    r.*,
    t.id           AS task_id,
    t.project_id,
    t.priority,
    t.focalboard_card_id AS task_card_id,
    p.name         AS project_name,
    p.focalboard_board_id
  FROM reminders r
  LEFT JOIN tasks t ON t.reminder_id = r.id
  LEFT JOIN projects p ON p.id = t.project_id;
CREATE TABLE IF NOT EXISTS users (
  id BIGSERIAL PRIMARY KEY,
  telegram_chat_id BIGINT UNIQUE NOT NULL,
  telegram_username TEXT,
  display_name TEXT,
  timezone TEXT DEFAULT 'Europe/Madrid',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reminders (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  source_text TEXT NOT NULL,
  task_text TEXT NOT NULL,
  remind_at TIMESTAMPTZ NOT NULL,
  status TEXT NOT NULL DEFAULT 'scheduled',
  recurrence_type TEXT,
  recurrence_value TEXT,
  weekdays_only BOOLEAN NOT NULL DEFAULT FALSE,
  remind_if_no_response BOOLEAN NOT NULL DEFAULT FALSE,
  retry_delay_minutes INTEGER,
  cancel_on_event_type TEXT,
  last_sent_at TIMESTAMPTZ,
  acked_at TIMESTAMPTZ,
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  sent_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_reminders_status_remind_at
  ON reminders(status, remind_at);

CREATE INDEX IF NOT EXISTS idx_reminders_user_status
  ON reminders(user_id, status);

CREATE TABLE IF NOT EXISTS events (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
  event_type TEXT NOT NULL,
  event_value TEXT,
  source TEXT NOT NULL DEFAULT 'system',
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_events_user_type_created
  ON events(user_id, event_type, created_at);

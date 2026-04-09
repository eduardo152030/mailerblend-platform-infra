ALTER TABLE reminders
ADD COLUMN IF NOT EXISTS is_persistent BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS repeat_every_minutes INTEGER NULL,
ADD COLUMN IF NOT EXISTS stop_at TIMESTAMPTZ NULL,
ADD COLUMN IF NOT EXISTS awaiting_ack BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ NULL,
ADD COLUMN IF NOT EXISTS expired_at TIMESTAMPTZ NULL,
ADD COLUMN IF NOT EXISTS cancelled_at TIMESTAMPTZ NULL,
ADD COLUMN IF NOT EXISTS ack_text TEXT NULL;

ALTER TABLE reminders
ADD COLUMN IF NOT EXISTS retry_count INTEGER NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS max_retries INTEGER NOT NULL DEFAULT 3;

CREATE INDEX IF NOT EXISTS idx_reminders_status_remind_at
  ON reminders(status, remind_at);

CREATE INDEX IF NOT EXISTS idx_reminders_user_status
  ON reminders(user_id, status);

CREATE INDEX IF NOT EXISTS idx_reminders_user_awaiting_ack
  ON reminders(user_id, awaiting_ack, last_sent_at DESC);

CREATE INDEX IF NOT EXISTS idx_events_user_type_created
  ON events(user_id, event_type, created_at DESC);
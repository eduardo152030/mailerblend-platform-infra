BEGIN;
CREATE SCHEMA IF NOT EXISTS crm_notifications;

CREATE TABLE IF NOT EXISTS crm_notifications.preferences (
  id boolean PRIMARY KEY DEFAULT true CHECK (id),
  enabled boolean NOT NULL DEFAULT false,
  recipients text[] NOT NULL DEFAULT '{}',
  CHECK (cardinality(recipients) <= 25)
);

INSERT INTO crm_notifications.preferences DEFAULT VALUES ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS crm_notifications.contact_delivery (
  contact_id uuid NOT NULL REFERENCES public.contactos(id) ON DELETE CASCADE,
  recipient text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  attempts integer NOT NULL DEFAULT 0 CHECK (attempts BETWEEN 0 AND 6),
  next_attempt_at timestamptz NOT NULL DEFAULT now(),
  sent_at timestamptz,
  last_error text,
  PRIMARY KEY (contact_id, recipient)
);
CREATE INDEX IF NOT EXISTS contact_delivery_ready
  ON crm_notifications.contact_delivery (next_attempt_at, created_at)
  WHERE sent_at IS NULL AND attempts < 6;
CREATE TABLE IF NOT EXISTS crm_notifications.delivery_attempt (
  contact_id uuid NOT NULL,
  recipient text NOT NULL,
  attempt integer NOT NULL,
  attempted_at timestamptz NOT NULL DEFAULT now(),
  error_type text,
  PRIMARY KEY (contact_id, recipient, attempt),
  FOREIGN KEY (contact_id, recipient) REFERENCES crm_notifications.contact_delivery
    ON DELETE CASCADE
);
COMMIT;

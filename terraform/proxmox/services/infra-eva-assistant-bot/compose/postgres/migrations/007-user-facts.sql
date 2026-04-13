-- 007-user-facts.sql
-- Memoria semántica de EVA: hechos sobre el usuario extraídos de conversaciones

CREATE TABLE IF NOT EXISTS user_facts (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key         TEXT NOT NULL,          -- ej: "logopeda_ian", "hora_fichar", "nombre"
    value       TEXT NOT NULL,          -- ej: "miércoles a las 17:00", "08:00", "Jainer"
    source      TEXT NOT NULL DEFAULT 'conversation',  -- conversation | manual | inferred
    confidence  FLOAT NOT NULL DEFAULT 1.0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(user_id, key)
);

CREATE INDEX IF NOT EXISTS idx_user_facts_user_id ON user_facts(user_id);

-- Trigger para updated_at automático
CREATE OR REPLACE FUNCTION update_user_facts_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS user_facts_updated_at ON user_facts;
CREATE TRIGGER user_facts_updated_at
    BEFORE UPDATE ON user_facts
    FOR EACH ROW EXECUTE FUNCTION update_user_facts_updated_at();
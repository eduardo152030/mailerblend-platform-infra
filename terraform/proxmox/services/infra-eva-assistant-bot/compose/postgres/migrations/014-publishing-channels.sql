-- 014-publishing-channels.sql
-- Sistema de recordatorios de publicación por canal

CREATE TABLE IF NOT EXISTS publishing_channels (
    id                      SERIAL PRIMARY KEY,
    user_id                 INTEGER REFERENCES users(id) ON DELETE CASCADE,
    channel                 TEXT NOT NULL,              -- 'linkedin', 'youtube', 'tiktok'
    display_name            TEXT NOT NULL,              -- 'LinkedIn', 'YouTube', 'TikTok'
    enabled                 BOOLEAN NOT NULL DEFAULT TRUE,
    last_published_at       TIMESTAMP WITH TIME ZONE,
    max_days_without_posting INTEGER NOT NULL DEFAULT 7,
    -- Preparado para escalar (no usado en MVP)
    target_posts_per_week   NUMERIC(5,2),               -- e.g. 3.0 = 3 veces/semana
    target_posts_per_day    NUMERIC(5,2),               -- e.g. 2.0 = 2 veces/día
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at              TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(user_id, channel)
);

CREATE INDEX IF NOT EXISTS idx_publishing_channels_user_id
    ON publishing_channels(user_id);

-- Insertar canales iniciales para el usuario admin (id=21, ajusta si es diferente)
-- Se usa ON CONFLICT para que sea idempotente
INSERT INTO publishing_channels (user_id, channel, display_name, max_days_without_posting, enabled)
SELECT u.id, 'linkedin', 'LinkedIn', 5, TRUE FROM users u LIMIT 1
ON CONFLICT (user_id, channel) DO NOTHING;

INSERT INTO publishing_channels (user_id, channel, display_name, max_days_without_posting, enabled)
SELECT u.id, 'youtube', 'YouTube', 14, TRUE FROM users u LIMIT 1
ON CONFLICT (user_id, channel) DO NOTHING;

INSERT INTO publishing_channels (user_id, channel, display_name, max_days_without_posting, enabled)
SELECT u.id, 'tiktok', 'TikTok', 7, TRUE FROM users u LIMIT 1
ON CONFLICT (user_id, channel) DO NOTHING;

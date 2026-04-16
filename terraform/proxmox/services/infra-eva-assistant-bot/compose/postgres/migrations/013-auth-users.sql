-- 013-auth-users.sql
-- Sistema de autenticación EVA
-- Estado: LISTO para ejecutar cuando se active el módulo auth
-- Ejecutar: docker exec -i eva-postgres psql -U eva -d eva < 013-auth-users.sql

-- Tabla de usuarios UI (separada de la tabla users existente de Telegram)
CREATE TABLE IF NOT EXISTS eva_users (
    id           SERIAL PRIMARY KEY,
    username     TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    display_name TEXT,
    is_active    BOOLEAN NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Tabla de permisos por área
CREATE TABLE IF NOT EXISTS user_permissions (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES eva_users(id) ON DELETE CASCADE,
    area       TEXT NOT NULL CHECK (area IN ('tareas', 'contenido')),
    can_read   BOOLEAN NOT NULL DEFAULT TRUE,
    can_write  BOOLEAN NOT NULL DEFAULT FALSE,
    can_delete BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE(user_id, area)
);

-- Usuario admin inicial (password: Tsu4MvniPjERtSgaWz7G)
-- Hash generado con bcrypt rounds=12
-- IMPORTANTE: cambiar password después de activar el módulo
INSERT INTO eva_users (username, password_hash, display_name, is_active)
VALUES (
    'eduardovl5',
    '$2b$12$placeholder_change_this_hash_before_activating',
    'Eduardo Velázquez',
    TRUE
) ON CONFLICT (username) DO NOTHING;

-- Permisos completos para admin
INSERT INTO user_permissions (user_id, area, can_read, can_write, can_delete)
SELECT id, 'tareas',    TRUE, TRUE, TRUE FROM eva_users WHERE username = 'eduardovl5'
ON CONFLICT (user_id, area) DO NOTHING;

INSERT INTO user_permissions (user_id, area, can_read, can_write, can_delete)
SELECT id, 'contenido', TRUE, TRUE, TRUE FROM eva_users WHERE username = 'eduardovl5'
ON CONFLICT (user_id, area) DO NOTHING;

-- Índices
CREATE INDEX IF NOT EXISTS idx_user_permissions_user_id ON user_permissions(user_id);
CREATE INDEX IF NOT EXISTS idx_eva_users_username ON eva_users(username);

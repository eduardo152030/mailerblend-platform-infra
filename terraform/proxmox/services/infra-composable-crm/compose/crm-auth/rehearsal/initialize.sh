#!/bin/sh
set -eu
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
    -v auth_password="$POSTGRES_PASSWORD" <<'SQL'
CREATE ROLE crm_auth LOGIN NOINHERIT PASSWORD :'auth_password';
CREATE SCHEMA auth AUTHORIZATION crm_auth;
ALTER ROLE crm_auth IN DATABASE postgres SET search_path TO auth;
SQL

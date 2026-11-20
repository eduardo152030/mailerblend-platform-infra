BEGIN;
CREATE ROLE crm_auth LOGIN NOINHERIT PASSWORD :'auth_password';
CREATE SCHEMA auth AUTHORIZATION crm_auth;
ALTER ROLE crm_auth IN DATABASE postgres SET search_path TO auth;
COMMIT;

-- 02_patch_contacto_nombre_denorm.sql
-- Denormaliza contactos.nombre -> contacto_nombre en tablas seleccionadas
-- Idempotente + triggers para mantener consistencia.
/*
  REFERENCIA TÉCNICA - PARCHE 01:
  Este bloque denormaliza el nombre del contacto para mejorar la legibilidad.
  Se aplica a las 7 tablas principales del CRM.
  Mantiene sincronización mediante triggers automáticos.
  Revisado: 2026-02-09
  jainer@Jainer:~/work/mailerblend-platform-infra/terraform/proxmox/services/infra-composable-crm/database-schemas$ ssh root@${CRM_DB_HOST} \
  "docker exec -i ${CRM_DB_CONTAINER} env PGPASSWORD='${CRM_DB_PASS}' \
   psql -U '${CRM_DB_USER}' -d '${CRM_DB_NAME}' -v ON_ERROR_STOP=1" \
  < 01_patch_contacto_nombre_denorm.sql
BEGIN
CREATE FUNCTION
CREATE FUNCTION
DO
DO
COMMIT
jainer@Jainer:~/work/mailerblend-platform-infra/terraform/proxmox/services/infra-composable-crm/database-schemas$
*/

BEGIN;

-- 1) Función: setea contacto_nombre en tablas hijas (por FK a contactos)
CREATE OR REPLACE FUNCTION crm_set_contacto_nombre()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  fk_col text := TG_ARGV[0];
  ref_col text := TG_ARGV[1]; -- columna referenciada en contactos (normalmente "id")
  sql text;
  fk_value text;
BEGIN
  -- Obtener el valor del FK dinámicamente
  sql := format('SELECT ($1).%I::text', fk_col);
  EXECUTE sql INTO fk_value USING NEW;

  -- Si el FK viene NULL, limpiamos el nombre
  IF fk_value IS NULL THEN
    NEW.contacto_nombre := NULL;
    RETURN NEW;
  END IF;

  -- Set contacto_nombre desde contactos.nombre
  sql := format(
    'SELECT c.nombre FROM contactos c WHERE c.%I::text = $1',
    ref_col
  );

  EXECUTE sql INTO NEW.contacto_nombre USING fk_value;

  RETURN NEW;
END;
$$;

-- 2) Función: propaga cambios de contactos.nombre a tablas hijas
CREATE OR REPLACE FUNCTION crm_propagate_contacto_nombre_update()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  t record;
  sql text;
BEGIN
  IF NEW.nombre IS NOT DISTINCT FROM OLD.nombre THEN
    RETURN NEW;
  END IF;

  -- Lista fija (7 tablas) + detectar dinámicamente el FK y columna referenciada
  FOR t IN
    WITH targets(tbl) AS (
      VALUES
        ('parametros_utm'::text),
        ('formulario_web'::text),
        ('facturas'::text),
        ('presupuestos'::text),
        ('pendientes'::text),
        ('historial'::text),
        ('oportunidades'::text)
    )
    SELECT
      targets.tbl,
      a.attname  AS fk_col,
      a2.attname AS ref_col
    FROM targets
    JOIN pg_class c        ON c.relname = targets.tbl
    JOIN pg_namespace n    ON n.oid = c.relnamespace
    JOIN pg_constraint con ON con.conrelid = c.oid
    JOIN pg_class cref     ON cref.oid = con.confrelid
    JOIN pg_namespace nref ON nref.oid = cref.relnamespace
    JOIN LATERAL unnest(con.conkey)  WITH ORDINALITY AS ck(attnum, ord) ON TRUE
    JOIN LATERAL unnest(con.confkey) WITH ORDINALITY AS fk(attnum, ord) ON fk.ord = ck.ord
    JOIN pg_attribute a  ON a.attrelid  = c.oid    AND a.attnum  = ck.attnum
    JOIN pg_attribute a2 ON a2.attrelid = cref.oid AND a2.attnum = fk.attnum
    WHERE con.contype = 'f'
      AND cref.relname = 'contactos'
      AND n.nspname = 'public'
      AND nref.nspname = 'public'
  LOOP
    sql := format(
      'UPDATE %I SET contacto_nombre = $1 WHERE %I = $2',
      t.tbl, t.fk_col
    );
    EXECUTE sql USING NEW.nombre, NEW.id;
  END LOOP;

  RETURN NEW;
END;
$$;

-- 3) Trigger en contactos: al cambiar nombre, propaga a hijas (idempotente)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'trg_contactos_propagate_nombre'
  ) THEN
    CREATE TRIGGER trg_contactos_propagate_nombre
    AFTER UPDATE OF nombre ON contactos
    FOR EACH ROW
    EXECUTE FUNCTION crm_propagate_contacto_nombre_update();
  END IF;
END $$;

-- 4) Patch por tabla (add column, backfill, trigger per-table)
DO $$
DECLARE
  tbl text;
  fk_col text;
  ref_col text;
  sql text;
BEGIN
  FOREACH tbl IN ARRAY ARRAY[
    'parametros_utm',
    'formulario_web',
    'facturas',
    'presupuestos',
    'pendientes',
    'historial',
    'oportunidades'
  ]
  LOOP
    -- Detectar FK de la tabla hacia contactos (toma el primero si hubiera varios)
    SELECT a.attname, a2.attname
      INTO fk_col, ref_col
    FROM pg_class c
    JOIN pg_namespace n    ON n.oid = c.relnamespace
    JOIN pg_constraint con ON con.conrelid = c.oid
    JOIN pg_class cref     ON cref.oid = con.confrelid
    JOIN pg_namespace nref ON nref.oid = cref.relnamespace
    JOIN LATERAL unnest(con.conkey)  WITH ORDINALITY AS ck(attnum, ord) ON TRUE
    JOIN LATERAL unnest(con.confkey) WITH ORDINALITY AS fk(attnum, ord) ON fk.ord = ck.ord
    JOIN pg_attribute a  ON a.attrelid  = c.oid    AND a.attnum  = ck.attnum
    JOIN pg_attribute a2 ON a2.attrelid = cref.oid AND a2.attnum = fk.attnum
    WHERE con.contype = 'f'
      AND c.relname = tbl
      AND n.nspname = 'public'
      AND cref.relname = 'contactos'
      AND nref.nspname = 'public'
    ORDER BY con.oid
    LIMIT 1;

    IF fk_col IS NULL THEN
      RAISE NOTICE 'Tabla %: no tiene FK hacia contactos. Se omite.', tbl;
      CONTINUE;
    END IF;

    -- Add column si no existe
    sql := format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS contacto_nombre text;', tbl);
    EXECUTE sql;

    -- Backfill (solo donde esté NULL)
    sql := format(
      'UPDATE %I t
       SET contacto_nombre = c.nombre
       FROM contactos c
       WHERE t.contacto_nombre IS NULL
         AND t.%I = c.%I;',
      tbl, fk_col, COALESCE(ref_col, 'id')
    );
    EXECUTE sql;

    -- Trigger nombre único por tabla (idempotente)
    IF NOT EXISTS (
      SELECT 1
      FROM pg_trigger
      WHERE tgname = format('trg_%s_set_contacto_nombre', tbl)
    ) THEN
      sql := format(
        'CREATE TRIGGER %I
         BEFORE INSERT OR UPDATE OF %I ON %I
         FOR EACH ROW
         EXECUTE FUNCTION crm_set_contacto_nombre(%L, %L);',
        format('trg_%s_set_contacto_nombre', tbl),
        fk_col,
        tbl,
        fk_col,
        COALESCE(ref_col, 'id')
      );
      EXECUTE sql;
    END IF;

  END LOOP;
END $$;

COMMIT;
-- 04_add_updated_at_pendientes.sql
BEGIN;

-- 1) Columna updated_at
ALTER TABLE public.pendientes
  ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now();

-- Backfill "bonito": si existía created_at, alínealo (por si acaso)
UPDATE public.pendientes
SET updated_at = created_at
WHERE updated_at IS NULL AND created_at IS NOT NULL;

-- 2) Trigger genérico updated_at (idempotente)
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_trigger
    WHERE tgname = 'trg_pendientes_set_updated_at'
  ) THEN
    CREATE TRIGGER trg_pendientes_set_updated_at
    BEFORE UPDATE ON public.pendientes
    FOR EACH ROW
    EXECUTE FUNCTION public.set_updated_at();
  END IF;
END $$;

COMMIT;

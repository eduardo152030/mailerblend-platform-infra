-- 04_add_urgencia.sql
-- Adds "urgencia" to formulario_web + oportunidades with CHECK constraint.
-- Values must match frontend literals:
--  - Lo antes posible
--  - Durante este mes
--  - En los próximos 2-3 meses
--  - Aún no lo sé

BEGIN;

ALTER TABLE public.formulario_web
  ADD COLUMN IF NOT EXISTS urgencia VARCHAR(50);

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'formulario_web_urgencia_check'
  ) THEN
    ALTER TABLE public.formulario_web
      ADD CONSTRAINT formulario_web_urgencia_check
      CHECK (
        urgencia IS NULL OR urgencia IN (
          'Lo antes posible',
          'Durante este mes',
          'En los próximos 2-3 meses',
          'Aún no lo sé'
        )
      );
  END IF;
END$$;

ALTER TABLE public.oportunidades
  ADD COLUMN IF NOT EXISTS urgencia VARCHAR(50);

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'oportunidades_urgencia_check'
  ) THEN
    ALTER TABLE public.oportunidades
      ADD CONSTRAINT oportunidades_urgencia_check
      CHECK (
        urgencia IS NULL OR urgencia IN (
          'Lo antes posible',
          'Durante este mes',
          'En los próximos 2-3 meses',
          'Aún no lo sé'
        )
      );
  END IF;
END$$;

COMMIT;
BEGIN;

-- 1) columna nueva con default seguro (para no romper inserts antiguos)
ALTER TABLE public.gastos
  ADD COLUMN IF NOT EXISTS project_key varchar(20) NOT NULL DEFAULT 'Nucleo_tecnologico';

-- 2) constraint (sin IF NOT EXISTS porque PostgreSQL no lo soporta en constraints)
-- Si ya existe, fallará y puedes ignorar el error
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint 
    WHERE conname = 'gastos_project_key_check'
  ) THEN
    ALTER TABLE public.gastos
      ADD CONSTRAINT gastos_project_key_check
      CHECK (project_key::text = ANY (ARRAY['Nucleo_tecnologico','Mailerblend','SHARED']::text[]));
  END IF;
END$$;

-- 3) index para filtros Budibase
CREATE INDEX IF NOT EXISTS idx_gastos_project_key ON public.gastos USING btree (project_key);

COMMIT;
BEGIN;

CREATE TABLE IF NOT EXISTS public.proveedores (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  nombre text NOT NULL,
  cif varchar(50),
  tipo varchar(50) NOT NULL DEFAULT 'OTRO',
  email text,
  telefono text,
  website text,
  notas text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- tipos simples (no enum para evitar migraciones dolorosas)
ALTER TABLE public.proveedores
  ADD CONSTRAINT proveedores_tipo_check
  CHECK (tipo::text = ANY (ARRAY[
    'SaaS','HOSTING','ADS','ASESORIA','HARDWARE','VIAJES','FORMACION','OTRO'
  ]::text[]));

CREATE INDEX IF NOT EXISTS idx_proveedores_nombre ON public.proveedores USING btree (nombre);

COMMIT;
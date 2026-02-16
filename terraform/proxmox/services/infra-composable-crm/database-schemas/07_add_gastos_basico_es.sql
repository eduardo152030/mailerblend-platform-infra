BEGIN;

CREATE TABLE IF NOT EXISTS public.gastos (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- fechas
  fecha_gasto date NOT NULL,
  fecha_vencimiento date,

  -- proveedor
  proveedor_id uuid REFERENCES public.proveedores(id) ON DELETE SET NULL,
  proveedor_nombre text, -- snapshot / fallback rápido

  -- contenido
  concepto text NOT NULL,
  categoria varchar(50) NOT NULL DEFAULT 'OTRO',

  -- importes (España)
  base_imponible numeric(12,2) NOT NULL DEFAULT 0,
  iva_porcentaje numeric(5,2) NOT NULL DEFAULT 21,
  iva_importe numeric(12,2),
  total numeric(12,2),

  currency varchar(3) NOT NULL DEFAULT 'EUR',

  -- control
  estado varchar(20) NOT NULL DEFAULT 'PAGADO',
  metodo_pago varchar(30) DEFAULT 'Transferencia',

  -- referencia fiscal
  numero_factura text,
  adjunto_url text,

  -- notas
  notas text,
  internal_notes text,

  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.gastos
  ADD CONSTRAINT gastos_categoria_check
  CHECK (categoria::text = ANY (ARRAY[
    'ADS','SaaS','HOSTING','ASESORIA','HARDWARE','VIAJES','FORMACION','OTRO'
  ]::text[]));

ALTER TABLE public.gastos
  ADD CONSTRAINT gastos_estado_check
  CHECK (estado::text = ANY (ARRAY['PENDIENTE','PAGADO','ANULADO']::text[]));

ALTER TABLE public.gastos
  ADD CONSTRAINT gastos_currency_check
  CHECK (currency::text = ANY (ARRAY['EUR','USD']::text[]));

ALTER TABLE public.gastos
  ADD CONSTRAINT gastos_metodo_pago_check
  CHECK (metodo_pago IS NULL OR metodo_pago::text = ANY (ARRAY[
    'Transferencia','Tarjeta','Efectivo','PayPal','Stripe','Otro'
  ]::text[]));

CREATE INDEX IF NOT EXISTS idx_gastos_fecha ON public.gastos USING btree (fecha_gasto DESC);
CREATE INDEX IF NOT EXISTS idx_gastos_categoria ON public.gastos USING btree (categoria);
CREATE INDEX IF NOT EXISTS idx_gastos_estado ON public.gastos USING btree (estado);
CREATE INDEX IF NOT EXISTS idx_gastos_proveedor ON public.gastos USING btree (proveedor_id);

COMMIT;

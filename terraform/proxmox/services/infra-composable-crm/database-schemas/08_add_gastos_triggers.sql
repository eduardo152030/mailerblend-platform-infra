BEGIN;

-- 1) Calc IVA + total
CREATE OR REPLACE FUNCTION public.crm_calc_gasto_totales()
RETURNS trigger AS $$
DECLARE
  v_base numeric(12,2);
  v_iva_pct numeric(5,2);
  v_iva numeric(12,2);
  v_total numeric(12,2);
BEGIN
  v_base := COALESCE(NEW.base_imponible, 0);
  v_iva_pct := COALESCE(NEW.iva_porcentaje, 0);

  v_iva := ROUND(v_base * (v_iva_pct / 100.0), 2);
  v_total := ROUND(v_base + v_iva, 2);

  NEW.iva_importe := v_iva;
  NEW.total := v_total;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_gastos_calc_totales ON public.gastos;
CREATE TRIGGER trg_gastos_calc_totales
BEFORE INSERT OR UPDATE OF base_imponible, iva_porcentaje
ON public.gastos
FOR EACH ROW
EXECUTE FUNCTION public.crm_calc_gasto_totales();


-- 2) updated_at
CREATE OR REPLACE FUNCTION public.crm_set_updated_at()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_gastos_set_updated_at ON public.gastos;
CREATE TRIGGER trg_gastos_set_updated_at
BEFORE UPDATE ON public.gastos
FOR EACH ROW
EXECUTE FUNCTION public.crm_set_updated_at();

DROP TRIGGER IF EXISTS trg_proveedores_set_updated_at ON public.proveedores;
CREATE TRIGGER trg_proveedores_set_updated_at
BEFORE UPDATE ON public.proveedores
FOR EACH ROW
EXECUTE FUNCTION public.crm_set_updated_at();

COMMIT;

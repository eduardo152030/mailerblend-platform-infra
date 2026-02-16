-- 05_add_updated_at_presupuestos.sql
-- Micro-migración segura: añade updated_at + trigger para mantenerlo en UPDATE.
-- No rompe inserts: updated_at por defecto = now().

BEGIN;

-- 1) columna updated_at (idempotente)
ALTER TABLE presupuestos
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- 2) función trigger (idempotente / replace)
CREATE OR REPLACE FUNCTION crm_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3) trigger BEFORE UPDATE (idempotente)
DROP TRIGGER IF EXISTS trg_presupuestos_set_updated_at ON presupuestos;

CREATE TRIGGER trg_presupuestos_set_updated_at
BEFORE UPDATE ON presupuestos
FOR EACH ROW
EXECUTE FUNCTION crm_set_updated_at();

-- 4) backfill para filas existentes (por si ya había datos)
UPDATE presupuestos
SET updated_at = COALESCE(updated_at, created_at, NOW())
WHERE updated_at IS NULL;

-- 5) index útil para grids “última modificación”
CREATE INDEX IF NOT EXISTS idx_presupuestos_updated_at
  ON presupuestos (updated_at DESC);

COMMIT;

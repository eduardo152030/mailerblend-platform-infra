import importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import yaml
ROOT=Path(__file__).resolve().parents[2]
s=importlib.util.spec_from_file_location('report',ROOT/'scripts/report-approved-rollout.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class ReportingTests(unittest.TestCase):
 def test_repeated_update_preserves_section_boundaries_and_inherited_items(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);home=root/'home';(home/'.local/share/mailerblend-recovery/phase4/integration-20261102T000000Z').mkdir(parents=True)
   (root/'docs/roadmap/evidence').mkdir(parents=True);(root/'services/common').mkdir(parents=True)
   (root/'services/common/exporter-migration.yml').write_text(yaml.safe_dump({'telegram_chain_verified':[],'exporters_validated':{}}));(root/'services/common/phase4-images.json').write_text('{}')
   (root/'docs/roadmap/CURRENT-STATUS.md').write_text('# Estado\nActualizado: fecha vieja y variable\n\nPrometheus recoge 17 Node +17 cAdvisor: fuentes\nexplícitamente no verificados.\n\n## Siguiente paso concreto\nviejo\n## Hitos conservados\nUAT Waiver sigue\n## Pendientes heredados\nINC-005 preservado\n')
   (root/'docs/roadmap/ROADMAP.md').write_text('# Roadmap\n')
   with patch.object(m,'ROOT',root),patch.object(m.Path,'home',return_value=home):m.update('integration-20261102T000000Z');m.update('integration-20261102T000000Z')
   text=(root/'docs/roadmap/CURRENT-STATUS.md').read_text();self.assertEqual(text.count('## Siguiente paso concreto'),1);self.assertEqual(text.count('## Hitos conservados'),1);self.assertIn('UAT Waiver sigue',text);self.assertIn('INC-005 preservado',text)

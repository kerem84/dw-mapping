import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from validate_mapping_data import validate_rows  # noqa: E402


class ValidateMappingDataTests(unittest.TestCase):
    def test_valid_rows_pass(self):
        rows = [
            {
                "source_system": "PostgreSQL",
                "source_system_short": "KEY",
                "source_db": "keydb",
                "source_schema": "public",
                "source_table": "kazalar",
                "master_detail": "Master",
                "target_schema": "DWH",
                "source_attribute": "id",
                "target_physical_name": "f_kaza",
                "target_logical_name": "Kaza",
                "target_attribute": "kaza_id",
                "schema_code": "KEY_KS001",
                "modul": "KEY",
                "kullanim_senaryosu": "KS_001",
                "senaryo_adimi": "Kaza-Risk",
            },
            {
                "source_system": "PostgreSQL",
                "source_system_short": "KEY",
                "source_db": "keydb",
                "source_schema": "public",
                "source_table": "kazalar",
                "master_detail": "",
                "target_schema": "",
                "source_attribute": "kazatarihi",
                "target_physical_name": "f_kaza",
                "target_logical_name": "",
                "target_attribute": "kaza_tarihi",
                "schema_code": "KEY_KS001",
                "modul": "KEY",
                "kullanim_senaryosu": "KS_001",
                "senaryo_adimi": "Kaza-Risk",
            },
        ]
        self.assertEqual(validate_rows(rows), [])

    def test_invalid_prefix_and_master_rules_fail(self):
        rows = [
            {
                "source_system": "PostgreSQL",
                "source_system_short": "KEY",
                "source_db": "keydb",
                "source_schema": "public",
                "source_table": "kazalar",
                "master_detail": "",
                "target_schema": "",
                "source_attribute": "id",
                "target_physical_name": "fact_kaza",
                "target_logical_name": "",
                "target_attribute": "KazaID",
                "schema_code": "KEY001",
                "modul": "KEY",
                "kullanim_senaryosu": "KS1",
                "senaryo_adimi": "Kaza-Risk",
            }
        ]
        errors = validate_rows(rows)
        self.assertTrue(any("f_/d_/b_" in e for e in errors))
        self.assertTrue(any("master_detail='Master'" in e for e in errors))
        self.assertTrue(any("target_schema='DWH'" in e for e in errors))


if __name__ == "__main__":
    unittest.main()

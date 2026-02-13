import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DW_MAP_CLI = ROOT / "scripts" / "dwmap.py"


def valid_rows():
    return [
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


class DwMapCliIntegrationTests(unittest.TestCase):
    def test_validate_json_success(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            input_json = tmp / "mapping_data.json"
            input_json.write_text(json.dumps(valid_rows(), ensure_ascii=True), encoding="utf-8")

            proc = subprocess.run(
                [sys.executable, str(DW_MAP_CLI), "validate-json", "--input", str(input_json)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("Validation OK", proc.stdout)

    def test_run_generates_all_outputs(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            input_json = tmp / "mapping_data.json"
            out_dir = tmp / "out"
            input_json.write_text(json.dumps(valid_rows(), ensure_ascii=True), encoding="utf-8")

            proc = subprocess.run(
                [
                    sys.executable,
                    str(DW_MAP_CLI),
                    "run",
                    "--input",
                    str(input_json),
                    "--module",
                    "KEY",
                    "--output-dir",
                    str(out_dir),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertTrue((out_dir / "Attribute_Level_Mapping.xlsx").exists())
            self.assertTrue((out_dir / "Entity_Level_Mapping.xlsx").exists())
            self.assertTrue((out_dir / "mapping_validation_report.json").exists())
            self.assertTrue((out_dir / "mapping_raporu.md").exists())


if __name__ == "__main__":
    unittest.main()

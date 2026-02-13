#!/usr/bin/env python3
"""
mapping_data.json dogrulayici.
"""

import argparse
import json
import re
import sys
from collections import defaultdict

RE_SNAKE_LOWER = re.compile(r"^[a-z][a-z0-9_]*$")
RE_SCENARIO = re.compile(r"^KS_\d{3}$")
RE_SCHEMA_CODE = re.compile(r"^[A-Z0-9]+_KS\d{3}$")

REQUIRED_FIELDS = [
    "source_system",
    "source_system_short",
    "source_db",
    "source_schema",
    "source_table",
    "source_attribute",
    "target_physical_name",
    "target_attribute",
    "schema_code",
    "modul",
    "kullanim_senaryosu",
    "senaryo_adimi",
]


def _is_empty(value):
    return value is None or (isinstance(value, str) and value.strip() == "")


def _add_error(errors, row_no, message):
    errors.append(f"row {row_no}: {message}")


def validate_rows(rows):
    errors = []
    first_seen = {}
    groups = defaultdict(list)

    if not isinstance(rows, list):
        return ["root: JSON bir liste (array) olmali."]
    if not rows:
        return ["root: JSON bos olmamali."]

    for idx, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            _add_error(errors, idx, "satir bir obje (dict) olmali.")
            continue

        for key in REQUIRED_FIELDS:
            if _is_empty(row.get(key)):
                _add_error(errors, idx, f"'{key}' zorunlu ve bos olamaz.")

        target_phys = str(row.get("target_physical_name", "")).strip()
        target_attr = str(row.get("target_attribute", "")).strip()
        scenario = str(row.get("kullanim_senaryosu", "")).strip()
        schema_code = str(row.get("schema_code", "")).strip()

        if target_phys and not target_phys.startswith(("f_", "d_", "b_")):
            _add_error(errors, idx, "target_physical_name f_/d_/b_ ile baslamali.")
        if target_phys and not RE_SNAKE_LOWER.match(target_phys):
            _add_error(errors, idx, "target_physical_name lowercase snake_case olmali.")
        if target_attr and not RE_SNAKE_LOWER.match(target_attr):
            _add_error(errors, idx, "target_attribute lowercase snake_case olmali.")
        if scenario and not RE_SCENARIO.match(scenario):
            _add_error(errors, idx, "kullanim_senaryosu KS_001 formatinda olmali.")
        if schema_code and not RE_SCHEMA_CODE.match(schema_code):
            _add_error(errors, idx, "schema_code MODUL_KS001 formatinda olmali.")

        if target_phys:
            groups[target_phys].append((idx, row))
            if target_phys not in first_seen:
                first_seen[target_phys] = idx

    for target_phys, grouped_rows in groups.items():
        first_idx, first_row = grouped_rows[0]
        first_md = str(first_row.get("master_detail", "")).strip()
        first_schema = str(first_row.get("target_schema", "")).strip()
        first_logical = str(first_row.get("target_logical_name", "")).strip()

        if first_md != "Master":
            _add_error(errors, first_idx, f"{target_phys}: ilk satirda master_detail='Master' olmali.")
        if first_schema != "DWH":
            _add_error(errors, first_idx, f"{target_phys}: ilk satirda target_schema='DWH' olmali.")
        if not first_logical:
            _add_error(errors, first_idx, f"{target_phys}: ilk satirda target_logical_name dolu olmali.")

        for row_no, row in grouped_rows[1:]:
            md = str(row.get("master_detail", "")).strip()
            schema = str(row.get("target_schema", "")).strip()
            logical = str(row.get("target_logical_name", "")).strip()
            if md not in ("", "Detail"):
                _add_error(errors, row_no, f"{target_phys}: sonraki satirlarda master_detail bos veya 'Detail' olmali.")
            if schema:
                _add_error(errors, row_no, f"{target_phys}: sonraki satirlarda target_schema bos olmali.")
            if logical:
                _add_error(errors, row_no, f"{target_phys}: sonraki satirlarda target_logical_name bos olmali.")

    return errors


def main():
    parser = argparse.ArgumentParser(description="mapping_data.json dogrulama")
    parser.add_argument("--input", required=True, help="Girdi JSON dosyasi")
    parser.add_argument("--report", help="Opsiyonel cikti raporu (json)")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        rows = json.load(f)

    errors = validate_rows(rows)
    result = {
        "valid": len(errors) == 0,
        "error_count": len(errors),
        "errors": errors,
    }

    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=True, indent=2)

    if errors:
        print("Validation FAILED")
        for err in errors:
            print(f"- {err}")
        sys.exit(1)

    print("Validation OK")


if __name__ == "__main__":
    main()

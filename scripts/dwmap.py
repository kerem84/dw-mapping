#!/usr/bin/env python3
"""
dw-mapping icin tek giris CLI.
"""

import argparse
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def _run(script_name, *script_args):
    cmd = [sys.executable, str(SCRIPT_DIR / script_name), *script_args]
    subprocess.run(cmd, check=True)


def cmd_extract(args):
    script_args = []
    for key in ("type", "host", "port", "db", "user", "password", "connection_file", "output"):
        val = getattr(args, key, None)
        if val is None:
            continue
        flag = "--pass" if key == "password" else f"--{key.replace('_', '-')}"
        script_args.extend([flag, str(val)])
    _run("extract_metadata.py", *script_args)


def cmd_validate_json(args):
    script_args = ["--input", args.input]
    if args.report:
        script_args.extend(["--report", args.report])
    _run("validate_mapping_data.py", *script_args)


def cmd_generate(args):
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    attr_file = str(output_dir / args.attribute_output)
    entity_file = str(output_dir / args.entity_output)
    if not args.skip_validate:
        _run("validate_mapping_data.py", "--input", args.input)
    _run("generate_mapping.py", "--input", args.input, "--output", attr_file)
    _run("generate_entity_mapping.py", "--input", args.input, "--output", entity_file)


def cmd_report(args):
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_file = str(output_dir / args.report_output)
    attr_file = str(output_dir / args.attribute_output) if args.attribute_output else None
    entity_file = str(output_dir / args.entity_output) if args.entity_output else None
    validation_report = str(output_dir / args.validation_report) if args.validation_report else None

    report_args = [
        "--input",
        args.input,
        "--output",
        report_file,
        "--module",
        args.module,
    ]
    if attr_file:
        report_args.extend(["--attribute-mapping", attr_file])
    if entity_file:
        report_args.extend(["--entity-mapping", entity_file])
    if validation_report:
        report_args.extend(["--validation-report", validation_report])
    _run("build_mapping_report.py", *report_args)


def cmd_run(args):
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    attr_file = str(output_dir / args.attribute_output)
    entity_file = str(output_dir / args.entity_output)
    validation_report = str(output_dir / args.validation_report)

    if not args.skip_validate:
        _run("validate_mapping_data.py", "--input", args.input, "--report", validation_report)

    _run("generate_mapping.py", "--input", args.input, "--output", attr_file)
    _run("generate_entity_mapping.py", "--input", args.input, "--output", entity_file)
    cmd_report(args)


def build_parser():
    parser = argparse.ArgumentParser(description="dw-mapping orkestrator CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_extract = sub.add_parser("extract", help="Metadata cikar")
    p_extract.add_argument("--type", choices=["postgresql", "mssql"], help="DB tipi")
    p_extract.add_argument("--host", help="DB host")
    p_extract.add_argument("--port", type=int, help="DB port")
    p_extract.add_argument("--db", help="DB adi")
    p_extract.add_argument("--user", help="DB kullanici")
    p_extract.add_argument("--pass", dest="password", help="DB sifre")
    p_extract.add_argument("--connection-file", help="Connection dosyasi")
    p_extract.add_argument("--output", required=True, help="Metadata Excel cikti")
    p_extract.set_defaults(func=cmd_extract)

    p_validate = sub.add_parser("validate-json", help="mapping_data.json dogrula")
    p_validate.add_argument("--input", required=True, help="JSON dosyasi")
    p_validate.add_argument("--report", help="Opsiyonel validation raporu (json)")
    p_validate.set_defaults(func=cmd_validate_json)

    p_generate = sub.add_parser("generate", help="Attribute + entity mapping uret")
    p_generate.add_argument("--input", required=True, help="JSON dosyasi")
    p_generate.add_argument("--output-dir", default=".", help="Cikti dizini")
    p_generate.add_argument("--attribute-output", default="Attribute_Level_Mapping.xlsx")
    p_generate.add_argument("--entity-output", default="Entity_Level_Mapping.xlsx")
    p_generate.add_argument("--skip-validate", action="store_true", help="JSON dogrulamayi atla")
    p_generate.set_defaults(func=cmd_generate)

    p_report = sub.add_parser("report", help="Markdown ozet rapor uret")
    p_report.add_argument("--input", required=True, help="JSON dosyasi")
    p_report.add_argument("--module", required=True, help="Modul adi")
    p_report.add_argument("--output-dir", default=".", help="Cikti dizini")
    p_report.add_argument("--report-output", default="mapping_raporu.md")
    p_report.add_argument("--attribute-output", default="Attribute_Level_Mapping.xlsx")
    p_report.add_argument("--entity-output", default="Entity_Level_Mapping.xlsx")
    p_report.add_argument("--validation-report", default="mapping_validation_report.json")
    p_report.set_defaults(func=cmd_report)

    p_run = sub.add_parser("run", help="validate + generate + report")
    p_run.add_argument("--input", required=True, help="JSON dosyasi")
    p_run.add_argument("--module", required=True, help="Modul adi")
    p_run.add_argument("--output-dir", default=".", help="Cikti dizini")
    p_run.add_argument("--attribute-output", default="Attribute_Level_Mapping.xlsx")
    p_run.add_argument("--entity-output", default="Entity_Level_Mapping.xlsx")
    p_run.add_argument("--report-output", default="mapping_raporu.md")
    p_run.add_argument("--validation-report", default="mapping_validation_report.json")
    p_run.add_argument("--skip-validate", action="store_true", help="JSON dogrulamayi atla")
    p_run.set_defaults(func=cmd_run)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

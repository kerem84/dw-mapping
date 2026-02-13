#!/usr/bin/env python3
"""
mapping_data.json icin basit markdown ozet raporu uretir.
"""

import argparse
import json
from collections import Counter
from datetime import datetime, timezone


def classify_table(name):
    lower = (name or "").lower()
    if lower.startswith("f_"):
        return "fact"
    if lower.startswith("d_"):
        return "dimension"
    if lower.startswith("b_"):
        return "bridge"
    return "other"


def build_stats(rows):
    total = len(rows)
    table_types = {"fact": set(), "dimension": set(), "bridge": set(), "other": set()}
    source_systems = Counter()
    scenarios = Counter()

    for row in rows:
        table = (row.get("target_physical_name") or "").strip()
        ttype = classify_table(table)
        if table:
            table_types[ttype].add(table)

        source_system = (row.get("source_system_short") or row.get("source_system") or "").strip()
        if source_system:
            source_systems[source_system] += 1

        scenario = (row.get("kullanim_senaryosu") or "").strip()
        if scenario:
            scenarios[scenario] += 1

    return {
        "total_attributes": total,
        "fact_tables": len(table_types["fact"]),
        "dimension_tables": len(table_types["dimension"]),
        "bridge_tables": len(table_types["bridge"]),
        "other_tables": len(table_types["other"]),
        "source_systems": source_systems,
        "scenarios": scenarios,
    }


def generate_markdown(module_name, rows, artifacts):
    stats = build_stats(rows)
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        f"# {module_name} Mapping Raporu",
        "",
        f"- Uretim Zamani: {created_at}",
        f"- Toplam Attribute: {stats['total_attributes']}",
        "",
        "## Mapping Istatistikleri",
        "",
        "| Metrik | Deger |",
        "|---|---:|",
        f"| Fact tablo sayisi | {stats['fact_tables']} |",
        f"| Dimension tablo sayisi | {stats['dimension_tables']} |",
        f"| Bridge tablo sayisi | {stats['bridge_tables']} |",
        f"| Diger tablo sayisi | {stats['other_tables']} |",
        "",
        "## Kaynak Sistem Dagilimi",
        "",
        "| Kaynak Sistem | Attribute Sayisi |",
        "|---|---:|",
    ]

    for key, value in sorted(stats["source_systems"].items()):
        lines.append(f"| {key} | {value} |")

    if not stats["source_systems"]:
        lines.append("| - | 0 |")

    lines.extend(
        [
            "",
            "## Senaryo Dagilimi",
            "",
            "| Senaryo | Attribute Sayisi |",
            "|---|---:|",
        ]
    )

    for key, value in sorted(stats["scenarios"].items()):
        lines.append(f"| {key} | {value} |")

    if not stats["scenarios"]:
        lines.append("| - | 0 |")

    lines.extend(
        [
            "",
            "## Uretilen Artefaktlar",
            "",
            f"- Attribute Mapping: {artifacts.get('attribute_mapping', '-')}",
            f"- Entity Mapping: {artifacts.get('entity_mapping', '-')}",
            f"- Validation Report: {artifacts.get('validation_report', '-')}",
        ]
    )

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="mapping_data.json markdown raporu uret")
    parser.add_argument("--input", required=True, help="Girdi mapping_data.json")
    parser.add_argument("--output", required=True, help="Markdown cikti dosyasi")
    parser.add_argument("--module", required=True, help="Modul adi")
    parser.add_argument("--attribute-mapping", help="Attribute mapping dosyasi")
    parser.add_argument("--entity-mapping", help="Entity mapping dosyasi")
    parser.add_argument("--validation-report", help="Validation report dosyasi")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        rows = json.load(f)

    markdown = generate_markdown(
        module_name=args.module,
        rows=rows,
        artifacts={
            "attribute_mapping": args.attribute_mapping,
            "entity_mapping": args.entity_mapping,
            "validation_report": args.validation_report,
        },
    )
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(markdown)
    print(f"Rapor yazildi: {args.output}")


if __name__ == "__main__":
    main()

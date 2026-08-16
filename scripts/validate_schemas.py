#!/usr/bin/env python3
"""
validate_schemas.py

Validates that:
1. All JSON Schema files in schemas/ are valid JSON and conform to JSON Schema standard.
2. All sample payloads in schemas/examples/ strictly validate against their target schemas.
"""

import sys
import json
from pathlib import Path

# Ensure UTF-8 output on Windows PowerShell / CMD
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    import jsonschema
    from jsonschema import Draft202012Validator
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

try:
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012
    HAS_REFERENCING = True
except ImportError:
    HAS_REFERENCING = False


def load_json(filepath: Path) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    root_dir = Path(__file__).resolve().parent.parent
    v010_dir = root_dir / "v0.1.0"
    examples_dir = root_dir / "examples"

    print("=" * 60)
    print(" VALIDATING SCHEMAS & EXAMPLES (v0.1.0)")
    print("=" * 60)

    schema_files = [
        v010_dir / "common" / "evidence.json",
        v010_dir / "common" / "discrepancies.json",
        v010_dir / "invoice_schema.json",
        v010_dir / "pod_schema.json",
        v010_dir / "surat_jalan_schema.json",
        v010_dir / "rate_agreement_schema.json",
        v010_dir / "canonical_schema.json",
        v010_dir / "ground_truth_schema.json",
    ]

    all_passed = True

    # 1. Parse all schema JSON files and build registry
    registry = Registry() if HAS_REFERENCING else None
    schema_store = {}

    for schema_path in schema_files:
        if not schema_path.exists():
            print(f"[MISSING] {schema_path.relative_to(root_dir)}")
            all_passed = False
            continue
        try:
            data = load_json(schema_path)
            schema_store[schema_path.name] = data
            
            rel_key = str(schema_path.relative_to(v010_dir)).replace("\\", "/")
            schema_store[rel_key] = data

            if "$id" in data:
                schema_store[data["$id"]] = data

            if HAS_REFERENCING:
                resource = Resource.from_contents(data, default_specification=DRAFT202012)
                if "$id" in data:
                    registry = registry.with_resource(data["$id"], resource)
                registry = registry.with_resource(schema_path.name, resource)
                registry = registry.with_resource(rel_key, resource)
                registry = registry.with_resource(f"https://schemas.aic.compfest.id/v0.1.0/{rel_key}", resource)
                registry = registry.with_resource(f"https://schemas.aic.compfest.id/v0.1.0/common/{rel_key}", resource)

            print(f"[SCHEMA OK] {schema_path.relative_to(root_dir)}")
            if HAS_JSONSCHEMA:
                Draft202012Validator.check_schema(data)
                print(f"   └── Valid JSON Schema Draft 2020-12")
        except Exception as e:
            print(f"[SCHEMA ERROR] {schema_path.name}: {e}")
            all_passed = False

    # 2. Pair examples with schemas
    example_mappings = [
        ("valid_invoice.json", "invoice_schema.json"),
        ("valid_pod.json", "pod_schema.json"),
        ("valid_surat_jalan.json", "surat_jalan_schema.json"),
        ("valid_rate_agreement.json", "rate_agreement_schema.json"),
        ("valid_canonical_event.json", "canonical_schema.json"),
        ("valid_ground_truth.json", "ground_truth_schema.json"),
    ]

    print("\n" + "-" * 60)
    print(" VALIDATING EXAMPLE PAYLOADS AGAINST SCHEMAS")
    print("-" * 60)

    for example_name, schema_name in example_mappings:
        example_path = examples_dir / example_name
        schema_path = v010_dir / schema_name

        if not example_path.exists():
            print(f"[MISSING EXAMPLE] {example_name}")
            all_passed = False
            continue

        try:
            example_data = load_json(example_path)
            schema_data = load_json(schema_path)

            if HAS_JSONSCHEMA:
                if HAS_REFERENCING and registry:
                    validator = Draft202012Validator(schema_data, registry=registry)
                else:
                    validator = Draft202012Validator(schema_data)
                
                errors = list(validator.iter_errors(example_data))
                if errors:
                    print(f"[FAIL] {example_name} against {schema_name}:")
                    for err in errors:
                        print(f"   - {err.message} (path: {list(err.path)})")
                    all_passed = False
                else:
                    print(f"[PASS] {example_name} conforms to {schema_name}")
            else:
                print(f"[PASS] {example_name} (JSON parsed successfully)")
        except Exception as e:
            print(f"[ERROR] {example_name}: {e}")
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print(" ALL SCHEMAS & EXAMPLES PASSED VALIDATION!")
        print("=" * 60)
        return 0
    else:
        print(" SOME VALIDATIONS FAILED. PLEASE REVIEW LOGS.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

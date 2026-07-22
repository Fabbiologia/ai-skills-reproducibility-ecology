#!/usr/bin/env python3
"""Validate AI Skill Evidence Manifests and their referenced local files."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parent
SCHEMA = json.loads((ROOT / "skill-evidence.schema.json").read_text())


def validate_manifest(path: Path) -> list[str]:
    data = json.loads(path.read_text())
    errors = [f"schema: {e.message}" for e in Draft202012Validator(SCHEMA).iter_errors(data)]
    base = path.parent

    for field, relative in [("skill_file", data.get("skill_file"))]:
        if relative and not (base / relative).is_file():
            errors.append(f"{field}: missing file {relative}")

    for test in data.get("validation", {}).get("reference_tests", []):
        relative = test.get("dataset")
        if relative and not (base / relative).is_file():
            errors.append(f"reference_tests: missing dataset {relative}")

    controls = data.get("controls", {})
    if controls.get("stochastic") and not controls.get("fixed"):
        errors.append("controls: stochastic skills must declare fixed controls")

    output_names = {x.get("name") for x in data.get("contract", {}).get("outputs", [])}
    for test in data.get("validation", {}).get("reference_tests", []):
        if test.get("output") not in output_names:
            errors.append(f"reference_tests: unknown output {test.get('output')!r}")
    return sorted(errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifests", nargs="*", type=Path)
    args = parser.parse_args()
    manifests = args.manifests or sorted(ROOT.glob("examples/**/skill-evidence.json"))
    if not manifests:
        print("ERROR: no skill-evidence.json manifests found")
        return 1

    failed = False
    for manifest in manifests:
        errors = validate_manifest(manifest.resolve())
        if errors:
            failed = True
            print(f"FAIL {manifest}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {manifest}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

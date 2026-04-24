#!/usr/bin/env python3
"""
OSP manifest validator.

Validates service manifests against the core OSP schema and, for each
declared profile, against that profile's JSON Schema. Can also check
the profile registry itself for internal consistency.

Usage:
    python tools/validate.py <manifest.yaml> [<manifest.yaml> ...]
    python tools/validate.py --all examples/manifests/
    python tools/validate.py --check-registry

Resolution:
    Profile schemas are resolved from the local `profiles/` directory first
    (by convention: profiles/<name>/v<major>.schema.json, mirroring the URL
    layout). If not found and a URL is declared, the validator falls back to
    an HTTP fetch. Unknown profiles produce warnings, not errors.

Registry check:
    --check-registry validates `profiles/registry/index.json` against its
    schema, confirms every listed profile resolves to a parseable JSON
    Schema, verifies the `required_fields` hint matches the schema's real
    `required`, and flags orphan schema files in `profiles/` that are not
    listed in the registry.

Requires: PyYAML, jsonschema (>= 4.0).

Exit codes:
    0 — all checks passed
    1 — one or more checks failed
    2 — usage / setup error
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Optional, List, Tuple
from urllib.request import urlopen

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

try:
    from jsonschema import Draft7Validator
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(2)


REPO_ROOT = Path(__file__).resolve().parent.parent
CORE_SCHEMA_PATH = REPO_ROOT / "schemas" / "service-manifest.schema.json"
PROFILES_DIR = REPO_ROOT / "profiles"
REGISTRY_DIR = PROFILES_DIR / "registry"
REGISTRY_INDEX_PATH = REGISTRY_DIR / "index.json"
REGISTRY_INDEX_SCHEMA_PATH = REGISTRY_DIR / "index.schema.json"
REGISTRY_URL_PREFIX = "https://profiles.openserviceprotocol.org/"


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        data = yaml.safe_load(f)
    return data or {}


def resolve_profile_schema(profile_id: str, profile_url: Optional[str]) -> Optional[dict]:
    candidates: List[Path] = []

    if profile_url and profile_url.startswith(REGISTRY_URL_PREFIX):
        relative = profile_url[len(REGISTRY_URL_PREFIX):]
        parts = relative.split("/")
        if len(parts) == 2 and parts[1].endswith(".schema.json"):
            name = parts[0]
            version_file = parts[1]
            candidates.append(PROFILES_DIR / name / version_file)

    if profile_id.startswith("osp-"):
        stripped = profile_id[len("osp-"):]
    else:
        stripped = profile_id
    candidates.append(PROFILES_DIR / stripped / "v1.schema.json")

    for candidate in candidates:
        if candidate.exists():
            return load_json(candidate)

    if profile_url:
        try:
            with urlopen(profile_url, timeout=5) as resp:
                return json.loads(resp.read())
        except Exception:
            return None

    return None


def format_error_location(path_parts) -> str:
    parts = [str(p) for p in path_parts]
    return "/".join(parts) if parts else "<root>"


def validate_manifest(path: Path, core_schema: dict) -> Tuple[bool, List[str]]:
    messages: List[str] = []

    try:
        manifest = load_yaml(path)
    except yaml.YAMLError as e:
        return False, [f"  YAML parse error: {e}"]

    validator = Draft7Validator(core_schema)
    errors = sorted(validator.iter_errors(manifest), key=lambda e: list(e.path))
    if errors:
        for err in errors:
            loc = format_error_location(err.path)
            messages.append(f"  core:{loc}: {err.message}")
        return False, messages

    service = manifest.get("service", {})
    declared_profiles = {p["id"]: p for p in service.get("profiles", [])}
    attributes = service.get("evaluation", {}).get("attributes", {}) or {}

    for attr_id in attributes:
        if attr_id not in declared_profiles:
            messages.append(
                f"  warning: attributes block '{attr_id}' has no matching service.profiles entry"
            )

    all_valid = True
    for profile_id, declaration in declared_profiles.items():
        profile_schema = resolve_profile_schema(profile_id, declaration.get("url"))
        if profile_schema is None:
            messages.append(
                f"  warning: profile '{profile_id}' not resolvable "
                f"(no local copy found; URL fetch failed or not provided)"
            )
            continue

        attr_block = attributes.get(profile_id)
        if attr_block is None:
            messages.append(
                f"  info: profile '{profile_id}' declared but no attributes block present"
            )
            continue

        profile_validator = Draft7Validator(profile_schema)
        profile_errors = sorted(
            profile_validator.iter_errors(attr_block),
            key=lambda e: list(e.path),
        )
        if profile_errors:
            all_valid = False
            for err in profile_errors:
                loc = format_error_location(err.path)
                messages.append(f"  profile {profile_id}:{loc}: {err.message}")

    return all_valid, messages


def check_registry() -> Tuple[bool, List[str]]:
    messages: List[str] = []
    ok = True

    try:
        index = load_json(REGISTRY_INDEX_PATH)
    except FileNotFoundError:
        return False, [f"  registry index not found at {REGISTRY_INDEX_PATH}"]
    except json.JSONDecodeError as e:
        return False, [f"  registry index is not valid JSON: {e}"]

    try:
        index_schema = load_json(REGISTRY_INDEX_SCHEMA_PATH)
    except FileNotFoundError:
        return False, [f"  registry index schema not found at {REGISTRY_INDEX_SCHEMA_PATH}"]

    index_errors = sorted(
        Draft7Validator(index_schema).iter_errors(index),
        key=lambda e: list(e.path),
    )
    if index_errors:
        for err in index_errors:
            loc = format_error_location(err.path)
            messages.append(f"  index:{loc}: {err.message}")
        return False, messages
    messages.append("  [OK] registry index structure")

    listed_files = set()
    for profile in index.get("profiles", []):
        pid = profile.get("id", "?")
        for version in profile.get("versions", []):
            v = version.get("version", "?")
            schema_url = version.get("schema_url")

            if schema_url and schema_url.startswith(REGISTRY_URL_PREFIX):
                relative = schema_url[len(REGISTRY_URL_PREFIX):]
                parts = relative.split("/")
                if len(parts) == 2:
                    expected_local = PROFILES_DIR / parts[0] / parts[1]
                    if expected_local.exists():
                        listed_files.add(expected_local.resolve())

            schema = resolve_profile_schema(pid, schema_url)
            if schema is None:
                messages.append(f"  [FAIL] {pid} {v}: schema not resolvable ({schema_url})")
                ok = False
                continue

            try:
                Draft7Validator.check_schema(schema)
            except Exception as e:
                messages.append(f"  [FAIL] {pid} {v}: schema is not valid JSON Schema: {e}")
                ok = False
                continue

            declared_required = set(version.get("required_fields", []))
            actual_required = set(schema.get("required", []))
            if declared_required != actual_required:
                only_index = declared_required - actual_required
                only_schema = actual_required - declared_required
                detail = []
                if only_index:
                    detail.append(f"in index only: {sorted(only_index)}")
                if only_schema:
                    detail.append(f"in schema only: {sorted(only_schema)}")
                messages.append(
                    f"  [FAIL] {pid} {v}: required_fields mismatch ({'; '.join(detail)})"
                )
                ok = False
                continue

            messages.append(f"  [OK] {pid} {v}")

    local_schemas = {p.resolve() for p in PROFILES_DIR.glob("*/v*.schema.json") if p.parent.name != "registry"}
    orphans = local_schemas - listed_files
    if orphans:
        ok = False
        for orphan in sorted(orphans):
            messages.append(f"  [FAIL] orphan schema not listed in registry: {orphan.relative_to(REPO_ROOT)}")
    else:
        messages.append(f"  [OK] no orphan schemas in profiles/")

    return ok, messages


def collect_files(paths: List[str], recurse_dirs: bool) -> List[Path]:
    files: List[Path] = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            if recurse_dirs:
                files.extend(sorted(path.rglob("*.yaml")))
            else:
                print(f"ERROR: {p} is a directory; use --all to recurse", file=sys.stderr)
                sys.exit(2)
        elif path.is_file():
            files.append(path)
        else:
            print(f"ERROR: {p} not found", file=sys.stderr)
            sys.exit(2)
    return files


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate OSP service manifests against core schema and declared profiles.",
    )
    parser.add_argument("paths", nargs="*", help="Manifest YAML files or directories")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Recursively validate all *.yaml in the given directories",
    )
    parser.add_argument(
        "--check-registry",
        action="store_true",
        help="Validate the profile registry index for internal consistency",
    )
    args = parser.parse_args()

    if not args.paths and not args.check_registry:
        parser.error("provide manifest paths, or use --check-registry")

    total_failures = 0

    if args.check_registry:
        ok, messages = check_registry()
        status = "OK" if ok else "FAIL"
        print(f"[{status}] registry check")
        for msg in messages:
            print(msg)
        if not ok:
            total_failures += 1

    if args.paths:
        try:
            core_schema = load_json(CORE_SCHEMA_PATH)
        except FileNotFoundError:
            print(f"ERROR: core schema not found at {CORE_SCHEMA_PATH}", file=sys.stderr)
            sys.exit(2)

        files = collect_files(args.paths, recurse_dirs=args.all)
        if not files:
            print("No manifest files found.", file=sys.stderr)
            sys.exit(2)

        manifest_failures = 0
        for path in files:
            valid, messages = validate_manifest(path, core_schema)
            status = "OK" if valid else "FAIL"
            display = path.relative_to(REPO_ROOT) if path.is_absolute() and str(path).startswith(str(REPO_ROOT)) else path
            print(f"[{status}] {display}")
            for msg in messages:
                print(msg)
            if not valid:
                manifest_failures += 1

        total = len(files)
        if manifest_failures:
            print(f"\n{manifest_failures} of {total} manifests failed validation.", file=sys.stderr)
            total_failures += manifest_failures
        else:
            print(f"\nAll {total} manifests valid.")

    if total_failures:
        sys.exit(1)


if __name__ == "__main__":
    main()

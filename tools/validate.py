#!/usr/bin/env python3
"""
OSP manifest validator.

Validates a service manifest against the core OSP schema and, for each
declared profile, against that profile's JSON Schema.

Usage:
    python tools/validate.py <manifest.yaml> [<manifest.yaml> ...]
    python tools/validate.py --all examples/manifests/

Resolution:
    Profile schemas are resolved from the local `profiles/` directory first
    (by convention: profiles/<name>-v<major>.schema.json). If not found and a
    URL is declared, the validator falls back to an HTTP fetch. Unknown
    profiles produce warnings, not errors.

Requires: PyYAML, jsonschema (>= 4.0).

Exit codes:
    0 — all manifests valid
    1 — one or more manifests failed validation
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
            version_tag = parts[1].replace(".schema.json", "")
            candidates.append(PROFILES_DIR / f"{name}-{version_tag}.schema.json")

    if profile_id.startswith("osp-"):
        stripped = profile_id[len("osp-"):]
    else:
        stripped = profile_id
    candidates.append(PROFILES_DIR / f"{stripped}-v1.schema.json")

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
    parser.add_argument("paths", nargs="+", help="Manifest YAML files or directories")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Recursively validate all *.yaml in the given directories",
    )
    args = parser.parse_args()

    try:
        core_schema = load_json(CORE_SCHEMA_PATH)
    except FileNotFoundError:
        print(f"ERROR: core schema not found at {CORE_SCHEMA_PATH}", file=sys.stderr)
        sys.exit(2)

    files = collect_files(args.paths, recurse_dirs=args.all)
    if not files:
        print("No manifest files found.", file=sys.stderr)
        sys.exit(2)

    failed = 0
    for path in files:
        valid, messages = validate_manifest(path, core_schema)
        status = "OK" if valid else "FAIL"
        print(f"[{status}] {path.relative_to(REPO_ROOT) if path.is_absolute() and str(path).startswith(str(REPO_ROOT)) else path}")
        for msg in messages:
            print(msg)
        if not valid:
            failed += 1

    total = len(files)
    if failed:
        print(f"\n{failed} of {total} manifests failed validation.", file=sys.stderr)
        sys.exit(1)
    print(f"\nAll {total} manifests valid.")


if __name__ == "__main__":
    main()

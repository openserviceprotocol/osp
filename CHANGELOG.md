# Changelog

All notable changes to the OSP specification and tooling will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- GitHub Actions workflow (`.github/workflows/validate.yml`) — runs the validator against all example manifests and the profile registry on every push and pull request to `main`.
- `--check-registry` mode in `tools/validate.py` — validates the registry index against its schema, verifies every listed profile schema resolves and parses as valid JSON Schema, cross-checks `required_fields` hints, and flags orphan profile schemas not listed in the registry.
- `profiles/registry/profiles.txt` — llms.txt-style Markdown summary of the profile registry for LLM-friendly discovery.

### Changed

- RFC-001 status updated to Accepted (implemented in OSP v0.2).

## [0.2.0] — 2026-04-24

### Added

- **Domain profiles** — a mechanism for branch-specific vocabularies validated against community-maintained JSON Schemas. See `spec/profiles.md`.
- `service.profiles` field in manifests — declares conformance to one or more profiles.
- `service.evaluation.attributes` field — profile-scoped attributes namespaced by profile id.
- Seven pilot profiles in `profiles/`: logistics-general, cold-chain-logistics, consulting, it-managed-services, legal-advisory, energy-supply, cleaning-services.
- Profile registry under `profiles/registry/` with `index.json` and its schema. Hosted at `profiles.openserviceprotocol.org`.
- `spec/profiles.md` — full specification of the profile mechanism, agent behaviour, registry structure.
- Three additional example manifests (legal, energy, cleaning) demonstrating the new profiles.
- `tools/validate.py` — manifest validator that also fetches and validates against declared profile schemas.
- RFC document `proposals/001-profiles-and-attributes.md`.

### Changed

- `schemas/service-manifest.schema.json` accepts `osp_version: "0.1"` and `"0.2"`.
- Canonical example manifests (`ltl-transport`, `market-entry`, `managed-hosting`) migrated to v0.2 with profile declarations; previously ad-hoc domain fields moved into profile attributes.
- `spec/service-manifest-reference.md` status bumped to Draft v0.2, with sections added for profiles and attributes.
- Relaxed `service.identity.id` pattern to allow hyphens in the first two segments (e.g., `ewz-plus.electricity.sme-green`). Backwards-compatible: all v0.1 IDs continue to match.

### Backwards compatibility

- v0.1 manifests remain valid under v0.2 — all additions are optional.

## [0.1.0] — 2026-03-19

### Added

- Layer 1: Discovery specification (`spec/discovery.md`)
- Service Manifest Reference with all six sections (`spec/service-manifest-reference.md`)
- JSON Schema for `osp.md` validation (`schemas/osp-md.schema.json`)
- JSON Schema for service manifest validation (`schemas/service-manifest.schema.json`)
- Three example `osp.md` files (logistics, consulting, IT services)
- Three complete service manifests (LTL transport, market entry strategy, managed hosting)
- Repository setup with contribution guidelines, code of conduct, issue templates

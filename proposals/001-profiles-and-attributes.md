# RFC-001: Domain Profiles and Attributes

- **Status:** Accepted — implemented in OSP v0.2 (2026-04-24)
- **Target:** OSP v0.2
- **Relates to:** `spec/service-manifest-reference.md`, `schemas/service-manifest.schema.json`
- **Implemented by:** `spec/profiles.md`, `profiles/`, `profiles/registry/`, `tools/validate.py`

> This RFC is retained as a historical record. The specification itself lives in [`spec/profiles.md`](../spec/profiles.md); the schema changes are in `schemas/service-manifest.schema.json`; the pilot profiles are published under `profiles/`. Registry hosting at `profiles.openserviceprotocol.org` is pending website deployment.

## Problem

OSP v0.1 standardises a strong generic skeleton (identity, evaluation, contract, delivery, governance, lifecycle) and covers parameters that are common across industries: geography, lead time, pricing model, SLA response time, certifications.

What it does **not** standardise is the long tail of parameters that are decisive *within* a branch:

- Cold-chain logistics: temperature range, monitoring resolution, excursion policy, MKT reporting.
- Legal advisory: jurisdictions, bar admissions, matter types, privilege handling.
- Energy supply: supply mix, carbon intensity per kWh, balancing group, green certification.
- Cleaning services: surface types, biocide class, frequency, access model.

Today providers can put these under `evaluation.capacity` (which has `additionalProperties: true`) or invent ad-hoc fields. Two consequences:

1. **No shared vocabulary per branch.** Two pharma logistics providers may write `temperature_target` vs. `temp_celsius` — semantically identical, mechanically uncomparable.
2. **No discoverability.** An agent receiving an unknown field has no way to look up what it means, what units it uses, or which values are valid.

Without a fix, OSP ranks services only on the generic axes and ignores what actually differentiates offers within a branch. The standard's utility for real agent-side selection stays shallow.

## Proposal

Introduce two additive concepts. Both are backwards-compatible — existing v0.1 manifests remain valid.

### 1. `service.profiles` — conformance declaration

A new optional array at the `service` level that declares which domain profiles the manifest conforms to, each with a resolvable schema URL.

```yaml
service:
  profiles:
    - id: "osp-cold-chain-logistics"
      version: "1.0.0"
      url: "https://profiles.openserviceprotocol.org/cold-chain-logistics/v1.schema.json"
```

### 2. `service.evaluation.attributes` — profile-scoped fields

A new optional object under `evaluation`, keyed by profile id. Each value is validated against the corresponding profile schema.

```yaml
service:
  evaluation:
    capacity:             # unchanged: "how much"
      min_pallets: 5
      max_pallets: 15
    attributes:           # new: profile-validated domain fields
      osp-cold-chain-logistics:
        temperature_range_celsius: [2, 8]
        temperature_precision_celsius: 0.5
        temperature_logging: "continuous"
        excursion_policy: "auto-quarantine"
        qualifications: ["GDP", "USP_1079"]
```

Namespacing by profile id prevents field-name collisions between profiles (a `frequency` field means different things for cleaning and for energy).

### Scope boundary: `capacity` vs. `attributes`

- `capacity` — keep for *quantitative* "how much can this service handle" (counts, weights, parallel engagements). Still free-form.
- `attributes` — for *qualitative / branch-specific* fields that decide fit. Validated against a declared profile.

The split is a convention, not a hard rule. Providers who find the distinction unhelpful can keep using `capacity`; they just forgo cross-provider comparability.

## Profile Definition

A profile is a published JSON Schema describing the shape of one namespace under `attributes`. Minimum requirements:

- Stable `$id` (URL under which the schema is served).
- Semver `version` embedded in the URL path (`/v1`, `/v2`).
- `title`, `description`, and field-level `description` on every property.
- Explicit `required` for fields that must be present for the profile to be meaningful.
- Enums wherever an agent would otherwise have to do fuzzy matching.

See `proposals/profiles/cold-chain-logistics-v1.schema.json` for a worked example.

### Governance

Profiles are maintained by branch communities, not by the OSP core. The OSP project operates a **hosted registry at `profiles.openserviceprotocol.org`**, surfaced through the OSP website so that:

- Businesses and agents can browse existing profiles by branch without entering Git.
- Third parties (e.g., distll.io) can link to, or embed, the profile catalog directly.
- Each profile has a stable, resolvable schema URL for machine use.

The registry lists known profiles, maintainers, status (draft / active / deprecated), and version history. Review criteria apply for inclusion in the registry, not for using profiles — anyone is free to publish a profile under their own domain and reference it from a manifest. The registry is curation, not gatekeeping.

This keeps the OSP core small and lets branches evolve vocabularies at their own pace.

### Pilot Profiles

The first four pilot profiles stress the abstraction across distinct branch types:

| Profile | Domain focus |
|---|---|
| `osp-cold-chain-logistics` | Temperature-controlled transport (pharma, food, chemicals) |
| `osp-legal-advisory` | Legal services — jurisdictions, practice areas, privilege |
| `osp-energy-supply` | Energy retail — supply mix, carbon intensity, tariff model |
| `osp-cleaning-services` | Facility cleaning — service types, specializations, access model |

Draft schemas live under `proposals/profiles/` until the registry goes live.

## Agent Semantics

Specified behaviour for agents reading a manifest:

1. **Unknown profile** (id not recognised, URL not resolvable, version too new): ignore the corresponding `attributes.<id>` block. Do not fail. The manifest's generic fields stay usable.
2. **Known profile**: validate `attributes.<id>` against the profile schema. A failed validation should be treated as a provider bug — prefer to skip the offer rather than act on invalid data.
3. **Missing profile but attributes present**: treat as an undeclared extension. Agents MAY use the data at their own risk; validators SHOULD warn.
4. **Comparison**: agents rank within a profile namespace. A cold-chain agent comparing two providers should require both to declare `osp-cold-chain-logistics` before comparing their temperature fields.

## Schema Diff

Changes to `schemas/service-manifest.schema.json`:

```jsonc
// Under service.properties, add:
"profiles": {
  "type": "array",
  "description": "Domain profiles this manifest conforms to.",
  "items": {
    "type": "object",
    "required": ["id", "version"],
    "properties": {
      "id": {
        "type": "string",
        "pattern": "^[a-z][a-z0-9-]*$",
        "description": "Profile identifier (kebab-case)."
      },
      "version": {
        "type": "string",
        "pattern": "^\\d+\\.\\d+\\.\\d+$"
      },
      "url": {
        "type": "string",
        "format": "uri",
        "description": "Resolvable JSON Schema URL for the profile."
      }
    }
  }
}

// Under service.evaluation.properties, add:
"attributes": {
  "type": "object",
  "description": "Profile-scoped, domain-specific attributes. Keys are profile ids declared in service.profiles; values are validated against each profile's schema.",
  "additionalProperties": {
    "type": "object"
  }
}
```

Nothing else changes. Validation of the content under each profile id happens against the profile schema, fetched separately.

Total footprint: ~30 lines in the core schema, plus per-profile schemas maintained out-of-tree.

## Osp.md Impact

Discovery is unchanged. Profile declarations live in the service manifest, not in `osp.md`. Optional follow-up: a new `## Profiles` section in `osp.md` so an agent can pre-filter providers before fetching any manifest. Out of scope for this RFC.

## Open Questions

1. **Profile composition.** Should a manifest be able to declare two overlapping profiles (e.g., `osp-cold-chain-logistics` and `osp-pharma-distribution`)? Current proposal: yes, each under its own namespace, no merging.
2. **Profile conformance levels.** Some branches may want "core" vs. "extended" conformance. Deferred; can be expressed inside each profile schema if needed.
3. **Profile extensions to `contract` / `delivery`.** v0.2 scope limits profiles to `evaluation.attributes`. Extending to input/output field definitions is a natural v0.3 question.
4. ~~**Registry hosting.**~~ Decided: hosted at `profiles.openserviceprotocol.org`, surfaced via the OSP website. Embeddable by third parties.

## Migration

- v0.1 manifests remain valid under v0.2.
- New `profiles` / `attributes` fields are optional.
- Providers with domain-specific fields in `capacity` can migrate them into `attributes.<profile-id>` once a suitable profile exists; no deadline.

## Appendix A: Registry URL Structure

The hosted registry at `profiles.openserviceprotocol.org` exposes a stable URL layout so that manifests, validators, and third-party embeds can reference profiles predictably.

| Purpose | URL pattern | Example |
|---|---|---|
| Registry index (machine) | `/registry/index.json` | `https://profiles.openserviceprotocol.org/registry/index.json` |
| Registry index schema | `/registry/index.schema.json` | `https://profiles.openserviceprotocol.org/registry/index.schema.json` |
| Profile schema | `/{profile-id}/v{major}.schema.json` | `https://profiles.openserviceprotocol.org/cold-chain-logistics/v1.schema.json` |
| Human profile page | `openserviceprotocol.org/profiles/{profile-id}/v{major}` | `https://openserviceprotocol.org/profiles/cold-chain-logistics/v1` |

**Stability guarantees.** Once published, a profile schema URL MUST remain resolvable and byte-stable. Breaking changes are published under a new major version (`/v2.schema.json`); the old URL keeps serving the original schema. Deprecation is signalled in the registry index, not by removing the file.

**Index freshness.** The index is regenerated from the source profiles on every registry change. Consumers SHOULD cache with a short TTL (e.g., 1 hour) and are encouraged to honour `ETag`/`Last-Modified` headers.

**Third-party embedding.** `index.json` is CORS-enabled for GET. A consumer like distll.io fetches once, filters by `domain`/`tags`/`status`, and renders its own UI. The schema URLs in the index are what that consumer should link to or resolve for manifest validation.

**Publishing outside the registry.** Providers and communities MAY publish profiles under their own domains without being in the registry; manifests referencing such URLs remain valid OSP. The registry is curation for discovery, not a validity gate.

# OSP Profiles

**Status: Draft v0.2**

## Purpose

OSP's core schema standardises what is common to all services: identity, generic evaluation parameters (geography, performance, pricing, SLA), contracting, delivery, governance. It deliberately does not standardise the parameters that matter *within* a branch — cold-chain temperature range, legal jurisdiction, energy supply mix, cleaning-service specialization.

Profiles fill that gap. A profile is a versioned, community-maintained JSON Schema that defines the vocabulary for a specific branch. A manifest declares the profiles it conforms to, and the fields populated under those profiles can be compared across providers the same way generic fields can.

Without profiles, the standard covers every industry at the surface level and none in the depth that actually drives selection. With them, the depth is delegated to the branches themselves, and the core stays small.

---

## How a manifest uses profiles

```yaml
osp_version: "0.2"

service:
  identity:
    id: "translog.transport.ltl"
    # ...

  profiles:
    - id: "osp-logistics-general"
      version: "1.0.0"
      url: "https://profiles.openserviceprotocol.org/logistics-general/v1.schema.json"
    - id: "osp-cold-chain-logistics"
      version: "1.0.0"
      url: "https://profiles.openserviceprotocol.org/cold-chain-logistics/v1.schema.json"

  evaluation:
    capacity:
      min_pallets: 5                     # still free-form, still valid
      max_pallets: 15

    attributes:
      osp-logistics-general:
        transport_modes: ["road_ltl"]
        service_scope: ["domestic", "cross_border_eu"]
        hazmat_classes: ["class_2", "class_3", "class_8"]
      osp-cold-chain-logistics:
        temperature_range_celsius: [2, 8]
        temperature_logging: "continuous"
        qualifications: ["GDP"]
```

Two concepts only:

1. **`service.profiles`** — declares conformance. An array of `{ id, version, url }`.
2. **`service.evaluation.attributes`** — namespaced by profile id. Each sub-object is validated against the profile's schema.

Namespacing prevents field-name collisions between profiles (a `frequency` field means different things for cleaning and for energy).

---

## `capacity` vs. `attributes`

Both exist in `evaluation`. The split:

- **`capacity`** — quantitative "how much can this service handle". Units are universal (kg, m³, kWh, number of parallel engagements). Still free-form: the core schema does not constrain it.
- **`attributes`** — qualitative, branch-specific vocabulary. Values only make sense inside a declared profile. Validated against that profile's schema.

Rule of thumb: if you can interpret a value without knowing the branch (e.g., `max_weight_kg: 12000`), it belongs in `capacity`. If you need branch context to interpret it (e.g., `qualifications: ["GDP"]` means nothing outside pharma logistics), it belongs in `attributes`.

The split is a convention, not a hard rule. Validators accept both.

---

## Agent behaviour

Reading a manifest:

1. **Unknown profile** (id not recognised, URL not resolvable, version too new): ignore the corresponding `attributes.<id>` block. The manifest's generic fields (geography, performance, pricing, etc.) remain usable.
2. **Known profile**: fetch the schema and validate `attributes.<id>` against it. Failed validation is a provider bug — prefer to skip the offer over acting on invalid data.
3. **Attributes present without a matching `profiles` entry**: treat as an undeclared extension. Agents MAY use the data at their own risk; validators SHOULD warn.
4. **Comparison**: agents rank within a profile namespace. Two providers are comparable on `osp-cold-chain-logistics.temperature_range_celsius` only if both declare that profile.

Agents SHOULD cache profile schemas with a reasonable TTL (15 minutes to a few hours). Profile schema URLs are byte-stable — once published, they do not change in place.

---

## Profile schemas

A profile is a JSON Schema (Draft-07) with these requirements:

- **Stable `$id`**: the canonical URL under which the schema is served. Once published, the URL and its contents MUST remain byte-stable.
- **Versioned URL**: major version embedded in the path (`/v1.schema.json`, `/v2.schema.json`). Breaking changes ship as new majors.
- **`title`, `description`**: both at schema level and on every property.
- **`required`**: list fields without which the profile is not meaningful.
- **Enums for classification fields**: wherever an agent would otherwise need fuzzy matching, use an `enum`.
- **`additionalProperties: false`**: profiles are intentionally closed. Extending a profile means cutting a new version.

A worked example is [`profiles/cold-chain-logistics-v1.schema.json`](../profiles/cold-chain-logistics-v1.schema.json).

### Versioning

Profiles follow semver:

- **Patch** (`1.0.0` → `1.0.1`): description fixes, typo corrections. No breaking change.
- **Minor** (`1.0.0` → `1.1.0`): new optional fields, new enum values. Backwards-compatible.
- **Major** (`1.0.0` → `2.0.0`): field removal, field rename, tightening of required fields or enums. Published under a new URL path.

When a major is cut, the previous major stays resolvable indefinitely. Deprecation is signalled through the registry, not by removing the file.

### Composability

A manifest may declare multiple profiles. Each is validated independently under its own namespace in `attributes`. There is no schema-level merging and no resolution of overlapping fields — a provider choosing to declare both `osp-logistics-general` and `osp-cold-chain-logistics` populates two distinct blocks.

---

## The hosted registry

OSP operates a hosted registry at **`profiles.openserviceprotocol.org`**, surfaced through the OSP website. It lets anyone browse profiles by branch, compare versions, find example manifests, and link to schemas from third-party tooling (e.g., distll.io).

### URL structure

| Purpose | URL pattern |
|---|---|
| Registry index (JSON) | `https://profiles.openserviceprotocol.org/registry/index.json` |
| Registry index schema | `https://profiles.openserviceprotocol.org/registry/index.schema.json` |
| Profile schema | `https://profiles.openserviceprotocol.org/{profile-id}/v{major}.schema.json` |
| Human profile page | `https://openserviceprotocol.org/profiles/{profile-id}/v{major}` |

### Stability guarantees

- Once published, a profile schema URL MUST remain resolvable and byte-stable.
- Breaking changes get a new major URL (`/v2.schema.json`). The old URL keeps serving the original schema.
- Deprecation is signalled in the registry index; the schema file itself is not removed.

### Index format

The registry index is a JSON document validated by [`profiles/registry/index.schema.json`](../profiles/registry/index.schema.json). Consumers fetch once, filter by `domain`/`tags`/`status`, and render or link from there. CORS-enabled for GET; ETag / Last-Modified supported for caching.

### Curation, not gatekeeping

Anyone can publish a profile schema under their own domain and reference it from a manifest — inclusion in the registry is not a validity requirement. The registry exists so agents and humans can *discover* community-maintained vocabularies without crawling the open web.

Accepting a profile into the registry requires:

- Stable URL and hosting commitment.
- Clear maintainer identity.
- Schema meets the requirements listed above.
- Doesn't duplicate an existing active profile without justification.

---

## Pilot profiles

The v0.2 launch ships with seven pilot profiles, chosen to stress the abstraction across distinct branch shapes:

| Profile | Domain |
|---|---|
| `osp-logistics-general` | General freight — transport modes, hazmat, customs, equipment |
| `osp-cold-chain-logistics` | Temperature-controlled transport (composable with `osp-logistics-general`) |
| `osp-consulting` | Strategy and advisory services |
| `osp-it-managed-services` | Managed hosting, databases, Kubernetes, SRE-on-demand |
| `osp-legal-advisory` | Legal services — jurisdictions, practice areas, privilege |
| `osp-energy-supply` | Energy retail — commodity, supply mix, tariff model |
| `osp-cleaning-services` | Facility cleaning — specializations, surfaces, access models |

Each is published at its canonical registry URL. See [`profiles/registry/index.json`](../profiles/registry/index.json) for the full index.

---

## Writing your own profile

If your branch is not covered by an existing profile, a new profile is lightweight to draft:

1. Pick a stable id (`osp-<branch-name>`) and a canonical URL.
2. Start from an existing profile schema as a template.
3. Fill in required vs. optional fields. Err toward fewer required fields — a profile that demands too much upfront is adopted by nobody.
4. Use enums for any classification field an agent would otherwise need to fuzzy-match.
5. Publish with semver and stable URLs.
6. (Optional) Propose inclusion in the hosted registry via pull request to this repository.

A profile is valuable the moment two providers in the same branch adopt it. You do not need the whole branch on board to start.

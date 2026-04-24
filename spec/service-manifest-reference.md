# Service Manifest Reference

**Status: Draft v0.2**

## Purpose

A service manifest is a YAML file that describes a single service in full, machine-readable detail. It is the document an agent reads when it needs to evaluate whether a service fits its requirements, what inputs are needed to order it, and what it can expect in return.

Service manifests are linked from the `osp.md` file and placed in an `/osp/services/` directory by convention.

---

## Schema Overview

A service manifest consists of the following top-level components:

| Section | Purpose | Required |
|---|---|---|
| **identity** | Naming, classification, when to use / not use | Yes |
| **profiles** | Domain profiles the manifest conforms to (v0.2+) | Optional |
| **evaluation** | Parameters for agent comparison and selection | Yes |
| **contract** | Input requirements, output guarantees, engagement model | Recommended |
| **delivery** | Execution mode, timelines, status tracking | Recommended |
| **governance** | Access control, compliance, data handling | Recommended |
| **lifecycle** | Version, changelog, review cycle | Optional |

Not every service needs every section at full depth. A simple lookup service can omit governance entirely. A complex consulting engagement needs all sections. The schema is a maximum format — providers fill what applies.

### What changed in v0.2

- **`service.profiles`** — declare which domain profiles (branch vocabularies) the manifest conforms to. See [spec/profiles.md](profiles.md).
- **`service.evaluation.attributes`** — profile-scoped, branch-specific fields validated against the declared profile schemas.
- **`osp_version: "0.2"`** — v0.1 manifests remain valid; upgrade is optional.

---

## Section 1: identity

Identifies the service and provides the semantic context an agent needs to decide whether this service is relevant.

```yaml
osp_version: "0.1"                     # Required. Protocol version.

service:
  identity:
    id: "string"                        # Required. Unique identifier.
                                        # Convention: domain.entity.action
                                        # Example: "translog.transport.ltl"
    
    name: "string"                      # Required. Human-readable name.
                                        # Example: "LTL Transport Europe"
    
    version: "string"                   # Required. Semver.
                                        # Example: "2.1.0"
    
    status: "string"                    # Required. One of:
                                        # active, deprecated, draft, experimental
    
    maturity: "string"                  # Recommended. Indicates how the service
                                        # is currently delivered. One of:
                                        # human, assisted, supervised, autonomous
                                        # See Maturity Levels below.
    
    summary: "string"                   # Required. 2-3 sentences describing what
                                        # the service does. An agent reading only
                                        # this field should understand the core
                                        # capability.
    
    when_to_use: "string"               # Required. Conditions under which an
                                        # agent should consider this service.
                                        # Include concrete parameters and
                                        # thresholds where possible.
    
    when_not_to_use: "string"           # Required. Conditions under which this
                                        # service is NOT appropriate. Include
                                        # concrete exclusion criteria. At least
                                        # two specific exclusions recommended.
    
    tags: ["string"]                    # Recommended. Keywords for discovery.
    
    domain: "string"                    # Optional. Business domain.
                                        # Example: "logistics", "consulting"
    
    service_family: "string"            # Optional. Groups related services.
                                        # Example: "transport"
    
    engagement_type: "string"           # Recommended. One of:
                                        # transactional — single order, defined
                                        #   inputs and outputs
                                        # consultative — scope developed in
                                        #   dialogue, multi-phase possible
                                        # continuous — ongoing service with
                                        #   recurring delivery
```

### Maturity Levels

The `maturity` field indicates how the service is currently delivered. It does NOT affect the interface — agents interact identically regardless of maturity.

| Level | Meaning |
|---|---|
| `human` | A human performs the service. The API is a facade. |
| `assisted` | AI prepares, a human decides and delivers. |
| `supervised` | AI delivers, a human reviews selectively. |
| `autonomous` | Fully automated with monitoring. |

Agents may use this field to set expectations about response times or to prefer automated services for time-critical tasks. But the field is informational, not contractual — SLAs are defined in the evaluation section.

---

## Profiles (v0.2+)

Declares the domain profiles this manifest conforms to. Profiles are versioned JSON Schemas published by branch communities. They define vocabularies that let two providers in the same branch describe themselves with the same field names, so agents can compare them.

```yaml
  profiles:
    - id: "osp-cold-chain-logistics"      # kebab-case profile id
      version: "1.0.0"                    # semver
      url: "https://profiles.openserviceprotocol.org/cold-chain-logistics/v1.schema.json"
    - id: "osp-logistics-general"
      version: "1.0.0"
      url: "https://profiles.openserviceprotocol.org/logistics-general/v1.schema.json"
```

A manifest may declare zero, one, or many profiles. Profiles are composable: a provider of temperature-controlled LTL transport declares both `osp-logistics-general` and `osp-cold-chain-logistics`, and populates fields for each under `evaluation.attributes`.

See [spec/profiles.md](profiles.md) for the full profile mechanism, agent behaviour, and the hosted registry.

---

## Section 2: evaluation

Contains the parameters an agent needs to compare this service against its requirements without placing an order. This is the section that enables agent-side filtering and ranking.

The evaluation section is intentionally flexible. Different service types need different parameters. The spec defines a set of common sub-sections, but providers can add domain-specific fields.

```yaml
  evaluation:

    # --- Capacity ---
    # Quantitative "how much can this service handle" parameters.
    # Structure varies by service type.
    capacity:
      # Example for transport:
      min_pallets: 5                    # number, optional
      max_pallets: 15                   # number, optional
      max_weight_kg: 12000              # number, optional

      # Example for consulting:
      min_engagement_days: 10           # number, optional
      max_parallel_engagements: 3       # number, optional
      team_size_range: [2, 6]           # [min, max], optional

      # Providers define fields relevant to their service.
      # Agents match against fields they understand and ignore others.

    # --- Attributes (v0.2+) ---
    # Profile-scoped, branch-specific attributes. Keys are profile ids
    # from service.profiles; values are validated against each profile's
    # schema. Use this — not 'capacity' — for qualitative domain fields
    # that only make sense within a branch vocabulary.
    attributes:
      osp-cold-chain-logistics:
        temperature_range_celsius: [2, 8]
        temperature_logging: "continuous"
        qualifications: ["GDP"]

    # --- Geography ---
    geography:
      service_regions: ["string"]       # Recommended. ISO 3166-1 alpha-2
                                        # country codes or region descriptions.
      excluded_regions: ["string"]      # Optional. Explicit exclusions.

    # --- Performance ---
    performance:
      standard_leadtime: "string"       # Recommended. Typical time from order
                                        # to delivery. Example: "48-96h"
      express_available: true           # Optional. Boolean.
      express_leadtime: "string"        # Optional. Example: "24-36h"
      
      # Quantitative track record (optional but valuable for agent ranking):
      completion_rate: 0.97             # number, 0-1. Optional.
      on_time_rate: 0.94                # number, 0-1. Optional.
      average_quality_score: 4.6        # number, scale defined by provider. Optional.
      sample_size: 4200                 # number. Basis for the above metrics. Optional.
      sample_period: "12 months"        # string. Time window. Optional.

    # --- Pricing ---
    pricing:
      model: "string"                   # Recommended. One of:
                                        # per_unit, per_hour, per_project,
                                        # per_shipment, subscription, custom
      currency: "string"                # Recommended. ISO 4217. Example: "CHF"
      
      indicative_range:                 # Recommended. Non-binding price range
                                        # for agent budgeting.
        min: 0                          # number
        max: 0                          # number
        note: "string"                  # Optional. Explains what drives the price.
      
      # Optional modifiers:
      express_surcharge: "string"       # Example: "40-60%"
      token_pricing_available: true     # Boolean. Optional.

    # --- Certifications ---
    certifications: ["string"]          # Optional. Industry certifications.
                                        # Example: ["ISO 9001", "GDP", "AEO"]

    # --- SLA ---
    sla:
      response_time: "string"           # Recommended. Time to respond to a
                                        # quote request. Example: "< 2h"
      tracking_available: true          # Optional. Boolean.
      incident_notification: "string"   # Optional. Example: "< 15 minutes"
      
      # Compensation commitments (optional):
      late_delivery_compensation: "string"  # Example: "15% per 24h delay"
      quality_guarantee: "string"           # Free text describing guarantees.

    # --- Confidence Note ---
    confidence_note: "string"           # Optional. Contextualizes the above
                                        # data. Example: "Metrics based on
                                        # 4,200 shipments over 12 months.
                                        # Indicative pricing is non-binding."
```

### Guidelines for the Evaluation Section

**Be concrete.** "Fast delivery" is useless for an agent. "48-96h standard, 24-36h express" is actionable.

**Include ranges, not just averages.** An agent that needs a guarantee cares about the worst case, not the average.

**The `confidence_note` matters.** It tells the agent how much to trust the numbers. Metrics based on 50 cases are less reliable than metrics based on 5,000. Making this explicit builds trust.

**Domain-specific fields are fine — but prefer `attributes` over `capacity` for them.** A logistics provider will have fields a consulting firm doesn't. `capacity` remains free-form for quantitative "how much" values, but for qualitative branch-specific vocabulary use `attributes` under a declared profile. That way two providers in the same branch describe themselves with the same field names and an agent can actually compare them. The common fields (geography, performance, pricing, SLA) provide the cross-branch baseline.

---

## Section 3: contract

Defines what an agent needs to provide to order the service, what it will receive in return, and what guarantees apply.

```yaml
  contract:
  
    # --- Engagement Model ---
    engagement:
      type: "string"                    # transactional | consultative | continuous
      
      # For transactional:
      quote_binding: true               # Boolean. Is the quote a firm offer?
      quote_validity: "string"          # Example: "48h"
      
      # For consultative:
      multi_phase: true                 # Boolean. Can the engagement be split?
      initial_phase_independent: true   # Boolean. Can phase 1 be ordered alone?
      scope_negotiation: "string"       # Description of how scope is developed.
      
      # For continuous:
      minimum_term: "string"            # Example: "12 months"
      notice_period: "string"           # Example: "3 months"
      individual_orders: true           # Boolean. Are there separate orders
                                        # within the framework?
    
    # --- Input Requirements ---
    input:
      required_fields:
        - name: "string"                # Field name
          type: "string"                # string | number | boolean | date |
                                        # datetime | enum | file | object | array
          description: "string"         # What this field means
          constraints: {}               # Optional. Type-specific constraints:
                                        # For string: pattern, min_length, max_length
                                        # For number: minimum, maximum
                                        # For enum: values (array of allowed values)
                                        # For file: accepted_formats, max_size_mb
                                        
      optional_fields:
        - name: "string"
          type: "string"
          description: "string"
          default: "any"                # Default value if not provided
          constraints: {}
    
    # --- Output Specification ---
    output:
      fields:
        - name: "string"               # Field name
          type: "string"               # Same types as input
          description: "string"
          
      confidence_included: true         # Boolean. Does the output include a
                                        # confidence indicator?
      
      # Example scenarios showing realistic input/output pairs:
      examples:
        - scenario: "string"            # Description of the scenario
          input: {}                     # Example input values
          output: {}                    # Example output values
    
    # --- Preconditions ---
    preconditions:
      - condition: "string"             # What must be true
        on_failure: "string"            # What happens if not true:
                                        # reject, skip, or degrade
        agent_instruction: "string"     # What the agent should do

    # --- Postconditions ---
    postconditions:
      - guarantee: "string"             # What is guaranteed after execution
```

---

## Section 4: delivery

Describes how the service is executed and how the agent tracks progress.

```yaml
  delivery:
    
    mode: "string"                      # Required. One of:
                                        # synchronous — result returned immediately
                                        # async_tracked — result delivered later,
                                        #   status tracking available
                                        # interactive — multi-step with agent
                                        #   interaction during delivery
    
    # --- For synchronous ---
    expected_duration: "string"         # Example: "< 5 seconds"
    
    # --- For async_tracked ---
    tracking:
      status_endpoint: true             # Boolean. Is a polling endpoint provided?
      webhook_support: true             # Boolean. Can the agent register a webhook?
      update_frequency: "string"        # Example: "every 30 minutes"
    
    # --- For interactive ---
    interaction:
      input_requests_possible: true     # Boolean. May the provider ask for
                                        # additional input during delivery?
      review_points: true               # Boolean. Are there intermediate
                                        # deliverables the agent must review?
      max_interactions: 0               # number. Optional. Upper bound on
                                        # interactions during delivery.
    
    # --- Status Model ---
    # All delivery modes use the same status vocabulary:
    status_values:
      - "accepted"                      # Order confirmed
      - "preparing"                     # Resources being allocated
      - "in_progress"                   # Active work
      - "review"                        # Internal quality review
      - "pending_input"                 # Waiting for agent/customer input
      - "delivered"                     # Result delivered
      - "completed"                     # Confirmed by customer
      - "disputed"                      # Issue raised
    
    # --- Human-in-the-Loop Transparency ---
    human_involvement:
      disclosed: true                   # Boolean. Does the provider disclose
                                        # when humans are involved?
      typical_touchpoints: 0            # number. Optional. Average number of
                                        # human decision points.
```

---

## Section 5: governance

Describes access control, data handling, and compliance requirements.

```yaml
  governance:
  
    # --- Access Control ---
    access:
      authentication_required: true     # Boolean.
      authorization_model: "string"     # api_key | oauth2 | token_account
      agent_registration_required: true # Boolean. Must agents register
                                        # before first use?
    
    # --- Data Handling ---
    data:
      input_sensitivity: "string"       # public | internal | confidential | restricted
      output_sensitivity: "string"      # Same values.
      pii_fields: ["string"]            # List of fields containing personal data.
      retention_period: "string"        # Example: "90 days"
      deletion_on_request: true         # Boolean. Can data be deleted on request?
    
    # --- Compliance ---
    compliance:
      regulations: ["string"]           # Applicable regulations.
                                        # Example: ["GDPR", "DSG", "GDP"]
      audit_trail: true                 # Boolean. Are all interactions logged?
      certifications: ["string"]        # Relevant certifications (can repeat
                                        # from evaluation for emphasis).
    
    # --- Agent Restrictions ---
    agent_restrictions:
      rate_limit: "string"              # Optional. Example: "100 requests/hour"
      budget_limit_enforceable: true    # Boolean. Can the provider enforce
                                        # a per-agent budget limit?
      geographic_restrictions: ["string"] # Optional. Agent must operate from
                                        # listed jurisdictions.
```

---

## Section 6: lifecycle

Version history and maintenance information.

```yaml
  lifecycle:
    created: "date"                     # ISO 8601. Example: "2026-01-15"
    last_modified: "date"               # ISO 8601.
    
    changelog:
      - version: "string"
        date: "date"
        changes: "string"
    
    deprecation:
      planned: false                    # Boolean.
      successor: "string"              # Service ID of replacement. Null if none.
      sunset_date: "date"              # When this service will be removed.
    
    review:
      next_review: "date"              # When the manifest will be reviewed.
      review_cycle: "string"           # Example: "quarterly"
```

---

## Minimal Valid Manifest

The smallest valid service manifest contains only the required fields:

```yaml
osp_version: "0.1"

service:
  identity:
    id: "example.service.basic"
    name: "Basic Example Service"
    version: "1.0.0"
    status: "active"
    summary: "A minimal service manifest demonstrating required fields only."
    when_to_use: "Use this as a template when creating your first service manifest."
    when_not_to_use: "Do not use in production. This is a documentation example."

  evaluation:
    geography:
      service_regions: ["CH", "DE", "AT"]
    performance:
      standard_leadtime: "48h"
    pricing:
      model: "per_unit"
      currency: "CHF"
      indicative_range:
        min: 100
        max: 500
```

This is enough for an agent to find, understand, and roughly evaluate the service. The provider can add sections incrementally as the integration deepens.

---

## File Naming Convention

Service manifests are placed in `/osp/services/` and named after the service:

```
/osp/services/ltl-transport.yaml
/osp/services/market-entry.yaml
/osp/services/managed-hosting.yaml
```

Use lowercase, hyphens for word separation, no spaces. The filename should be recognizable without opening the file.

---

## Token Efficiency Guidelines

Service manifests will be read by agents operating under token budgets. To keep consumption reasonable:

- Keep `summary`, `when_to_use`, and `when_not_to_use` under 100 words each
- Use concrete values instead of verbose descriptions
- Avoid repeating information across sections
- A full manifest should consume fewer than 1,500 tokens
- A minimal manifest should consume fewer than 400 tokens

Providers can verify token counts using the OSP validator tool.

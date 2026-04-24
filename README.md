# Open Service Protocol (OSP)

**An open standard for agent-first service discovery, contracting, and delivery.**

> ⚠️ **Draft specification — not yet stable.** This is an early proposal. Everything is subject to change. Feedback welcome via [Issues](../../issues) and [Discussions](../../discussions).

AI agents can read websites ([llms.txt](https://llmstxt.org/), [Cloudflare Markdown](https://developers.cloudflare.com/fundamentals/reference/markdown-for-agents/)). They can call tools ([MCP](https://modelcontextprotocol.io/), [OpenAPI](https://www.openapis.org/)). But they can't discover what a company *does*, evaluate whether it fits their needs, place an order, and receive the result — all through a single, standardized protocol.

OSP closes this gap. It defines how businesses describe their services for AI agents, how agents order those services, and how delivery works — regardless of whether the service is performed by a human, a machine, or any combination.

## Quick Start

Create an `osp.md` file in your website's root directory:

```markdown
# Your Company Name

> One-paragraph description of what you do, who you serve, 
> and what makes you relevant for an AI agent looking for 
> your type of service.

## Available Services

- [Service A](/osp/services/service-a.yaml): Brief description
- [Service B](/osp/services/service-b.yaml): Brief description

## Not Available

- Things you explicitly don't do (saves agents time)

## Conditions

- Geographic scope, minimum order, languages, response times

## Integration

- OSP Version: 0.1
```

That's it. Your business is now discoverable by AI agents.

## Why OSP?

| Standard | What it solves | What it doesn't solve |
|---|---|---|
| llms.txt | Agents can read your content | Agents can't act on it |
| MCP | Agents can call tools | No service lifecycle (order, deliver, pay) |
| OpenAPI | API endpoints are documented | No business semantics (SLAs, pricing, human steps) |
| **OSP** | **Agents can discover, evaluate, order, and receive services** | — |

OSP doesn't replace these standards. It builds on them. Service manifests link to MCP endpoints. The `osp.md` file complements `llms.txt`. Technical APIs use OpenAPI under the hood.

## Architecture

OSP has four layers. Each is independently implementable.

```
Layer 4: Settlement — billing, compensation, dispute resolution
Layer 3: Delivery   — execution, tracking, result handover
Layer 2: Contracting — quotes, orders, configuration
Layer 1: Discovery   — catalog, evaluation, comparison
```

Start with Layer 1 (a single file). Add layers as you need them.

## Specification

- **[Layer 1: Discovery](spec/discovery.md)** — the `osp.md` file format and how agents find your services
- **[Service Manifest Reference](spec/service-manifest-reference.md)** — complete YAML schema for describing a service
- **[Profiles (v0.2+)](spec/profiles.md)** — branch-specific vocabularies for attributes that matter within an industry but not across
- Layer 2: Contracting (planned)
- Layer 3: Delivery (planned)
- Layer 4: Settlement (planned)

## Schemas and Profiles

Machine-readable schemas for validation:

- **[osp-md.schema.json](schemas/osp-md.schema.json)** — validates the structure of `osp.md` files
- **[service-manifest.schema.json](schemas/service-manifest.schema.json)** — validates service manifest YAML files
- **[profiles/](profiles/)** — seven pilot domain profiles (logistics, cold-chain, consulting, IT managed services, legal, energy, cleaning)
- **[profiles/registry/index.json](profiles/registry/index.json)** — machine-readable profile registry, mirrored at `profiles.openserviceprotocol.org/registry/index.json`

## Examples

### osp.md files

Discovery files for different industries:

- **[Logistics provider](examples/logistics.osp.md)** — international transport, temperature-controlled
- **[Consulting firm](examples/consulting.osp.md)** — strategy advisory, multi-phase engagements
- **[IT service provider](examples/it-services.osp.md)** — managed cloud, continuous service

### Service manifests

Complete YAML manifests showing all schema sections, each declaring the relevant domain profiles:

- **[LTL Transport](examples/manifests/ltl-transport.yaml)** — logistics-general + cold-chain-logistics; transactional, async delivery
- **[Market Entry Strategy](examples/manifests/market-entry.yaml)** — consulting; consultative, interactive delivery
- **[Managed Cloud Hosting](examples/manifests/managed-hosting.yaml)** — IT managed services; continuous, tracked delivery
- **[Swiss Market Entry Legal Package](examples/manifests/legal-market-entry.yaml)** — legal advisory
- **[SME Green Electricity](examples/manifests/energy-sme-supply.yaml)** — energy supply
- **[Medical Cleaning Specialist](examples/manifests/cleaning-medical.yaml)** — cleaning services

These examples deliberately cover different engagement types, maturity levels, delivery modes, and branches to show the full range of the format.

## Design Principles

- **Agent-first, human-compatible.** Optimized for machines, readable by humans.
- **Progressive disclosure.** 50 tokens for a first impression. Full detail on demand.
- **Maturity-agnostic interface.** Same API whether a human or algorithm fulfills the service.
- **Build on what exists.** Markdown for readability, JSON Schema for structure, MCP for tool integration.

## Repository Structure

```
osp/
├── spec/
│   ├── discovery.md                    # Layer 1 specification
│   ├── service-manifest-reference.md   # Complete manifest schema docs
│   └── profiles.md                     # Domain profile mechanism (v0.2)
├── schemas/
│   ├── osp-md.schema.json              # JSON Schema for osp.md
│   └── service-manifest.schema.json    # JSON Schema for manifests
├── profiles/                           # Branch-specific vocabularies (v0.2)
│   ├── logistics-general-v1.schema.json
│   ├── cold-chain-logistics-v1.schema.json
│   ├── consulting-v1.schema.json
│   ├── it-managed-services-v1.schema.json
│   ├── legal-advisory-v1.schema.json
│   ├── energy-supply-v1.schema.json
│   ├── cleaning-services-v1.schema.json
│   └── registry/
│       ├── index.json                  # Machine-readable registry
│       └── index.schema.json
├── examples/
│   ├── logistics.osp.md
│   ├── consulting.osp.md
│   ├── it-services.osp.md
│   └── manifests/                      # Six full example manifests
├── proposals/                          # RFCs and drafts
│   └── 001-profiles-and-attributes.md
└── tools/
    └── validate.py                     # Manifest + profile validator
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). We welcome feedback, examples, and implementations.

The most valuable contribution right now: create an `osp.md` for your own business or industry and submit it as a pull request.

## License

- Specification: [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/)
- Code and tools: [Apache 2.0](LICENSE)

See [NOTICE](NOTICE) for details.

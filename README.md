# Open Service Protocol (OSP)

**An open standard for agent-first service discovery, contracting, and delivery.**

AI agents can read websites (llms.txt, Cloudflare Markdown). They can call tools (MCP, OpenAPI). But they can't discover what a company *does*, evaluate whether it fits their needs, place an order, and receive the result — all through a single, standardized protocol.

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

- [Layer 1: Discovery](spec/discovery.md) ← start here
- Layer 2: Contracting (draft)
- Layer 3: Delivery (draft)
- Layer 4: Settlement (draft)

## Examples

Real-world `osp.md` files for different industries:

- [Logistics provider](examples/logistics.osp.md)
- [Consulting firm](examples/consulting.osp.md)
- [IT service provider](examples/it-services.osp.md)

## Tools

- **Validator** — Check your `osp.md` against the spec: `npx osp-validate ./osp.md`
- **Token counter** — See how many tokens your service description uses

## Design Principles

- **Agent-first, human-compatible.** Optimized for machines, readable by humans.
- **Progressive disclosure.** 50 tokens for a first impression. Full detail on demand.
- **Maturity-agnostic interface.** Same API whether a human or algorithm fulfills the service.
- **Build on what exists.** Markdown for readability, JSON Schema for structure, MCP for tool integration.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). We welcome feedback, examples, and implementations.

## License

- Specification: [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/)
- Code and tools: [Apache 2.0](LICENSE)

See [NOTICE](NOTICE) for details.

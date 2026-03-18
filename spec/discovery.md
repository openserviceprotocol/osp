# OSP Layer 1: Discovery

**Status: Draft v0.1**

## Purpose

OSP Discovery makes a business's capabilities machine-readable for AI agents. An agent that needs a service — a transport, a translation, an audit, a consultation — can read a provider's `osp.md` file and determine within seconds whether the provider fits.

## The `osp.md` File

A Markdown file placed at the root of a website:

```
https://example.com/osp.md
```

It follows this structure. Only the H1 heading and the blockquote summary are required. Everything else is recommended.

### Format

```markdown
# {Company Name}

> {One-paragraph summary. What you do, who you serve, what 
> makes you distinctive. An agent reading only this paragraph 
> should know whether to continue reading.}

## Available Services

- [{Service Name}]({link to service manifest}): {One-line description}
- [{Service Name}]({link to service manifest}): {One-line description}

## Not Available

- {Services you explicitly don't offer, to save agent time}

## Conditions

- {Geographic scope}
- {Minimum order or engagement size}
- {Languages}
- {Response times}

## Integration

- OSP Version: {version}
- Contracting: {available | not yet}
- Delivery Tracking: {available | not yet}
- Settlement: {token | invoice | not yet}
- MCP Endpoint: {URL, if available}
```

### Design Rationale

**Markdown, not YAML or JSON.** The `osp.md` file is optimized for token efficiency and human readability, following the precedent set by `llms.txt`. Structured data lives in the linked service manifests.

**"Not Available" section.** Explicitly stating what you don't do is as valuable as stating what you do. It prevents agents from sending requests that will be rejected, saving time on both sides.

**Progressive disclosure.** The `osp.md` file is a summary. Detailed, machine-readable service descriptions are linked as separate YAML files. An agent that only needs a quick match reads the `osp.md` (< 300 tokens). An agent that needs full contract details follows the links.

## Service Manifests

Each service listed in `osp.md` links to a YAML manifest with the full description. Service manifests are placed in an `/osp/services/` directory by convention.

### Minimal Service Manifest

```yaml
osp_version: "0.1"
service:
  id: "{domain.entity.action}"
  name: "{Human-readable name}"
  status: "active"

  summary: "{What this service does, in 2-3 sentences}"

  when_to_use: "{When an agent should consider this service}"

  when_not_to_use: "{When an agent should NOT use this service. 
    Include concrete thresholds where applicable.}"

  evaluation:
    # Key parameters an agent needs for comparison
    # Structure varies by service type
```

### Full Service Manifest

See [Service Manifest Reference](service-manifest-reference.md) for all available fields, including pricing indicators, SLAs, certifications, and maturity information.

## Relationship to Other Standards

### llms.txt

`osp.md` can be referenced from `llms.txt`:

```markdown
## Services
- [Service Capabilities (OSP)](/osp.md): Machine-readable 
  description of available services for AI agents
```

### MCP

If a provider offers MCP integration, the endpoint is listed in the Integration section of `osp.md`. Service manifests can reference specific MCP tool names.

### robots.txt

`osp.md` does not override `robots.txt` directives. A provider that blocks AI crawlers via `robots.txt` but publishes `osp.md` is explicitly choosing to be discoverable for service requests while restricting content crawling.

## Token Efficiency

A well-written `osp.md` file should consume fewer than 500 tokens for the full file, and fewer than 100 tokens for a quick relevance check (H1 + blockquote). Service manifests should consume fewer than 1,000 tokens each.

Providers can verify their token counts using the OSP validator tool.

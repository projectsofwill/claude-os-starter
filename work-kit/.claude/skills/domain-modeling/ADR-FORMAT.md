# ADR Format

ADRs live in `docs/adr/` using sequential numbering (`0001-slug.md`, etc.), created lazily on first use.

## Template

```md
# {Short title of the decision}

{1-3 sentences: what's the context, what did we decide, and why.}
```

Minimal by design — "the value is in recording *that* a decision was made and *why*."

## Optional sections

Include only when genuinely useful:

- **Status** frontmatter: `proposed | accepted | deprecated | superseded by ADR-NNNN`
- **Considered Options** — when rejected alternatives are worth preserving
- **Consequences** — when downstream effects aren't obvious

## When to write an ADR

All three criteria must be met:

1. **Hard to reverse** — changing course later carries real cost
2. **Surprising without context** — future readers would wonder why
3. **Real trade-off** — genuine alternatives existed

## What qualifies

- Architectural shape (monorepo, event sourcing, etc.)
- Cross-context integration patterns
- Technology choices with lock-in (DB, message bus, auth provider)
- Boundary/ownership decisions
- Deliberate deviations from the obvious path — prevents others from undoing intentional choices
- Constraints invisible in the code (compliance, SLA contracts)
- Non-obvious rejected alternatives

<!--
SPDX-FileCopyrightText: 2026 Arthur Mouraud
SPDX-License-Identifier: Apache-2.0
-->

# Architecture Decision Records (ADR)

Cross-module architectural decisions that affect this repo (or the broader workspace). Each ADR is a short, immutable note: once accepted, it is amended only via a successor ADR.

## When to write an ADR
- A decision changes a public Protocol, type, or contract that another repo depends on.
- A decision removes or replaces an abstraction (e.g. deprecating `RobotInterface`).
- A trade-off has been made between two viable alternatives, and the reasoning should outlive the conversation.

If the decision is fully local to one module and reversible without breaking consumers, skip the ADR — a code comment is enough.

## Format

Each ADR file: `ADR-NNN-short-kebab-title.md`.

```markdown
# ADR-NNN — Title

- **Status**: Proposed | Accepted YYYY-MM-DD | Superseded by ADR-MMM | Implemented YYYY-MM-DD
- **Deciders**: Arthur Mouraud
- **Scope**: <which repos / modules are affected>

## Context
<what problem prompted the decision>

## Decision
<what we chose, stated in one paragraph>

## Alternatives considered
<rejected options + why>

## Consequences
<positive + negative effects, and the migration plan if relevant>
```

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-001](ADR-001-unify-on-envadapter.md) | Unify on EnvAdapter, deprecate RobotInterface/Observation/Action | Accepted 2026-05-25 |

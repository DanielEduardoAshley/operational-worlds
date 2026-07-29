---
identifier: CON-INDEX
title: Conceptual Framework
status: Canonical
version: 0.2
updated: 2026-07
milestone: OWM-0005
---

# Conceptual Framework

The Conceptual Framework contains the canonical vocabulary of Operational
Worlds.

Each concept has one authoritative document.

Other parts of the repository should link to these documents rather than
silently redefining their terms.

## Canonical concepts

1. [Operational World](01-operational-world.md)
2. [Primitive](02-primitive.md)
3. [Capability](03-capability.md)
4. [Participant Action](04-participant-action.md)
5. [Mechanism](05-mechanism.md)
6. [Observation](06-observation.md)
7. [Evidence](07-evidence.md)
8. [Interface](08-interface.md)
9. [Infrastructure](09-infrastructure.md)

## Core operational chain

```text
Primitive
↓ introduces
Capability
↓ may be realized through
Participant Action
↓ may contribute to
Mechanism
↓ is documented through
Observation
↓ may become
Evidence
↓ may produce
Revision
```

This is a common analytic path.

It is not a deterministic sequence.

## Supporting concepts

```text
Interface
    represents and mediates capabilities

Infrastructure
    supports the world and its operation

Operational World
    contains and relates the full system
```

## Base noun and base verb distinction

A useful shorthand is:

```text
Primitives = base nouns
Capabilities = base verbs
```

This shorthand should not erase complexity.

A Primitive may introduce multiple Capabilities.

A Capability may be introduced by multiple Primitives or by non-Primitive
conditions.

## Concept levels

| Level | Concept |
|---|---|
| World | Operational World |
| Object | Primitive |
| Possibility | Capability |
| Event | Participant Action |
| Dynamic | Mechanism |
| Record | Observation |
| Support for claim | Evidence |
| Mediation | Interface |
| Support system | Infrastructure |

## Canonical use

When introducing a concept in another document:

1. use the canonical term;
2. link to the canonical definition;
3. avoid incompatible local redefinitions;
4. identify proposed variants as candidate concepts;
5. record meaningful changes in a release.

## Relationship to future models

The Conceptual Framework defines the terms.

The Conceptual Models will describe relationships among them.

OWM-0005 Part 03 will publish the first model set.

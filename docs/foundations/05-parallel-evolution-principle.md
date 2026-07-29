---
identifier: FND-0005
title: Parallel Evolution Principle
status: Canonical
version: 0.2
updated: 2026-07
milestone: OWM-0005
depends_on:
  - FND-0001
  - FND-0004
referenced_by:
  - MAN-0001
  - FND-0006
  - FND-0007
  - METH-0001
  - ENG-0001
  - ENG-0002
---

# Parallel Evolution Principle

## Principle

> Theory, methodology, practice, documentation, and engineering evolve
> concurrently. No single stream permanently precedes or governs the others.

## Diagram

```text
Theory ↔ Methodology ↔ Practice ↔ Documentation ↔ Engineering
```

The diagram is not a workflow order.

It represents a system of reciprocal influence.

A change in any stream may require revision elsewhere.

## Rationale

A strictly linear model might imply:

```text
Theory
↓
Methodology
↓
Engineering
↓
Practice
↓
Observation
```

That sequence may describe some projects, but it does not adequately describe
Operational Worlds.

In this research program:

- a fabricated object may expose a conceptual problem;
- a participant action may challenge an assumed capability;
- a software constraint may reveal an ambiguous specification;
- an observation method may require a different interface;
- a theoretical distinction may require new metadata;
- a documentation gap may reveal an unexamined implementation choice;
- an engineering abstraction may make a new comparison possible.

Knowledge emerges through movement among streams.

## Why documentation is included

Documentation is not simply the final record of decisions made elsewhere.

Writing may reveal:

- duplicated concepts;
- contradictions;
- unclear dependencies;
- hidden assumptions;
- missing distinctions;
- terms being used at different levels of abstraction.

Documentation therefore participates in research rather than merely reporting
it.

## Consequences

### Documentation must follow implementation

When engineering produces a meaningful distinction, the documentation must be
updated.

### Engineering must follow research meaning

A convenient implementation should not silently redefine a concept.

### Practice may revise theory

Unexpected use is not automatically an error. It may reveal a missing
capability, action, or mechanism.

### Methodology may revise representation

If a comparison cannot be made reliably, the canonical representation may need
to become more precise.

### Research may revise architecture

A new distinction may require changes to metadata, file structure, interfaces,
tests, or compilation logic.

## Example: canonical orientation

The first primitive gallery exposed the need for stable orientation.

The triangle needed a vertex-up reference.

The square needed edges parallel to the tile.

The hexagon needed top and bottom edges parallel to the tile.

These implementation decisions became documentation and testing requirements.

Engineering did not merely apply theory. It helped produce a clearer
theoretical and methodological distinction.

## Example: Primitive Gallery

The Primitive Gallery began as a usability feature.

During implementation it became clear that it also functions as a comparative
research instrument.

That realization affected:

- the methodology;
- object spacing;
- shared scale;
- canonical orientation;
- metadata;
- research questions;
- documentation.

The feature therefore evolved across all research streams.

## Milestone review question

For every major milestone, ask:

> What did each stream learn from the others?

A milestone is stronger when its conceptual, methodological, practical,
documentary, and engineering consequences are all visible.

## Revision history

| Version | Milestone | Change |
|---|---|---|
| 0.2 | OWM-0005 | Established as a canonical foundational principle |

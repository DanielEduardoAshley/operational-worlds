---
identifier: FND-0007
title: Research First Principle
status: Validated
version: 0.2
updated: 2026-07
milestone: OWM-0005
depends_on:
  - FND-0001
  - FND-0005
  - FND-0006
referenced_by:
  - METH-0001
  - METH-0006
  - ENG-0002
  - ENG-0003
---

# Research First Principle

## Principle

> Engineering, documentation, and fabrication should remain answerable to the
> research questions they are intended to support.

Research First does not mean that theory must be completed before anything is
built.

That would contradict the Parallel Evolution Principle.

It means that implementation should not become the unexamined center of the
project.

## Research-centered cycle

```text
Question
↓
Research
↓
Documentation
↓
Engineering
↓
Experiment
↓
Observation
↓
Evidence
↓
Revision
↓
New question
```

The cycle may begin at different points in practice.

The principle concerns orientation rather than sequence.

## Implementation-to-research relationship

Every meaningful implementation should be connected to a research purpose.

| Implementation | Research purpose |
|---|---|
| Primitive Gallery | Comparative observation |
| Primitive Inspector | Inspectable research metadata |
| Canonical orientation | Stable geometric comparison |
| Geometry representation | Backend-independent primitive meaning |
| Compiler architecture | Multiple material and digital outputs |
| Metadata | Provenance and conceptual continuity |
| Automated tests | Protection of specified research properties |

## Avoiding feature drift

A software feature may be technically useful while contributing little to the
research program.

Before adding a feature, ask:

1. What research activity does this enable?
2. Which concept does it represent?
3. Which method does it support?
4. What evidence could it help produce?
5. Does it belong in the current milestone?

These questions do not prohibit experimentation.

They help distinguish an experiment from an accidental expansion of scope.

## Documentation responsibility

Research First means that documentation should explain reasoning.

It is insufficient to record only:

> The triangle points upward.

The research record should also explain:

> The triangle uses a vertex-up canonical orientation to establish a stable
> comparative reference. Rotated variants remain possible, but the canonical
> orientation supports consistent galleries, documentation, and tests.

Reasoning allows future researchers to evaluate a decision rather than merely
inherit it.

## Engineering responsibility

Engineering should preserve distinctions that matter to the research.

For example:

- Primitive meaning should remain separate from Blender-specific code.
- Capabilities should not be inferred solely from geometry filenames.
- Metadata should not be discarded during generation.
- Canonical and variant parameters should be distinguishable.
- Tests should verify orientation and proportion where these are research
  requirements.
- Interfaces should expose meaningful distinctions rather than only technical
  settings.

## Fabrication responsibility

Fabrication should also remain answerable to research.

Material choices, tolerances, connectors, scale, finish, and assembly methods
may affect:

- perceived affordance;
- durability;
- movement;
- comparison;
- participant interpretation;
- repeatability.

A fabrication decision is not automatically neutral because it occurs outside
software.

## Completion test

A milestone is not complete merely because the software runs.

A research milestone should be evaluated across four dimensions.

### Research

Did the work sharpen or test a question?

### Engineering

Does the implementation behave reliably?

### Documentation

Does the manual explain what changed and why?

### Continuity

Can a future reader reconstruct the evolution of the decision?

A strong milestone leaves all four dimensions legible.

## Revision history

| Version | Milestone | Change |
|---|---|---|
| 0.2 | OWM-0005 | Established as a validated foundational principle |

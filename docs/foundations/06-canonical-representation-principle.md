---
identifier: FND-0006
title: Canonical Representation Principle
status: Canonical
version: 0.2
updated: 2026-07
milestone: OWM-0005
depends_on:
  - FND-0005
referenced_by:
  - CON-0002
  - OWCM-0002
  - METH-0002
  - ENG-0001
  - ENG-0004
  - PRIM-0001
  - PRIM-0002
  - PRIM-0003
  - PRIM-0004
---

# Canonical Representation Principle

## Principle

> Every established concept within Operational Worlds should have a stable
> reference representation appropriate to its domain.

Examples include:

- a concept with a canonical definition;
- a conceptual relationship with a canonical model;
- a Primitive with canonical geometry;
- an oriented Primitive with a canonical orientation;
- a software object with canonical metadata;
- a release with a canonical record.

## Purpose

Canonical representations make comparison possible.

Without a stable reference, it becomes difficult to determine whether two
objects are:

- the same Primitive;
- variants of one Primitive;
- different implementations;
- different scales;
- different orientations;
- conceptually distinct objects.

## Canonical does not mean universal

A canonical representation is the current stable reference within the research
program.

It does not claim to be the only possible representation.

A triangle may be rotated during use.

A circle may be scaled.

A square may become a rectangular variant.

A hexagon may be embedded in a larger surface.

These transformations do not erase the value of a canonical reference.

## Canonical geometry and variants

```text
Canonical Primitive
├── Canonical geometry
├── Canonical orientation
├── Canonical metadata
└── Canonical documentation

Variant
├── Modified scale
├── Modified proportion
├── Modified material
├── Modified orientation
├── Modified fabrication
└── Modified operational context
```

A variant should identify the canonical object from which it differs.

## Canonical orientation

Canonical orientation is necessary when rotation changes comparative
legibility or operational interpretation.

Current primitive orientations are:

| Primitive | Canonical orientation |
|---|---|
| Raised Circle | Rotation-independent |
| Raised Triangle | One vertex upward |
| Raised Square | Top and bottom edges parallel to the tile |
| Raised Hexagon | Top and bottom edges parallel to the tile |

Orientation is a stable reference, not a prohibition against rotation.

## Canonical definitions

Concept definitions should have one authoritative home.

Other documents should link to that definition rather than silently creating
competing versions.

For example:

```text
docs/conceptual-framework/03-capability.md
```

will be the canonical definition of Capability.

Primitive records, engineering documents, and conceptual models may summarize
the concept, but should not redefine it inconsistently.

## Canonical metadata

Metadata connects research meaning across systems.

A generated primitive should be able to identify:

- its Primitive ID;
- its canonical name;
- its geometry type;
- its dimensions;
- its research version;
- its documented capabilities;
- its relationship to a gallery or experiment;
- whether it is canonical or a variant.

This allows the object to remain connected to the research record.

## Canonical documentation

Canonical documentation does not require every idea to exist in one file.

It requires each concept, model, method, specification, or engineering
decision to have an authoritative location.

Other documents should reference that location.

This reduces:

- duplicated definitions;
- terminology drift;
- conflicting explanations;
- hidden assumptions;
- obsolete summaries.

## Revision

When a canonical representation changes, the change should be:

1. motivated;
2. documented;
3. versioned;
4. propagated to affected implementations;
5. included in a research release.

Canonical representation provides continuity precisely because revision is made
explicit.

## Review test

Before calling a representation canonical, ask:

- Is its purpose clear?
- Is its scope clear?
- Is it distinguishable from variants?
- Is it documented in one authoritative location?
- Can it be tested or inspected?
- Can future revisions be traced?

## Revision history

| Version | Milestone | Change |
|---|---|---|
| 0.2 | OWM-0005 | Established as a canonical foundational principle |

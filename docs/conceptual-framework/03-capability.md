---
identifier: CON-0003
title: Capability
status: Canonical
version: 0.2
updated: 2026-07
milestone: OWM-0005
depends_on:
  - CON-0001
  - CON-0002
referenced_by:
  - CON-0004
  - CON-0005
  - OWCM-0001
  - OWCM-0003
---

# Capability

## Definition

> A Capability is a possibility for operation introduced or supported by an
> entity, relation, interface, rule, or condition within an Operational World.

Capability describes what may be done, caused, enabled, prevented, or
transformed.

## Capability as base verb

If Primitives are base nouns, Capabilities are the base verbs of the system.

Examples include:

- connect;
- separate;
- contain;
- divide;
- pass;
- store;
- reveal;
- conceal;
- rotate;
- exchange;
- submit;
- revise;
- compete;
- cooperate.

These are operational possibilities, not guaranteed events.

## Capability is not action

A capability may exist without being enacted.

A slot may support insertion even if no participant inserts anything.

A save function may support persistence even if no save occurs.

The capability belongs to the system's possibility structure.

The action belongs to an event.

## Sources of capability

Capabilities may be introduced by:

- a Primitive;
- a relation among Primitives;
- an interface;
- infrastructure;
- a rule;
- a participant role;
- a temporal condition;
- a resource;
- an environmental state.

Capability is not limited to geometry.

## Intended and discovered capabilities

### Intended capability

A capability deliberately designed into the system.

### Discovered capability

A capability found through use but not originally specified.

### Attributed capability

A capability participants believe exists, whether or not the system reliably
supports it.

### Latent capability

A capability technically available but not represented clearly enough to be
recognized.

These categories help distinguish design intent from actual use.

## Capability profile

A Primitive or world may have a capability profile.

Example:

```text
Raised Circle
├── center
├── mark
├── place
├── gather
├── orbit
└── avoid
```

The profile is a research claim.

It should be supported by implementation, observation, or explicit hypothesis.

## Capability conditions

A capability may depend on conditions.

For example, a passage capability may depend on:

- sufficient width;
- accessible location;
- participant scale;
- absence of obstruction;
- permission to cross.

Capabilities should therefore be documented with relevant conditions where
necessary.

## Positive and negative capabilities

A system may support the capability to prevent.

Examples include:

- block;
- restrict;
- hide;
- lock;
- exclude;
- delay;
- erase.

Capabilities are not limited to enabling movement or access.

## Research questions

- Which capabilities are explicit?
- Which are latent?
- Which are discovered?
- Which depend on context?
- Which are shared by multiple Primitives?
- Which capabilities conflict?
- Which capabilities participants recognize without instruction?

## Revision history

| Version | Milestone | Change |
|---|---|---|
| 0.2 | OWM-0005 | Established canonical definition |

# Operational Worlds

Operational Worlds is a living artistic research program for investigating,
designing, constructing, and evaluating operational systems.

An operational world is defined not only by appearance, but by the
possibilities, constraints, relations, actions, and dynamics that become
available within it.

The project develops through several interdependent forms:

- conceptual research;
- methodological development;
- software engineering;
- physical fabrication;
- artistic experimentation;
- observation and documentation;
- public presentation and critique.

These forms do not follow a single linear sequence. They evolve together,
informing and revising one another.

## Research proposition

Operational Worlds begins from the proposition that systems can be treated as
artistic material.

A world may be investigated through:

- the primitives it contains;
- the capabilities those primitives introduce;
- the actions participants may perform;
- the mechanisms that emerge through repeated activity;
- the observations gathered during use;
- the evidence produced through comparison and revision.

The project therefore treats artworks not only as finished objects, but as
research environments through which operational questions can be posed and
tested.

## Current research focus

The current phase develops a family of physical Operational Primitives and the
Operational Worlds Design Engine, or OWDE.

| Identifier | Primitive | Canonical orientation |
|---|---|---|
| PRIM-0001 | Raised Circle | Rotation-independent |
| PRIM-0002 | Raised Triangle | One vertex upward |
| PRIM-0003 | Raised Square | Edges parallel to the tile |
| PRIM-0004 | Raised Hexagon | Top and bottom edges parallel to the tile |

The Blender implementation currently supports parametric primitive generation,
individual tiles, a comparative Primitive Gallery, structured metadata, a
Primitive Inspector, reproducible add-on builds, and automated tests.

## Governing principles

Operational Worlds currently follows three foundational principles.

### Parallel Evolution Principle

```text
Theory ↔ Methodology ↔ Practice ↔ Documentation ↔ Engineering
```

Each research stream may revise the others.

### Canonical Representation Principle

Established concepts, models, primitives, metadata, and releases require stable
reference representations so that variants and revisions can be compared.

### Research First Principle

Engineering, documentation, and fabrication remain answerable to the research
questions they are intended to support.

## Repository as research instrument

This repository records canonical definitions, conceptual models, primitive
specifications, implementation decisions, experiments, observations, evidence,
revisions, and releases.

Git history therefore records the evolution of ideas as well as software.

## Documentation architecture

```text
docs/
├── foundations/
├── conceptual-framework/
├── conceptual-models/
├── methodology/
├── primitives/
├── engineering/
├── research-notes/
├── releases/
└── templates/
```

## Reading path

1. [Research Manual index](docs/README.md)
2. [Introduction](docs/foundations/01-introduction.md)
3. [Repository as Research Instrument](docs/foundations/04-repository-as-research-instrument.md)
4. [Conceptual Framework](docs/conceptual-framework/README.md)
5. [Methodology](docs/methodology/README.md)
6. [Primitive Catalog](docs/primitives/README.md)
7. [Engineering Overview](docs/engineering/README.md)

## Status

Operational Worlds is an active research program.

```text
Draft → Validated → Stable → Canonical
```

Canonical means the current stable reference against which variants and
revisions are evaluated.

## License

See [LICENSE](LICENSE).

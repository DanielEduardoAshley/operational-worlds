**Motto:** *Design operations. Compile worlds.*

# OWEP-0001
# Core Architectural Principles

**Document:** Operational Worlds Engineering Proposal 0001  
**Title:** Core Architectural Principles  
**Status:** Accepted  
**Version:** 0.1.0  
**Author:** Daniel Ashley  
**Project:** Operational Worlds Design Engine (OWDE)  
**Created:** July 2026

---

# Abstract

The Operational Worlds Design Engine (OWDE) is a research-oriented software platform for designing, compiling, documenting, and studying Operational Worlds.

Unlike conventional creative software, OWDE does not begin with geometry, rendering, or fabrication. It begins with operational systems.

Operational relationships, capabilities, constraints, and interactions are treated as the primary objects of design. Physical artifacts, digital simulations, visualizations, and documentation are understood as compiled representations of an underlying operational model.

This document establishes the architectural principles that govern the development of OWDE. Every future engineering decision should be evaluated against the principles described herein.

---

# 1. Purpose

The purpose of the Operational Worlds Design Engine is to provide a computational framework for constructing Operational Worlds as reproducible research systems.

The engine exists to support artistic inquiry by enabling operational ideas to be represented, explored, fabricated, simulated, documented, and revised through a unified architecture.

The software is not the research itself.

Rather, it is the computational infrastructure through which research can be expressed, tested, and communicated.

---

# 2. Scope

This proposal establishes the philosophical and architectural foundations of OWDE.

It intentionally does **not** define:


• implementation details.
• programming language choices.
• software architecture.
• rendering technologies.
• fabrication workflows.
• user interface design.
• simulation algorithms.

These topics are specified in subsequent Operational Worlds Engineering Proposals (OWEPs).

---

# 3. Vision

OWDE exists to make Operational Worlds computationally expressible.

A single operational model should be capable of generating many forms of expression, including:


• physical artifacts.
• installations.
• simulations.
• interactive systems.
• visual documentation.
• research publications.
• archival records.

The operational model remains the single source from which all representations are derived.

---

# 4. Guiding Philosophy

Operational Worlds are systems.

They are not collections of objects.

The engine therefore models relationships, operations, constraints, and capabilities before considering geometry or appearance.

Geometry is representation.

Operations are meaning.

This distinction forms the conceptual foundation of the entire project.

---

# 5. Architectural Principles

## Principle 1 — Research First

Research is the primary purpose of the engine.

Every subsystem should contribute to investigating, documenting, communicating, or reproducing operational research.

Features that do not meaningfully support these goals should not become part of the core architecture.

---

## Principle 2 — Operations Before Geometry

Operational meaning always precedes representation.

No primitive is defined by its appearance.

Instead, primitives are defined by the operational capabilities they introduce into an Operational World.

Geometry is merely one possible manifestation of an operational construct.

---

## Principle 3 — Single Source of Truth

Research, software, documentation, metadata, simulations, and generated artifacts should derive from one operational model.

Information should never require duplication across multiple systems.

Changes to the operational model should propagate naturally to downstream outputs.

---

## Principle 4 — Reproducibility

Every Operational World should be reproducible.

Generated artifacts should always be traceable back to the operational model from which they originated.

Research outcomes should be reproducible whenever practical.

Version history should preserve the evolution of operational systems over time.

---

## Principle 5 — Modularity

The computational core should remain independent of:


• rendering systems.
• fabrication technologies.
• user interfaces.
• simulation engines.
• visualization platforms.

These capabilities should exist as adapters surrounding the operational core.

The engine should remain portable across technologies.

---

## Principle 6 — Relationships as First-Class Concepts

Operational Worlds emerge through relationships.

Objects exist because they participate in relationships.

Relationships should therefore be represented explicitly rather than inferred whenever possible.

Future computational reasoning should operate primarily upon relationships rather than isolated objects.

---

## Principle 7 — Extensibility

The architecture should remain open to future operational languages, fabrication methods, visualization systems, simulation techniques, and research methodologies.

Growth should occur through extension rather than redesign.

---

# 6. Architectural Layers

OWDE is organized into conceptual layers.

```
Research
        ↓
Experiment
        ↓
Operational Model
        ↓
Compiler
        ↓
Adapters
        ↓
Artifacts
        ↓
Observation
        ↓
Research
```

Research informs the operational model.

The operational model is compiled into artifacts.

Artifacts generate observations.

Observations inform future research.

The architecture therefore forms a continuous research cycle rather than a linear production pipeline.

---

# 7. Core Concepts

The following concepts define the foundational ontology of OWDE.


• Research.
• Experiment.
• World.
• Primitive.
• Entity.
• Relationship.
• Operation.
• Artifact.
• Observation.

Formal definitions of these concepts are provided in **OWEP-0002: Object Model**.

---

# 8. Design Constraints

The architecture should strive to satisfy the following constraints.


• Conceptual clarity.
• Reproducibility.
• Modularity.
• Extensibility.
• Traceability.
• Operational consistency.
• Computational simplicity where practical.

When trade-offs arise, preserving operational meaning should take precedence over implementation convenience.

---

# 9. Non-Goals

OWDE is not intended to become:


• a general-purpose CAD application.
• a replacement for Blender.
• a game engine.
• a mesh-editing application.
• a rendering package.
• a visual effects platform.

These systems may integrate with OWDE but do not define its purpose.

---

# 10. Success Criteria

The architecture succeeds when researchers can:


• define operational systems precisely.
• reproduce Operational Worlds reliably.
• generate multiple artifact types from one operational model.
• document experiments automatically.
• evolve operational languages without destabilizing previous work.
• maintain conceptual consistency across research, software, and artifacts.

---

# 11. Future Work

Subsequent Engineering Proposals are expected to define:


• OWEP-0002 — Object Model.
• OWEP-0003 — Compiler Pipeline.
• OWEP-0004 — Primitive System.
• OWEP-0005 — Capability Model.
• OWEP-0006 — Adapter Architecture.
• OWEP-0007 — Documentation System.

This document serves as the constitutional foundation from which these proposals derive.

---

# 12. Conclusion

Operational Worlds Design Engine is not software for drawing objects.

It is software for designing operational systems.

By establishing operations as the primary unit of design, OWDE seeks to provide a durable computational framework for artistic research—one in which physical artifacts, simulations, documentation, and future forms of expression emerge from a shared operational model.

Every future engineering decision should strengthen, rather than weaken, the principles established in this document.

---

"Design operations. Compile worlds."
#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

###############################################################################
# Operational Worlds
# Documentation Migration
#
# Milestone : OWM-0005
# Part      : 01B
# Name      : Foundational Principles
# Version   : 0.2
#
# Purpose:
#   Publish the three foundational principles that govern the relationship
#   among research, representation, practice, documentation, and engineering.
#
# Run from:
#   The root of the OperationalWorlds Git repository.
#
# Prerequisite:
#   OWM-0005 Part 01A should already have been run.
###############################################################################

MILESTONE_ID="OWM-0005"
PART_ID="01B"
PART_NAME="Foundational Principles"
BACKUP_ROOT=".owm-backups"
TIMESTAMP="$(date +"%Y%m%d-%H%M%S")"
BACKUP_DIR="${BACKUP_ROOT}/${MILESTONE_ID}-${PART_ID}-${TIMESTAMP}"

declare -a CREATED_FILES=()
declare -a UPDATED_FILES=()
declare -a BACKED_UP_FILES=()

rule() {
  printf '%s\n' "════════════════════════════════════════════════════════════"
}

fail() {
  printf '\nERROR: %s\n' "$1" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"
}

verify_repository_root() {
  [[ -d ".git" ]] || fail "No .git directory found. Run from the repository root."
  [[ -f "README.md" ]] || fail "README.md was not found."
  [[ -f "docs/README.md" ]] \
    || fail "docs/README.md was not found. Run OWM-0005 Part 01A first."
  [[ -f "docs/foundations/04-repository-as-research-instrument.md" ]] \
    || fail "Foundation files from Part 01A were not found."
}

backup_file() {
  local source_path="$1"
  [[ -f "${source_path}" ]] || return 0

  local backup_path="${BACKUP_DIR}/${source_path}"
  mkdir -p "$(dirname "${backup_path}")"
  cp -p "${source_path}" "${backup_path}"
  BACKED_UP_FILES+=("${source_path}")
}

prepare_destination() {
  local destination="$1"
  mkdir -p "$(dirname "${destination}")"

  if [[ -f "${destination}" ]]; then
    backup_file "${destination}"
    UPDATED_FILES+=("${destination}")
  else
    CREATED_FILES+=("${destination}")
  fi
}

write_file() {
  local destination="$1"
  local temporary="${destination}.owm-tmp"

  prepare_destination "${destination}"
  cat > "${temporary}"
  mv "${temporary}" "${destination}"
}

print_list() {
  local title="$1"
  shift
  local -a items=("$@")

  printf '\n%s (%d)\n' "${title}" "${#items[@]}"

  if ((${#items[@]} == 0)); then
    printf '  — none\n'
  else
    local item
    for item in "${items[@]}"; do
      printf '  • %s\n' "${item}"
    done
  fi
}

rule
printf '%s\n' "Operational Worlds"
printf '%s\n' "${MILESTONE_ID} — Part ${PART_ID}"
printf '%s\n' "${PART_NAME}"
rule

require_command git
require_command python3
require_command grep
require_command cp
require_command mv
verify_repository_root

mkdir -p "${BACKUP_DIR}"

###############################################################################
# FND-0005 — Parallel Evolution Principle
###############################################################################

write_file "docs/foundations/05-parallel-evolution-principle.md" <<'MD'
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
MD

###############################################################################
# FND-0006 — Canonical Representation Principle
###############################################################################

write_file "docs/foundations/06-canonical-representation-principle.md" <<'MD'
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
MD

###############################################################################
# FND-0007 — Research First Principle
###############################################################################

write_file "docs/foundations/07-research-first-principle.md" <<'MD'
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
MD

###############################################################################
# Update Foundations index
###############################################################################

write_file "docs/foundations/README.md" <<'MD'
---
identifier: FND-INDEX
title: Foundations
status: Validated
version: 0.2
updated: 2026-07
milestone: OWM-0005
---

# Foundations

The Foundations documents state the commitments that orient the Operational
Worlds Research Program.

They do not specify every concept or procedure.

They explain:

- why the program exists;
- what it seeks to investigate;
- how different forms of work relate;
- how stable reference representations are established;
- how implementation remains answerable to research.

## Documents

1. [Introduction](01-introduction.md)
2. [Vision](02-vision.md)
3. [Research Questions](03-research-questions.md)
4. [Repository as Research Instrument](04-repository-as-research-instrument.md)
5. [Parallel Evolution Principle](05-parallel-evolution-principle.md)
6. [Canonical Representation Principle](06-canonical-representation-principle.md)
7. [Research First Principle](07-research-first-principle.md)

## Governing relationship

The three principles work together.

```text
Parallel Evolution
    establishes reciprocal development among research streams

Canonical Representation
    establishes stable references for comparison and revision

Research First
    keeps implementation answerable to research purpose
```

No principle operates alone.

Parallel evolution without canonical representation can produce uncontrolled
drift.

Canonical representation without parallel evolution can become rigid.

Research First without reciprocal development can become a false linear
hierarchy.

Together, the principles support a research program that is stable enough to
compare and open enough to change.

## Relationship to the rest of the manual

The [Conceptual Framework](../conceptual-framework/README.md) defines the
program's vocabulary.

The [Conceptual Models](../conceptual-models/README.md) describe relationships
among concepts.

The [Methodology](../methodology/README.md) defines how research proceeds.

The [Primitive Catalog](../primitives/README.md) records concrete research
objects.

The [Engineering documents](../engineering/README.md) describe how software
and technical systems implement research requirements.
MD

###############################################################################
# Update Research Manual index
###############################################################################

write_file "docs/README.md" <<'MD'
---
identifier: MAN-0001
title: Operational Worlds Research Manual
status: Validated
version: 0.2
updated: 2026-07
milestone: OWM-0005
---

# Operational Worlds Research Manual

## Purpose

The Operational Worlds Research Manual is the curated reading path through the
project's conceptual, methodological, practical, and engineering records.

It does not duplicate every definition or specification.

It connects canonical documents into a coherent research system.

## Research architecture

```text
Foundations
    ↓
Conceptual Framework
    ↓
Conceptual Models
    ↓
Methodology
    ↓
Primitive Specifications
    ↓
Engineering
    ↓
Practice and Observation
    ↓
Evidence and Revision
```

This diagram is a reading path, not a claim that research proceeds linearly.

Operational Worlds follows parallel evolution.

Any layer may expose a question that revises another layer.

## Part I — Foundations

1. [Introduction](foundations/01-introduction.md)
2. [Vision](foundations/02-vision.md)
3. [Research Questions](foundations/03-research-questions.md)
4. [Repository as Research Instrument](foundations/04-repository-as-research-instrument.md)
5. [Parallel Evolution Principle](foundations/05-parallel-evolution-principle.md)
6. [Canonical Representation Principle](foundations/06-canonical-representation-principle.md)
7. [Research First Principle](foundations/07-research-first-principle.md)

## Part II — Conceptual Framework

See the [Conceptual Framework index](conceptual-framework/README.md).

## Part III — Conceptual Models

See the [Conceptual Models index](conceptual-models/README.md).

## Part IV — Methodology

See the [Methodology index](methodology/README.md).

## Part V — Primitive Catalog

See the [Primitive Catalog index](primitives/README.md).

## Part VI — Engineering

See the [Engineering index](engineering/README.md).

## Part VII — Research Notes

See the [Research Notes index](research-notes/README.md).

## Part VIII — Releases

See the [Release index](releases/README.md).

## Document maturity

Documents may carry one of four maturity states.

### Draft

The document captures an active proposal or early formulation.

### Validated

The document has been tested through discussion, implementation, fabrication,
practice, or comparison and is suitable for active use.

### Stable

The document has survived repeated use without requiring substantial
conceptual revision.

### Canonical

The document is the current authoritative representation within the research
program.

Maturity is not a claim of permanent truth.

A canonical document may still be revised when stronger evidence or clearer
distinctions emerge.

## Identifier families

| Prefix | Document family |
|---|---|
| MAN | Manual and reading-path documents |
| FND | Foundations |
| CON | Canonical concepts |
| OWCM | Operational Worlds Conceptual Models |
| METH | Methodology |
| PRIM | Primitive specifications |
| ENG | Engineering |
| NOTE | Research notes |
| OWM | Operational Worlds Milestones |

Identifiers provide stable references even when filenames or titles evolve.

## Core research chain

```text
Primitive
↓
Capability
↓
Participant Action
↓
Mechanism
↓
Observation
↓
Evidence
↓
Revision
```

The arrows describe a common analytic relationship, not a guaranteed causal
sequence.

A Primitive introduces one or more capabilities.

A participant may or may not realize those capabilities through action.

Repeated actions and interactions may produce mechanisms.

Researchers observe what occurs, organize those observations, evaluate them as
evidence, and revise the research program.

## Governing principles

Operational Worlds currently recognizes three foundational principles.

### Parallel Evolution Principle

Theory, methodology, practice, documentation, and engineering evolve
reciprocally.

### Canonical Representation Principle

Established concepts and objects require stable references for comparison.

### Research First Principle

Implementation remains answerable to the research activity it supports.

## Contribution

The contribution of Operational Worlds is not reducible to any single object,
software tool, or theoretical definition.

Its developing contribution is a living research program through which artists
and researchers can:

- identify operational structures;
- design primitives and capabilities;
- construct experimental worlds;
- observe emergent dynamics;
- compare implementations;
- document evidence;
- revise concepts and systems over time.
MD

###############################################################################
# Update root README principle section
###############################################################################

python3 <<'PY'
from pathlib import Path

path = Path("README.md")
text = path.read_text(encoding="utf-8")

old = """## Parallel development

Operational Worlds follows the Parallel Evolution Principle:

```text
Theory ↔ Methodology ↔ Practice ↔ Engineering
```

Engineering may expose a conceptual ambiguity. Fabrication may revise a
specification. Observation may revise a method. A theoretical distinction may
require a new software representation.
"""

new = """## Governing principles

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
"""

if old not in text:
    raise SystemExit(
        "README principle section did not match the expected Part 01A content."
    )

path.write_text(text.replace(old, new), encoding="utf-8")
PY

###############################################################################
# Validation
###############################################################################

printf '\nValidating migration...\n'

python3 <<'PY'
from pathlib import Path
import re
import sys

required = [
    Path("README.md"),
    Path("docs/README.md"),
    Path("docs/foundations/README.md"),
    Path("docs/foundations/01-introduction.md"),
    Path("docs/foundations/02-vision.md"),
    Path("docs/foundations/03-research-questions.md"),
    Path("docs/foundations/04-repository-as-research-instrument.md"),
    Path("docs/foundations/05-parallel-evolution-principle.md"),
    Path("docs/foundations/06-canonical-representation-principle.md"),
    Path("docs/foundations/07-research-first-principle.md"),
]

missing = [str(path) for path in required if not path.is_file()]
if missing:
    for path in missing:
        print(f"Missing required file: {path}", file=sys.stderr)
    sys.exit(1)

for path in required[1:]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        print(f"Missing YAML front matter: {path}", file=sys.stderr)
        sys.exit(1)

identifiers = {}
for path in required[1:]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^identifier:\s*(.+)$", text, re.MULTILINE)
    if not match:
        print(f"Missing identifier: {path}", file=sys.stderr)
        sys.exit(1)
    identifier = match.group(1).strip()
    if identifier in identifiers:
        print(
            f"Duplicate identifier {identifier}: "
            f"{identifiers[identifier]} and {path}",
            file=sys.stderr,
        )
        sys.exit(1)
    identifiers[identifier] = path

pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
for path in required:
    text = path.read_text(encoding="utf-8")
    for target in pattern.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        clean = target.split("#", 1)[0]
        if clean and not (path.parent / clean).resolve().exists():
            print(f"Broken link: {path} -> {target}", file=sys.stderr)
            sys.exit(1)

for expected in ("FND-0005", "FND-0006", "FND-0007"):
    if expected not in identifiers:
        print(f"Missing expected identifier: {expected}", file=sys.stderr)
        sys.exit(1)

print("Foundational principle validation passed.")
PY

printf '\nGit status after migration:\n\n'
git status --short

print_list "Created files" "${CREATED_FILES[@]}"
print_list "Updated files" "${UPDATED_FILES[@]}"
print_list "Backed-up files" "${BACKED_UP_FILES[@]}"

printf '\n'
rule
printf '%s\n' "${MILESTONE_ID} — Part ${PART_ID} Complete"
printf '%s\n' "${PART_NAME}"
rule

cat <<EOF

Recommended review:

  ✓ docs/foundations/05-parallel-evolution-principle.md
  ✓ docs/foundations/06-canonical-representation-principle.md
  ✓ docs/foundations/07-research-first-principle.md
  ✓ docs/foundations/README.md
  ✓ docs/README.md
  ✓ README.md

Backup location:

  ${BACKUP_DIR}

Useful review commands:

  git diff -- README.md
  git diff -- docs/README.md
  git diff -- docs/foundations/
  git status --short

After review, commit with:

  git add README.md docs
  git commit -m "OWM-0005 Part 01B: publish foundational principles"

Then continue with OWM-0005 Part 02: Conceptual Framework.

EOF

rule

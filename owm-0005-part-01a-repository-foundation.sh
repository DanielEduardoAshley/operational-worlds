#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

###############################################################################
# Operational Worlds
# Documentation Migration
#
# Milestone : OWM-0005
# Part      : 01A
# Name      : Repository Foundation
# Version   : 0.2
###############################################################################

MILESTONE_ID="OWM-0005"
PART_ID="01A"
PART_NAME="Repository Foundation"
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
mkdir -p \
  docs/foundations \
  docs/conceptual-framework \
  docs/conceptual-models \
  docs/methodology \
  docs/primitives \
  docs/engineering \
  docs/research-notes \
  docs/releases \
  docs/templates

write_file "README.md" <<'MD'
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

## Parallel development

Operational Worlds follows the Parallel Evolution Principle:

```text
Theory ↔ Methodology ↔ Practice ↔ Engineering
```

Engineering may expose a conceptual ambiguity. Fabrication may revise a
specification. Observation may revise a method. A theoretical distinction may
require a new software representation.

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
MD

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

The Research Manual is the curated reading path through the project's
conceptual, methodological, practical, and engineering records.

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

This is a reading path, not a claim that research proceeds linearly.

## Part I — Foundations

1. [Introduction](foundations/01-introduction.md)
2. [Vision](foundations/02-vision.md)
3. [Research Questions](foundations/03-research-questions.md)
4. [Repository as Research Instrument](foundations/04-repository-as-research-instrument.md)

## Remaining sections

- [Conceptual Framework](conceptual-framework/README.md)
- [Conceptual Models](conceptual-models/README.md)
- [Methodology](methodology/README.md)
- [Primitive Catalog](primitives/README.md)
- [Engineering](engineering/README.md)
- [Research Notes](research-notes/README.md)
- [Releases](releases/README.md)

## Document maturity

### Draft

An active proposal or early formulation.

### Validated

Tested through discussion, implementation, fabrication, practice, or
comparison and suitable for active use.

### Stable

Has survived repeated use without substantial conceptual revision.

### Canonical

The current authoritative representation within the research program.

## Identifier families

| Prefix | Document family |
|---|---|
| MAN | Manual and reading-path documents |
| FND | Foundations |
| CON | Canonical concepts |
| OWCM | Conceptual Models |
| METH | Methodology |
| PRIM | Primitive specifications |
| ENG | Engineering |
| NOTE | Research notes |
| OWM | Milestones |

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

The chain is analytic rather than deterministic.

## Contribution

Operational Worlds is a living research program through which artists and
researchers can identify operational structures, design primitives and
capabilities, construct experimental worlds, observe emergent dynamics,
compare implementations, document evidence, and revise systems over time.
MD

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

## Documents

1. [Introduction](01-introduction.md)
2. [Vision](02-vision.md)
3. [Research Questions](03-research-questions.md)
4. [Repository as Research Instrument](04-repository-as-research-instrument.md)

Additional foundational principles will be added in Part 01B.

## Relationship to the manual

The [Conceptual Framework](../conceptual-framework/README.md) defines
vocabulary. The [Conceptual Models](../conceptual-models/README.md) describe
relationships. The [Methodology](../methodology/README.md) defines how research
proceeds. The [Primitive Catalog](../primitives/README.md) records concrete
research objects. The [Engineering documents](../engineering/README.md)
describe technical implementation.
MD

write_file "docs/foundations/01-introduction.md" <<'MD'
---
identifier: FND-0001
title: Introduction
status: Validated
version: 0.2
updated: 2026-07
milestone: OWM-0005
depends_on: []
referenced_by:
  - MAN-0001
  - FND-0002
---

# Introduction

Operational Worlds is an artistic research program concerned with the design,
construction, observation, and revision of systems.

The program asks what becomes possible when a world is understood not only as
a visual or spatial arrangement, but as an operational structure.

An operational structure may include objects, spatial divisions, interfaces,
permissions, constraints, actions, sequences, feedback, memory,
communication, visibility, timing, resource distribution, and transformation.

These elements may be physical, digital, social, procedural, or hybrid.

## Worlds as systems of possibility

An Operational World is not defined only by what it contains. It is also
defined by what its contents permit, invite, prevent, record, or transform.

A raised circle may introduce a center. A wall may introduce separation. A
slot may introduce passage, insertion, or exchange. A save interface may
introduce persistence. A rule limiting submission to one attempt may
introduce commitment, irreversibility, or strategic delay.

Operational Worlds studies these possibilities as artistic and research
material.

## From artworks to research environments

An artwork within this program may function simultaneously as an aesthetic
construction, material experiment, interface, social arrangement, rule system,
research instrument, observational environment, and evolving world.

The artwork does not merely illustrate a prior theory. Its construction and
use may generate distinctions that were not available before implementation.

## Primitives

The current research begins with Operational Primitives.

A Primitive is the smallest research object treated as independently
specifiable, implementable, observable, and revisable within the program.

A Primitive may introduce one or more capabilities into a world.

Its geometry, material, orientation, placement, metadata, and context may all
contribute to its operational meaning.

## Research through construction

```text
Question
↓
Conceptual distinction
↓
Design
↓
Implementation
↓
Fabrication
↓
Use
↓
Observation
↓
Evidence
↓
Revision
↓
New question
```

This sequence describes one research cycle, but actual work may move backward,
forward, or across stages.

## A living research program

Operational Worlds is intentionally incomplete. Definitions may be refined,
primitives may gain variants, capabilities may be revised, methods may improve,
implementations may change, and evidence may challenge assumptions.

The goal is not to freeze a universal system. It is to establish enough
clarity and continuity that meaningful comparison and cumulative development
become possible.
MD

write_file "docs/foundations/02-vision.md" <<'MD'
---
identifier: FND-0002
title: Vision
status: Validated
version: 0.2
updated: 2026-07
milestone: OWM-0005
depends_on:
  - FND-0001
referenced_by:
  - MAN-0001
  - FND-0003
---

# Vision

Operational Worlds seeks to develop a durable artistic research program for
investigating how systems produce experience, behavior, relation, and meaning.

## Long-term vision

The long-term vision includes a coherent conceptual framework, a catalog of
researched Operational Primitives, methods for composing primitives into larger
systems, physical and digital fabrication tools, comparative research
environments, documented experiments, versioned evidence, public artworks, a
research handbook, and software supporting creation and inquiry.

## Artistic vision

Operational Worlds treats operational architecture as artistic material.

The work may include sculpture, installation, participatory environments,
game-like systems, software, interfaces, diagrams, publications, workshops,
performances, and distributed research structures.

No single medium defines the program. The unifying concern is how designed
conditions shape what can occur.

## Research vision

The program aims to make operational decisions explicit enough to be examined:

- What capability does a form introduce?
- Which actions does an interface make available?
- Which actions remain possible but unrepresented?
- What mechanisms emerge through repeated use?
- Which observations support a claim?
- How does geometry alter behavior?
- How does a rule alter timing, attention, or commitment?
- When do multiple primitives form a system?
- When does a system become a world?

## Engineering vision

Engineering is not a neutral service layer. Representational and architectural
decisions affect what the research can describe, generate, compare, and
preserve.

The Operational Worlds Design Engine should keep operational meaning distinct
from any single backend. A Primitive should not be defined by Blender.
Geometry should be compilable into multiple representations. Metadata should
survive movement between documentation, software, fabrication, and observation.

## Public vision

Other artists and researchers may eventually implement existing primitives,
propose new ones, create variants, test capabilities, document mechanisms,
compare evidence, construct new Operational Worlds, challenge the ontology,
and extend the tools.

For this to become possible, the project must remain legible, reproducible, and
open to revision.
MD

write_file "docs/foundations/03-research-questions.md" <<'MD'
---
identifier: FND-0003
title: Research Questions
status: Draft
version: 0.2
updated: 2026-07
milestone: OWM-0005
depends_on:
  - FND-0001
  - FND-0002
referenced_by:
  - MAN-0001
---

# Research Questions

Operational Worlds is organized around a developing family of questions rather
than a single closed hypothesis.

## Primary question

How can artists and researchers design, construct, observe, and revise
operational worlds as systems of possibility?

## Conceptual questions

- What distinguishes an Operational World from an object, environment,
  interface, game, or installation?
- What is the smallest useful unit of operational analysis?
- When should something be treated as a Primitive?
- How should capabilities be distinguished from actions?
- How should actions be distinguished from mechanisms?
- When does repeated activity become evidence of an emergent mechanism?
- Can a Primitive introduce multiple capabilities?
- Can the same capability be introduced by multiple Primitives?
- Can a capability exist without being represented by an interface?
- When do multiple primitives become a composite primitive, system, surface,
  or world?

## Material and spatial questions

- How does elevation affect perceived importance or authority?
- How does a center affect placement, gathering, orbiting, or avoidance?
- How does orientation affect interpretation?
- How do boundaries affect movement and territorial behavior?
- How do scale and proportion alter a Primitive's capabilities?
- How do repeated cells produce adjacency, pattern, or network effects?
- How do materials alter legibility, durability, and behavior?
- How do fabrication tolerances affect operational use?

## Participatory questions

- How do participants recognize available actions?
- What happens when a capability is available but not represented?
- How do participants reinterpret or misuse intended operations?
- How do rules alter cooperation, competition, attention, or commitment?
- How do anonymity, persistence, reversibility, and visibility alter behavior?
- What forms of agency remain with participants?
- What forms of agency are delegated to the system?

## Methodological questions

- What counts as an observation?
- What transforms an observation into evidence?
- How should variants be compared?
- How can artistic interpretation coexist with structured research records?
- When should a candidate concept be promoted into the canonical framework?
- How can failed implementations contribute knowledge?
- How should research releases represent conceptual change?

## Engineering questions

- How can operational meaning remain independent of a software backend?
- What geometry representation is sufficient for the current primitive family?
- What metadata should travel with a generated object?
- How should software distinguish canonical geometry from variants?
- How can the engine support physical and digital outputs?
- Which tests protect research meaning rather than only software behavior?
- How can software make conceptual differences inspectable?

## Open-ended direction

Some questions will lead to stable definitions. Others may remain productive
tensions. The program should preserve unresolved questions rather than hiding
them behind premature certainty.
MD

write_file "docs/foundations/04-repository-as-research-instrument.md" <<'MD'
---
identifier: FND-0004
title: Repository as Research Instrument
status: Validated
version: 0.2
updated: 2026-07
milestone: OWM-0005
depends_on:
  - FND-0001
  - FND-0002
referenced_by:
  - MAN-0001
---

# Repository as Research Instrument

The Operational Worlds repository is part of the research methodology. It does
not merely store results produced elsewhere.

The repository helps determine what can be represented, related, implemented,
tested, revised, and remembered.

## Instrumental functions

### Definition

Canonical documents establish the current meaning of concepts.

### Relation

Conceptual models record how definitions connect.

### Specification

Primitive records connect operational purpose to geometry, fabrication,
metadata, and research questions.

### Implementation

Software makes selected concepts executable and inspectable.

### Comparison

Tools such as the Primitive Gallery support structured comparison.

### Provenance

Version control records when and why a concept, specification, or
implementation changed.

### Publication

Research releases present coherent states of the program rather than an
undifferentiated accumulation of files.

## Code as research material

Code may embody assumptions that are not yet explicit in prose.

Implementing a triangle required choosing an orientation. Implementing a
hexagon required deciding whether it should have a point or an edge at the top.
Implementing a gallery required deciding whether primitives should share scale,
spacing, alignment, and metadata.

These decisions exposed questions about canonical representation and
comparative method.

Engineering produces research knowledge when implementation reveals a
decision that must be conceptually explained.

## Blender as research environment

Blender is currently one backend and research environment within Operational
Worlds.

The add-on allows a researcher to instantiate parametric primitives, compare
primitive families, inspect metadata, examine mesh structure, evaluate
orientation, test proportion, and prepare objects for fabrication.

Blender does not define the ontology. It provides one environment in which
parts of the ontology can be made material and observable.

## Git as intellectual history

A well-structured commit can preserve the question being addressed, the
distinction being introduced, the documents affected, the implementation
changed, the evidence motivating revision, and the release in which the change
became active.

Git history can therefore become an intellectual history of the research
program.

## Milestone scripts

Terminal-pasteable milestone scripts may verify repository structure, create
backups, write documents, modify software, run tests, validate links and
metadata, print review instructions, and provide a suggested commit.

The script is not a substitute for review. It is a reproducible installation
mechanism for a defined research release.

## Limits

A repository cannot replace embodied practice, fabrication, participation,
interpretation, or critique.

It can preserve and organize records of those activities and make assumptions
visible enough to be challenged.
MD

write_file "docs/conceptual-framework/README.md" <<'MD'
---
identifier: CON-INDEX
title: Conceptual Framework
status: Draft
version: 0.2
updated: 2026-07
milestone: OWM-0005
---

# Conceptual Framework

This directory will contain the canonical vocabulary of Operational Worlds.

OWM-0005 Part 02 will publish Operational World, Primitive, Capability,
Participant Action, Mechanism, Observation, Evidence, Interface, and
Infrastructure.
MD

write_file "docs/conceptual-models/README.md" <<'MD'
---
identifier: OWCM-INDEX
title: Conceptual Models
status: Draft
version: 0.2
updated: 2026-07
milestone: OWM-0005
---

# Conceptual Models

This directory will contain models describing relationships among canonical
Operational Worlds concepts.

OWM-0005 Part 03 will publish the first model set.
MD

write_file "docs/methodology/README.md" <<'MD'
---
identifier: METH-INDEX
title: Methodology
status: Draft
version: 0.2
updated: 2026-07
milestone: OWM-0005
---

# Methodology

This directory will contain research procedures, comparative methods,
observation practices, evidence standards, candidate-concept workflows, and
release methods.

OWM-0005 Part 04 will publish the first complete methodology set.
MD

write_file "docs/primitives/README.md" <<'MD'
---
identifier: PRIM-INDEX
title: Primitive Catalog
status: Draft
version: 0.2
updated: 2026-07
milestone: OWM-0005
---

# Primitive Catalog

This directory will contain canonical specifications and evolving research
records for Operational Primitives.

OWM-0005 Part 05 will publish PRIM-0001 through PRIM-0004.
MD

write_file "docs/engineering/README.md" <<'MD'
---
identifier: ENG-INDEX
title: Engineering
status: Draft
version: 0.2
updated: 2026-07
milestone: OWM-0005
---

# Engineering

This directory will document the technical systems that support Operational
Worlds research.

OWM-0005 Part 06 will publish the initial engineering documentation.
MD

write_file "docs/research-notes/README.md" <<'MD'
---
identifier: NOTE-INDEX
title: Research Notes
status: Draft
version: 0.2
updated: 2026-07
milestone: OWM-0005
---

# Research Notes

This directory preserves exploratory material that has not yet been promoted
into the canonical framework.

Research notes may include candidate concepts, unresolved distinctions,
experiment notes, implementation discoveries, critique responses, rejected
formulations, and future research directions.
MD

write_file "docs/releases/README.md" <<'MD'
---
identifier: OWM-INDEX
title: Releases
status: Validated
version: 0.2
updated: 2026-07
milestone: OWM-0005
---

# Releases

This directory records coherent research and engineering releases.

Each release record should identify what changed, why it changed, which
concepts were introduced or revised, which implementations were affected,
which questions remain open, and how the release can be reviewed.
MD

write_file "docs/templates/document-template.md" <<'MD'
---
identifier: REPLACE-ME
title: Replace Me
status: Draft
version: 0.1
updated: YYYY-MM
milestone: OWM-XXXX
depends_on: []
referenced_by: []
---

# Replace Me

## Purpose

State why this document exists.

## Definition or proposition

State the concept, principle, model, method, specification, or engineering
decision clearly.

## Rationale

Explain why the distinction or decision matters.

## Relationships

Link to related canonical documents.

## Research consequences

Explain what the document makes possible to investigate, compare, or revise.

## Engineering consequences

Explain any representational, metadata, interface, geometry, testing, or
implementation consequences.

## Open questions

Preserve unresolved issues.

## Revision history

| Version | Milestone | Change |
|---|---|---|
| 0.1 | OWM-XXXX | Initial draft |
MD

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
    Path("docs/conceptual-framework/README.md"),
    Path("docs/conceptual-models/README.md"),
    Path("docs/methodology/README.md"),
    Path("docs/primitives/README.md"),
    Path("docs/engineering/README.md"),
    Path("docs/research-notes/README.md"),
    Path("docs/releases/README.md"),
    Path("docs/templates/document-template.md"),
]

missing = [str(path) for path in required if not path.is_file()]
if missing:
    for path in missing:
        print(f"Missing required file: {path}", file=sys.stderr)
    sys.exit(1)

for path in required[1:]:
    if path.read_text(encoding="utf-8").splitlines()[0] != "---":
        print(f"Missing YAML front matter: {path}", file=sys.stderr)
        sys.exit(1)

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

print("Documentation validation passed.")
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

  ✓ README.md
  ✓ docs/README.md
  ✓ docs/foundations/
  ✓ docs/templates/document-template.md
  ✓ placeholder indexes for later OWM-0005 parts

Backup location:

  ${BACKUP_DIR}

Useful review commands:

  git diff -- README.md
  git diff -- docs/
  git status --short

After review, commit with:

  git add README.md docs
  git commit -m "OWM-0005 Part 01A: establish research manual foundation"

Then continue with OWM-0005 Part 01B.

EOF

rule

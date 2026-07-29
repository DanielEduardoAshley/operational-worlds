#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

###############################################################################
# Operational Worlds
# Documentation Migration
#
# Milestone : OWM-0005
# Part      : 02
# Name      : Conceptual Framework
# Version   : 0.2
#
# Purpose:
#   Publish the first complete canonical vocabulary for Operational Worlds.
#
# Run from:
#   The root of the OperationalWorlds Git repository.
#
# Prerequisites:
#   OWM-0005 Part 01A
#   OWM-0005 Part 01B
###############################################################################

MILESTONE_ID="OWM-0005"
PART_ID="02"
PART_NAME="Conceptual Framework"
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
  [[ -f "docs/README.md" ]] || fail "docs/README.md was not found."
  [[ -f "docs/foundations/07-research-first-principle.md" ]] \
    || fail "Part 01B was not found. Run OWM-0005 Part 01B first."
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
mkdir -p docs/conceptual-framework

###############################################################################
# CON-0001 — Operational World
###############################################################################

write_file "docs/conceptual-framework/01-operational-world.md" <<'MD'
---
identifier: CON-0001
title: Operational World
status: Canonical
version: 0.2
updated: 2026-07
milestone: OWM-0005
depends_on:
  - FND-0001
  - FND-0002
  - FND-0005
referenced_by:
  - CON-0002
  - CON-0003
  - CON-0004
  - CON-0005
  - OWCM-0001
  - METH-0001
---

# Operational World

## Definition

> An Operational World is a bounded or distinguishable system of entities,
> conditions, capabilities, actions, relations, constraints, and mechanisms
> through which events can occur.

An Operational World is not defined only by appearance.

It is defined by the structured field of possibility it creates.

## Necessary characteristics

An Operational World must contain enough operational structure that something
can happen within it.

This usually includes some combination of:

- entities or participants;
- boundaries or distinctions;
- available capabilities;
- permitted or discoverable actions;
- rules or constraints;
- spatial or temporal organization;
- state change;
- relations among parts;
- feedback or consequence;
- mechanisms produced through activity.

Not every world must contain every element.

The term identifies a system whose organization matters to what can occur.

## Boundaries

A world may be bounded physically, digitally, procedurally, socially, or
conceptually.

Examples include:

- a sculptural board;
- a room-scale installation;
- a software environment;
- a rule-governed workshop;
- a single interface;
- a distributed participant network;
- a timed exhibition process.

A boundary does not need to be closed.

It needs to make the system distinguishable enough to be investigated.

## Scale

An Operational World may be small or large.

A single tile may function as a world if it supports meaningful action.

A larger installation may contain multiple sub-worlds.

Operational scale is determined by research usefulness, not physical size.

## Composition

An Operational World may be composed from:

```text
Primitives
+
Capabilities
+
Interfaces
+
Infrastructure
+
Participants
+
Constraints
+
Temporal conditions
+
Relations
```

The resulting world may produce mechanisms that were not specified directly.

## Designed and emergent structure

Some properties of a world are designed.

Others emerge through use.

Designed structure may include:

- geometry;
- permissions;
- timing;
- available resources;
- interface controls;
- visibility;
- sequence.

Emergent structure may include:

- cooperation;
- competition;
- avoidance;
- territorial behavior;
- convention;
- hierarchy;
- ritual;
- informal strategy.

Operational Worlds studies the relation between these two levels.

## Distinction from environment

An environment may surround activity without making its operational structure
the object of inquiry.

An Operational World treats that structure as central.

## Distinction from artwork

An Operational World may be an artwork, part of an artwork, or a research model
used to produce artworks.

The concept is broader than a single exhibition format.

## Research consequence

The concept allows artists and researchers to ask:

- What can happen here?
- Why can it happen?
- What prevents other events?
- Which structures are explicit?
- Which mechanisms emerge?
- Which properties are transferable to another world?

## Revision history

| Version | Milestone | Change |
|---|---|---|
| 0.2 | OWM-0005 | Established canonical definition |
MD

###############################################################################
# CON-0002 — Primitive
###############################################################################

write_file "docs/conceptual-framework/02-primitive.md" <<'MD'
---
identifier: CON-0002
title: Primitive
status: Canonical
version: 0.2
updated: 2026-07
milestone: OWM-0005
depends_on:
  - CON-0001
  - FND-0006
referenced_by:
  - CON-0003
  - OWCM-0001
  - OWCM-0002
  - PRIM-0001
  - PRIM-0002
  - PRIM-0003
  - PRIM-0004
---

# Primitive

## Definition

> A Primitive is the smallest research object treated as independently
> specifiable, implementable, observable, and revisable within Operational
> Worlds.

A Primitive is not necessarily physically small.

Its status depends on whether it functions as a useful unit of research.

## Primitive as noun

Within the framework:

- Primitive is a base noun;
- Capability is a base verb-like possibility;
- Participant Action is an enacted operation;
- Mechanism is a patterned dynamic.

This distinction keeps the object separate from what it makes possible.

## Necessary characteristics

A Primitive should be capable of having:

- a stable identifier;
- a canonical description;
- an implementation or representation;
- one or more documented capabilities;
- observable use or effect;
- a revision history.

## Multiple capabilities

A Primitive may introduce multiple capabilities.

For example, a raised wall may enable:

- separation;
- obstruction;
- attachment;
- alignment;
- concealment;
- territorial marking.

A Primitive should not be forced into a one-Primitive-to-one-Capability model.

## Reuse

The same Primitive may appear in multiple worlds.

Its operational role may change with:

- scale;
- material;
- orientation;
- location;
- neighboring primitives;
- interface;
- rules;
- participant interpretation.

The canonical Primitive remains the reference point.

## Primitive and variant

A variant modifies one or more properties of a canonical Primitive.

Possible variant dimensions include:

- geometry;
- proportion;
- scale;
- orientation;
- material;
- color;
- fabrication;
- metadata;
- operational context.

A variant should preserve provenance to the canonical Primitive.

## Composite Primitive

Several parts may be treated as one Primitive when they function as one
independently specifiable research object.

For example, a slot may require:

- two boundary elements;
- a gap;
- a shared alignment;
- a specific width.

The research unit may be the composite relation rather than either wall alone.

## Distinction from component

A component is a technical part.

A Primitive is a research unit.

A mesh face, screw, vertex, or shader may be a component without being a
Primitive.

## Distinction from symbol

A Primitive may be interpreted symbolically, but it is not defined only by
symbolic meaning.

Its operational role must remain investigable.

## Research questions

- Which capabilities does the Primitive introduce?
- Which properties are essential?
- Which properties may vary?
- How does context change its operation?
- What makes two implementations equivalent?
- What evidence would justify revising the canonical form?

## Revision history

| Version | Milestone | Change |
|---|---|---|
| 0.2 | OWM-0005 | Established canonical definition |
MD

###############################################################################
# CON-0003 — Capability
###############################################################################

write_file "docs/conceptual-framework/03-capability.md" <<'MD'
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
MD

###############################################################################
# CON-0004 — Participant Action
###############################################################################

write_file "docs/conceptual-framework/04-participant-action.md" <<'MD'
---
identifier: CON-0004
title: Participant Action
status: Canonical
version: 0.2
updated: 2026-07
milestone: OWM-0005
depends_on:
  - CON-0001
  - CON-0003
referenced_by:
  - CON-0005
  - CON-0006
  - OWCM-0001
  - OWCM-0003
---

# Participant Action

## Definition

> A Participant Action is an operation performed by a participant within an
> Operational World.

An action is an event.

It realizes, attempts, combines, resists, or invents one or more capabilities.

## Participant

A participant may be:

- a person;
- a group;
- an automated agent;
- a software process;
- a device;
- an institution;
- a nonhuman actor treated as operationally relevant.

The category is functional rather than exclusively human.

## Action and capability

```text
Capability
    makes an operation possible

Participant Action
    enacts or attempts that operation
```

The distinction matters because a capability may exist without being used, and
an attempted action may fail.

## Action states

A Participant Action may be:

- successful;
- unsuccessful;
- partial;
- repeated;
- interrupted;
- reversed;
- prohibited;
- improvised;
- unrecognized by the system;
- misinterpreted by observers.

## Action categories

Possible action categories include:

- spatial action;
- material action;
- interface action;
- communicative action;
- rule action;
- strategic action;
- collaborative action;
- competitive action;
- observational action;
- refusal or non-action.

Non-action may be analytically relevant when a participant could act but
chooses not to.

## Action sequence

Actions often occur in sequences.

```text
approach
↓
inspect
↓
select
↓
place
↓
revise
↓
submit
```

The order, timing, reversibility, and visibility of these actions may affect the
resulting mechanism.

## Action trace

An action trace is a record of what occurred.

Possible traces include:

- changed object position;
- system log;
- saved state;
- video recording;
- written note;
- participant report;
- observer annotation;
- timestamp;
- material wear.

The trace is not identical to the action.

It is evidence about the action.

## Intended and unintended action

Participants may use a capability as intended, reinterpret it, ignore it, or
act outside the represented interface.

Unintended action should not automatically be classified as misuse.

It may reveal:

- a discovered capability;
- unclear constraints;
- a competing interpretation;
- a missing interface;
- an emergent mechanism.

## Research questions

- Which capabilities become actions?
- Which remain unused?
- Which actions are repeated?
- Which actions are prohibited but attempted?
- Which sequences matter?
- Which traces remain?
- How does participant interpretation differ from system intent?

## Revision history

| Version | Milestone | Change |
|---|---|---|
| 0.2 | OWM-0005 | Established canonical definition |
MD

###############################################################################
# CON-0005 — Mechanism
###############################################################################

write_file "docs/conceptual-framework/05-mechanism.md" <<'MD'
---
identifier: CON-0005
title: Mechanism
status: Canonical
version: 0.2
updated: 2026-07
milestone: OWM-0005
depends_on:
  - CON-0003
  - CON-0004
referenced_by:
  - CON-0006
  - CON-0007
  - OWCM-0001
  - OWCM-0004
---

# Mechanism

## Definition

> A Mechanism is a patterned operational dynamic through which actions,
> relations, rules, or conditions produce recurring effects within an
> Operational World.

A mechanism may be designed, emergent, or mixed.

## Examples

Possible mechanisms include:

- competition;
- cooperation;
- accumulation;
- exclusion;
- circulation;
- ranking;
- delay;
- signaling;
- concealment;
- territorialization;
- exchange;
- escalation;
- repetition;
- convergence;
- fragmentation.

## Mechanism is not capability

A capability is a possibility.

A mechanism is a dynamic pattern.

For example:

```text
Capability: submit
Actions: participants submit entries
Mechanism: competition through comparative evaluation
```

The capability does not guarantee the mechanism.

## Mechanism is not single action

A single action may contribute to a mechanism but does not necessarily
constitute one.

Mechanisms become visible through:

- repetition;
- relation;
- sequence;
- feedback;
- distribution;
- consequence;
- patterned response.

## Designed mechanism

A designed mechanism is intentionally built into the world.

Examples:

- a ranking process;
- a timer;
- a voting rule;
- a limited-resource economy;
- a turn-taking sequence.

## Emergent mechanism

An emergent mechanism arises through activity without being fully specified.

Examples:

- informal leadership;
- territorial norms;
- avoidance of a central region;
- strategic delay;
- participant-created exchange conventions.

## Mixed mechanism

Many mechanisms are partly designed and partly emergent.

A designed scoring system may produce an unplanned alliance.

A save limit may produce repeated rehearsal outside the official interface.

## Mechanism conditions

Mechanisms depend on conditions such as:

- participant number;
- time;
- resource scarcity;
- visibility;
- anonymity;
- reversibility;
- persistence;
- spatial arrangement;
- enforcement;
- feedback.

A mechanism claim should identify the conditions under which it was observed.

## Mechanism strength

A mechanism may be:

- possible;
- weakly indicated;
- recurring;
- dominant;
- disrupted;
- absent under comparison.

These terms should be used cautiously and supported by evidence.

## Research questions

- Which mechanisms were designed?
- Which emerged?
- Which conditions support them?
- Which actions reproduce them?
- Which actions interrupt them?
- Do they persist across implementations?
- How do participants describe them?
- What evidence distinguishes a mechanism from coincidence?

## Revision history

| Version | Milestone | Change |
|---|---|---|
| 0.2 | OWM-0005 | Established canonical definition |
MD

###############################################################################
# CON-0006 — Observation
###############################################################################

write_file "docs/conceptual-framework/06-observation.md" <<'MD'
---
identifier: CON-0006
title: Observation
status: Canonical
version: 0.2
updated: 2026-07
milestone: OWM-0005
depends_on:
  - CON-0004
  - CON-0005
referenced_by:
  - CON-0007
  - OWCM-0001
  - OWCM-0005
  - METH-0003
---

# Observation

## Definition

> An Observation is a documented account of a condition, event, action,
> relation, trace, or pattern encountered during research.

An observation records what was noticed.

It does not by itself establish a general claim.

## Sources

Observations may come from:

- direct viewing;
- participant report;
- system log;
- video;
- audio;
- photograph;
- object state;
- material trace;
- interview;
- survey;
- sensor data;
- comparative rendering;
- code inspection;
- fabrication result.

## Structured observation

A structured observation records enough context to remain interpretable.

Useful fields include:

- date and time;
- world or experiment identifier;
- primitive or system version;
- participant context;
- observer;
- conditions;
- observed event;
- trace or source;
- uncertainty;
- preliminary interpretation.

## Description and interpretation

Observations should distinguish, where possible, between:

### Description

What was seen, recorded, or reported.

### Interpretation

What the observation may mean.

Example:

```text
Description:
Three participants placed objects near the raised circle.

Interpretation:
The raised circle may have operated as a gathering center.
```

The interpretation may later become part of an evidence claim.

## Negative observation

The absence of an expected event may be significant.

Examples:

- no participant used the save function;
- no one crossed a boundary;
- no competition emerged;
- a capability was never recognized.

Negative observations require care because absence may reflect timing,
visibility, access, sample size, or method.

## Observation and mechanism

A mechanism is inferred from patterned activity.

An observation is a record contributing to that inference.

One observation may suggest a mechanism.

Repeated or comparative observations may support stronger claims.

## Observation quality

Observation quality depends on:

- context;
- specificity;
- traceability;
- clarity;
- relevance;
- uncertainty;
- reproducibility;
- observer position;
- method.

## Research questions

- What exactly was observed?
- Under what conditions?
- What traces remain?
- What is interpretation rather than description?
- What might the observer have missed?
- What alternative explanations exist?
- What comparison would strengthen the observation?

## Revision history

| Version | Milestone | Change |
|---|---|---|
| 0.2 | OWM-0005 | Established canonical definition |
MD

###############################################################################
# CON-0007 — Evidence
###############################################################################

write_file "docs/conceptual-framework/07-evidence.md" <<'MD'
---
identifier: CON-0007
title: Evidence
status: Canonical
version: 0.2
updated: 2026-07
milestone: OWM-0005
depends_on:
  - CON-0005
  - CON-0006
referenced_by:
  - OWCM-0001
  - OWCM-0005
  - METH-0003
  - METH-0004
---

# Evidence

## Definition

> Evidence is an organized body of observations, traces, comparisons, and
> arguments used to support, revise, limit, or reject a research claim.

Evidence is not raw data alone.

It is data or observation made relevant to a claim through a documented
reasoning process.

## Evidence chain

```text
Event
↓
Trace
↓
Observation
↓
Organization
↓
Interpretation
↓
Claim
↓
Evaluation
```

The chain should remain inspectable.

## Evidence forms

Operational Worlds may use:

- observational evidence;
- comparative evidence;
- material evidence;
- behavioral evidence;
- computational evidence;
- documentary evidence;
- participant testimony;
- implementation evidence;
- negative evidence;
- historical evidence;
- interpretive evidence.

Artistic research may combine several forms.

## Evidence strength

Evidence may be described as:

- exploratory;
- suggestive;
- corroborated;
- comparative;
- conflicting;
- insufficient;
- disconfirming.

These categories describe the relationship between evidence and claim.

They are not universal statistical thresholds.

## Comparative evidence

Comparative evidence is especially important.

Examples include:

- one orientation versus another;
- one scale versus another;
- anonymous versus attributed participation;
- reversible versus irreversible submission;
- one material versus another;
- one Primitive alone versus a composite system.

Comparison helps isolate what may have produced a difference.

## Evidence and interpretation

Interpretation is not eliminated from the process.

It is made explicit.

A strong evidence record identifies:

- the claim;
- supporting observations;
- relevant traces;
- alternative explanations;
- limitations;
- uncertainty;
- comparison conditions;
- revisions produced.

## Evidence and artistic judgment

Artistic judgment may identify meaningful patterns before they can be fully
formalized.

The research program should preserve such judgments while distinguishing them
from stronger general claims.

## Revision consequence

Evidence should have the ability to change the program.

It may revise:

- a capability profile;
- a Primitive specification;
- a mechanism claim;
- a conceptual distinction;
- a methodology;
- an engineering representation;
- a research question.

Evidence that cannot affect anything risks becoming decorative documentation.

## Research questions

- What claim is being supported?
- Which observations are relevant?
- What comparison exists?
- What uncertainty remains?
- What alternative explanations exist?
- What would count against the claim?
- What revision follows?

## Revision history

| Version | Milestone | Change |
|---|---|---|
| 0.2 | OWM-0005 | Established canonical definition |
MD

###############################################################################
# CON-0008 — Interface
###############################################################################

write_file "docs/conceptual-framework/08-interface.md" <<'MD'
---
identifier: CON-0008
title: Interface
status: Canonical
version: 0.2
updated: 2026-07
milestone: OWM-0005
depends_on:
  - CON-0001
  - CON-0003
  - CON-0004
referenced_by:
  - CON-0009
  - OWCM-0006
  - METH-0005
  - ENG-0003
---

# Interface

## Definition

> An Interface is the perceptible or actionable layer through which a
> participant encounters, understands, and acts upon capabilities within an
> Operational World.

An interface represents operation.

It may expose, hide, frame, constrain, or translate capabilities.

## Forms

Interfaces may be:

- physical;
- visual;
- spatial;
- textual;
- sonic;
- gestural;
- digital;
- procedural;
- social;
- institutional.

A raised edge can be an interface.

A button can be an interface.

A posted rule can be an interface.

A facilitator can function as an interface.

## Interface and capability

A capability may exist without being clearly represented.

An interface may also imply a capability that is unreliable or unavailable.

The distinction is:

```text
Capability
    what the system can support

Interface
    how that possibility is encountered or represented
```

## Interface functions

An interface may:

- reveal;
- invite;
- label;
- constrain;
- sequence;
- confirm;
- warn;
- conceal;
- authorize;
- deny;
- record;
- translate;
- provide feedback.

## Legibility

An interface is legible when participants can form a workable understanding of
available action.

Legibility does not require total explanation.

Ambiguity may be intentional.

The research question is whether ambiguity is operationally productive or
merely obstructive.

## Interface mismatch

A mismatch occurs when:

- the interface suggests a nonexistent capability;
- a capability exists but is not represented;
- the interface hides a consequential rule;
- feedback does not reflect state accurately;
- participant interpretation differs from system behavior.

Mismatch may be a defect, a research condition, or an artistic strategy.

## Interface and coercion

Interfaces shape behavior.

Defaults, visibility, ordering, friction, and feedback may direct action
without explicit rules.

These effects should be treated as operational structure rather than neutral
presentation.

## Research questions

- Which capabilities are represented?
- Which remain latent?
- What does the interface invite?
- What does it make difficult?
- Which rules are visible?
- Which are hidden?
- How do participants interpret it?
- What action occurs outside the represented interface?

## Revision history

| Version | Milestone | Change |
|---|---|---|
| 0.2 | OWM-0005 | Established canonical definition |
MD

###############################################################################
# CON-0009 — Infrastructure
###############################################################################

write_file "docs/conceptual-framework/09-infrastructure.md" <<'MD'
---
identifier: CON-0009
title: Infrastructure
status: Canonical
version: 0.2
updated: 2026-07
milestone: OWM-0005
depends_on:
  - CON-0001
  - CON-0008
referenced_by:
  - OWCM-0006
  - METH-0005
  - ENG-0002
  - ENG-0003
---

# Infrastructure

## Definition

> Infrastructure is the supporting technical, material, procedural, or
> institutional system that enables an Operational World to function without
> necessarily appearing as a primary object of participant attention.

Infrastructure supports operation.

It may remain partially hidden.

## Examples

Infrastructure may include:

- software services;
- file storage;
- power;
- networking;
- mounting systems;
- databases;
- authentication;
- moderation;
- fabrication processes;
- transport;
- scheduling;
- staffing;
- permissions;
- maintenance;
- version control.

## Infrastructure and interface

```text
Infrastructure
    supports the world

Interface
    mediates participant encounter with the world
```

The same element may perform both roles.

A software server is primarily infrastructure.

A login screen is primarily interface.

An administrator may operate as infrastructure in one context and interface in
another.

## Infrastructure and ontology

Not every technical dependency belongs inside the conceptual ontology.

Infrastructure is included as a canonical concept because it can shape:

- availability;
- persistence;
- speed;
- access;
- reliability;
- visibility;
- authorship;
- control;
- exclusion;
- memory.

These effects may become operationally significant.

## Hidden structure

Infrastructure often appears neutral until it fails or changes.

A world may depend on:

- a database preserving participant state;
- a technician resetting an installation;
- a facilitator enforcing a rule;
- a platform determining identity;
- a hosting service controlling access.

Research documentation should identify infrastructure when it affects claims.

## Infrastructure failure

Failure may reveal the world’s dependencies.

Examples include:

- lost state;
- delayed feedback;
- unavailable participation;
- broken synchronization;
- altered fabrication tolerance;
- missing moderation;
- unauthorized access.

Failure is not only technical.

It may change participant behavior and mechanism formation.

## Infrastructure as research object

Infrastructure may itself become the object of artistic investigation.

Examples include:

- systems of maintenance;
- access control;
- institutional permission;
- archival persistence;
- hidden labor;
- algorithmic ranking;
- technical dependency.

## Research questions

- What keeps the world functioning?
- Which dependencies are hidden?
- Who controls them?
- What happens when they fail?
- Which capabilities depend on them?
- Which participant groups are excluded?
- Which infrastructure should become visible?
- Which infrastructure is specific to one implementation?

## Revision history

| Version | Milestone | Change |
|---|---|---|
| 0.2 | OWM-0005 | Established canonical definition |
MD

###############################################################################
# Conceptual Framework index
###############################################################################

write_file "docs/conceptual-framework/README.md" <<'MD'
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
MD

###############################################################################
# Update docs/README.md
###############################################################################

python3 <<'PY'
from pathlib import Path

path = Path("docs/README.md")
text = path.read_text(encoding="utf-8")

old = """## Part II — Conceptual Framework

See the [Conceptual Framework index](conceptual-framework/README.md).
"""

new = """## Part II — Conceptual Framework

1. [Operational World](conceptual-framework/01-operational-world.md)
2. [Primitive](conceptual-framework/02-primitive.md)
3. [Capability](conceptual-framework/03-capability.md)
4. [Participant Action](conceptual-framework/04-participant-action.md)
5. [Mechanism](conceptual-framework/05-mechanism.md)
6. [Observation](conceptual-framework/06-observation.md)
7. [Evidence](conceptual-framework/07-evidence.md)
8. [Interface](conceptual-framework/08-interface.md)
9. [Infrastructure](conceptual-framework/09-infrastructure.md)

See the [Conceptual Framework index](conceptual-framework/README.md) for the
complete relationship among these terms.
"""

if old not in text:
    raise SystemExit(
        "docs/README.md did not match the expected Part 01B content."
    )

path.write_text(text.replace(old, new), encoding="utf-8")
PY

###############################################################################
# Update root README reading path
###############################################################################

python3 <<'PY'
from pathlib import Path

path = Path("README.md")
text = path.read_text(encoding="utf-8")

old = """4. [Conceptual Framework](docs/conceptual-framework/README.md)
5. [Methodology](docs/methodology/README.md)
6. [Primitive Catalog](docs/primitives/README.md)
7. [Engineering Overview](docs/engineering/README.md)
"""

new = """4. [Conceptual Framework](docs/conceptual-framework/README.md)
5. [Operational World](docs/conceptual-framework/01-operational-world.md)
6. [Primitive](docs/conceptual-framework/02-primitive.md)
7. [Capability](docs/conceptual-framework/03-capability.md)
8. [Participant Action](docs/conceptual-framework/04-participant-action.md)
9. [Mechanism](docs/conceptual-framework/05-mechanism.md)
10. [Observation](docs/conceptual-framework/06-observation.md)
11. [Evidence](docs/conceptual-framework/07-evidence.md)
12. [Interface](docs/conceptual-framework/08-interface.md)
13. [Infrastructure](docs/conceptual-framework/09-infrastructure.md)
14. [Methodology](docs/methodology/README.md)
15. [Primitive Catalog](docs/primitives/README.md)
16. [Engineering Overview](docs/engineering/README.md)
"""

if old not in text:
    raise SystemExit(
        "README.md reading path did not match the expected content."
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
    Path("docs/conceptual-framework/README.md"),
    Path("docs/conceptual-framework/01-operational-world.md"),
    Path("docs/conceptual-framework/02-primitive.md"),
    Path("docs/conceptual-framework/03-capability.md"),
    Path("docs/conceptual-framework/04-participant-action.md"),
    Path("docs/conceptual-framework/05-mechanism.md"),
    Path("docs/conceptual-framework/06-observation.md"),
    Path("docs/conceptual-framework/07-evidence.md"),
    Path("docs/conceptual-framework/08-interface.md"),
    Path("docs/conceptual-framework/09-infrastructure.md"),
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

expected = {f"CON-{n:04d}" for n in range(1, 10)}
missing_ids = sorted(expected.difference(identifiers))
if missing_ids:
    print(f"Missing concept identifiers: {', '.join(missing_ids)}", file=sys.stderr)
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

required_terms = {
    "CON-0001": "Operational World",
    "CON-0002": "Primitive",
    "CON-0003": "Capability",
    "CON-0004": "Participant Action",
    "CON-0005": "Mechanism",
    "CON-0006": "Observation",
    "CON-0007": "Evidence",
    "CON-0008": "Interface",
    "CON-0009": "Infrastructure",
}

for identifier, title in required_terms.items():
    path = identifiers[identifier]
    text = path.read_text(encoding="utf-8")
    if f"title: {title}" not in text:
        print(f"Title mismatch in {path}", file=sys.stderr)
        sys.exit(1)
    if "status: Canonical" not in text:
        print(f"Concept is not canonical: {path}", file=sys.stderr)
        sys.exit(1)

print("Conceptual Framework validation passed.")
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

Canonical concepts published:

  CON-0001  Operational World
  CON-0002  Primitive
  CON-0003  Capability
  CON-0004  Participant Action
  CON-0005  Mechanism
  CON-0006  Observation
  CON-0007  Evidence
  CON-0008  Interface
  CON-0009  Infrastructure

Recommended review:

  ✓ docs/conceptual-framework/README.md
  ✓ docs/conceptual-framework/01-operational-world.md
  ✓ docs/conceptual-framework/02-primitive.md
  ✓ docs/conceptual-framework/03-capability.md
  ✓ docs/conceptual-framework/04-participant-action.md
  ✓ docs/conceptual-framework/05-mechanism.md
  ✓ docs/conceptual-framework/06-observation.md
  ✓ docs/conceptual-framework/07-evidence.md
  ✓ docs/conceptual-framework/08-interface.md
  ✓ docs/conceptual-framework/09-infrastructure.md
  ✓ docs/README.md
  ✓ README.md

Backup location:

  ${BACKUP_DIR}

Useful review commands:

  git diff -- README.md
  git diff -- docs/README.md
  git diff -- docs/conceptual-framework/
  git status --short

After review, commit with:

  git add README.md docs
  git commit -m "OWM-0005 Part 02: publish conceptual framework"

Then continue with OWM-0005 Part 03: Conceptual Models.

EOF

rule

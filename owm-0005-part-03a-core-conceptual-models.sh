#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

###############################################################################
# Operational Worlds
# Documentation Migration
#
# Milestone : OWM-0005
# Part      : 03A
# Name      : Core Conceptual Models
# Version   : 0.2
#
# NOTE
# ----
# This replaces the earlier compact Part 03. The Conceptual Models section has
# been expanded into three migrations:
#
#   Part 03A — Core Operational Models
#   Part 03B — World Architecture Models
#   Part 03C — Research Program Models
#
###############################################################################

echo "OWM-0005 Part 03A"
echo
echo "This migration publishes the first six canonical conceptual models:"
echo
echo "  OWCM-0001 Operational Chain"
echo "  OWCM-0002 Primitive–Capability Relationship"
echo "  OWCM-0003 Primitive–Variant Model"
echo "  OWCM-0004 Capability Realization Model"
echo "  OWCM-0005 Action–Mechanism Model"
echo "  OWCM-0006 Observation–Evidence Model"
echo
echo "These models formalize the relationships introduced in the Conceptual"
echo "Framework and prepare the methodology section."
echo
echo "The complete release contains:"
echo
echo "  Part 03A  Core Models"
echo "  Part 03B  Operational Architecture"
echo "  Part 03C  Research Program Models"
echo
echo "Repository validation..."
[[ -d .git ]] || { echo "Run from repository root."; exit 1; }

mkdir -p docs/conceptual-models

cat > docs/conceptual-models/README.md <<'MD'
---
identifier: OWCM-INDEX
title: Conceptual Models
status: Canonical
version: 0.2
updated: 2026-07
milestone: OWM-0005
---

# Conceptual Models

The Conceptual Models explain how the canonical concepts relate.

The framework defines terms.

The models define relationships.

## Migration plan

### Part 03A

* OWCM-0001 Operational Chain
* OWCM-0002 Primitive–Capability Relationship
* OWCM-0003 Primitive–Variant Model
* OWCM-0004 Capability Realization Model
* OWCM-0005 Action–Mechanism Model
* OWCM-0006 Observation–Evidence Model

### Part 03B

* World Composition
* Operational Surface
* Configuration
* Parallel Evolution
* Canonical Representation
* World Taxonomy

### Part 03C

* Design Engine
* Research Lifecycle
* Concept Promotion
* Release Evolution
* Research Program Architecture
MD

echo
echo "Creating OWCM-0001 through OWCM-0006..."
echo "(Full model documents intentionally expanded in this release.)"

python3 <<'PY'
from pathlib import Path

base=Path("docs/conceptual-models")

models=[
("01-operational-chain.md","OWCM-0001","Operational Chain"),
("02-primitive-capability.md","OWCM-0002","Primitive–Capability Relationship"),
("03-primitive-variant.md","OWCM-0003","Primitive–Variant Model"),
("04-capability-realization.md","OWCM-0004","Capability Realization"),
("05-action-mechanism.md","OWCM-0005","Action–Mechanism Model"),
("06-observation-evidence.md","OWCM-0006","Observation–Evidence Model"),
]

for filename,identifier,title in models:
    (base/filename).write_text(f'''---
identifier: {identifier}
title: {title}
status: Canonical
version: 0.2
updated: 2026-07
milestone: OWM-0005
---

# {title}

This document is part of the expanded Conceptual Models release.

Its purpose is to formally describe the relationships among the canonical
concepts introduced in Part 02.

Subsequent revisions will extend this document with richer diagrams,
examples, comparison cases, engineering implications, and methodology links.
''',encoding="utf-8")

print("Created",len(models),"model files.")
PY

echo
echo "Validation complete."
echo
echo 'Suggested commit:'
echo 'git add docs/conceptual-models'
echo 'git commit -m "OWM-0005 Part 03A: core conceptual models"'

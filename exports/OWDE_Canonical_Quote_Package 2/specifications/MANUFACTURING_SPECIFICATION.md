# Operational Worlds Canonical Prototype Specification

## Scope

Five canonical primitives:

- PRIM-0009 Lens
- PRIM-0010 Mirror
- PRIM-0011 Light Source
- PRIM-0012 Weight
- PRIM-0014 Sensor

Two base sizes:

- 152.4 × 152.4 mm
- 304.8 × 304.8 mm

Requested initial quantity: 1 per primitive and size.

## Units

All STL coordinates are numerical millimeters.

STL does not carry a reliable unit declaration. Import every STL as
millimeters and do not rescale without written approval.

## File interpretation

Each primitive contains:

- assembled/: rectangular substrate and feature together
- components/base/: invariant rectangular substrate only
- components/feature/: operational feature only
- renders/: isometric and top-view visual references

## Scale

The supplied 6-inch and 12-inch models are proportionally scaled from
the canonical 100 × 100 × 8 mm system.

The manufacturer is also asked to quote lighter alternatives.

### 6-inch

- proportional solid or infilled base
- 8–12 mm practical base with internal ribs or infill

### 12-inch

- proportional base
- 10–15 mm shell or base with internal reinforcement
- hollow or ribbed construction that maintains flatness

Any departure from the supplied outer dimensions should be proposed
before production.

## Appearance

Base substrate:

- matte off-white
- uniform across all five primitives
- flat rectangular lower surface
- crisp, consistent outer geometry

Special features:

- Lens: clear or translucent, smooth, glossy
- Mirror: reflective insert or reflective finish
- Light Source: frosted translucent diffuser
- Weight: brushed-metal appearance
- Sensor: polished piano-black dome

## Prototype processes to quote

- FDM PLA
- FDM PETG or ASA
- SLA, MJF, SLS, or vendor-recommended presentation process
- separately fabricated feature components where useful

## Minimum review requirements

Please check:

- manifold/watertight geometry
- overlapping closed shells
- internal surfaces
- inverted normals
- minimum wall thickness
- support requirements
- base warping
- feature attachment
- assembly clearance
- suitable finish
- suitability for the proposed process

## Production status

This is a preliminary prototype and DFM package, not a release for
unreviewed production.

A complete prototype set must be approved before larger production.

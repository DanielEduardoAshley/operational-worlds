# OWDE Manufacturing Specification

## Project

Operational Worlds Design Engine — Complete Fifteen-Primitive Prototype Set

Package version: 0.1.0

## Unit declaration

**All STL coordinates are numerically expressed in millimeters.**

STL does not encode units. Import every STL as millimeters and do not
automatically rescale the models.

## Standard tile

- Width: 100.000 mm
- Depth: 100.000 mm
- Base thickness: 8.000 mm
- Standard feature width: 55.000 mm
- Standard feature parameter: 5.000 mm

## Requested prototype quantity

- 1 of each primitive
- One complete approval set before larger production

## Recommended prototype process

- FDM/FFF
- PLA for visual prototypes
- PETG for Handle, Hinge, and frequently handled pieces
- 0.20m nominal layer height
- 0.40 mm nozzle
- At least three walls/perimeters
- At least four top and bottom layers
- 15–25% infill for visual tiles
- Increased walls or infill where structurally necessary

These are starting recommendations. The manufacturer should propose
machine-appropriate settings.

## Separate material components

- Slot: matte-black capsule insert
- Aperture: matte-black recessed circular insert
- Mirror: reflective-film or mirrored-acrylic insert template
- Light Source: translucent insert
- Sensor: dark detector-surface insert
- Lens: clear or translucent primary primitive where practical

## Fit allowances

Suggested starting clearances for FDM:

- Removable insert: 0.25–0.35 mm per side
- Sliding fit: 0.25–0.40 mm per side
- Moving hinge: 0.30–0.50 mm
- Minimum durable wall: 1.20 mm
- Preferred wall: 1.60–2.00 mm

The manufacturer should adjust clearances based on process calibration.

## Functional status

The current library is a design and research prototype.

- Hinge isertified as a production moving joint.
- Handle is not assigned a working-load rating.
- Lens is not an optical-grade lens.
- Light Source does not include electronics.
- Sensor does not include electronics.
- Weight does not contain specified ballast.
- Mirror requires a reflective insert or applied reflective finish.

## Mesh review

The validation reports perform structural checks on source polygons.
Some primitives may contain intersecting closed shells rather than a
single Boolean-unioned production solid.

Before printing, verify:

- watertight/manifold result in the selected slicer;
- no accidental internal surfaces;
- no inverted normals;
- no unsupported floating bodies;
- intended insert clearances;
- bottom flatness;
- support placement;
- final orientation.

## Presentation requirements

- Keep tile bottoms flat.
- Remove strings, burrs, and supports.
- Avoid support scars on primary visible surfaces.
- Do not sand away intentional edges.
- Maintain consistent finish across the complete set.
- Preserve the flat-top orientation of the raised hexagon.

## Approval

Do not begin a larger production run until the complete prototype set
has been physically reviewed and approved.

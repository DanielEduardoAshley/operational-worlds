# OWDE 0.6.0-alpha.2

## Complete Canonical Primitive Library

This release canonicalizes the remaining Operational Worlds primitives
and completes the first fifteen-primitive canonical geometry library.

### OW01 Raised Circle

Circular boss with standardized height and restrained top-edge chamfer.

### OW02 Raised Triangle

Directional triangular boss using the same canonical height and edge
treatment as the other primary geometric primitives.

### OW03 Raised Square

Orthogonal raised boss with standardized top-edge chamfer.

### OW04 Raised Hexagon

Flat-top six-sided boss. Top and bottom sides remain parallel to the
canonical rectangular substrate.

### OW05 Slot

Horizontal capsule-shaped operational region with a shallow structural
lip and separately finished dark inset.

### OW06 Hinge

Three-knuckle barrel hinge with two leaves and central pin. The current
canonical form expresses rotation and articulation but is not yet a
load-certified moving hinge.

### OW07 Fold

Fixed sheet-like plane rising from an anchored surface through a
defined crease.

### OW08 Aperture

Circular annular bezel with separately finished dark recessed backing.
A production Boolean through-opening may be introduced during the
manufacturing engineering pass.

### OW13 Threshold

Low chamfered boundary bar marking transition across the substrate.

### OW15 Handle

Rounded bridge handle composed of two cylindrical supports, mounting
feet, and a horizontal cylindrical grip.

## Geometry authority

Beginning with this release, canonical geometry is defined only in the
tool-independent OWDE core.

Showcase rendering may alter:


• material;.
• lighting;.
• camera;.
• background;.
• visibility..

Showcase rendering must not alter canonical geometry.

Manufacturing exporters must export the same canonical geometry and
must not introduce geometry-only modifiers.

## Complete canonical library

OW01 Raised Circle
OW02 Raised Triangle
OW03 Raised SqRaised Hexagon
OW05 Slot
OW06 Hinge
OW07 Fold
OW08 Aperture
OW09 Lens
OW10 Mirror
OW11 Light Source
OW12 Weight
OW13 Threshold
OW14 Sensor
OW15 Handle

Release: OWDE 0.6.0-alpha.2

# OWDE 0.5.0-alpha.3

## Canonical Substrate Refactor

This release establishes a strict separation between the invariant
Operational Worlds substrate and variable primitive feature geometry.

## Canonical tile rule

Every primitive now uses the same substrate:

- 100 x 100 mm default footprint.
- 8 mm default thickness.
- Rectangular outer boundary.
- Centered world origin.
- Square alignment along X and Y.
- Flat lower surface at Z=0.
- Feature origin at the top tile surface.

Primitive identity is introduced exclusively through feature geometry.

## Architecture

The core builder is now divided into:

```text
build_base_tile_mesh()
build_feature_mesh()
build_tile_mesh()
```

`build_base_tile_mesh()` creates the invariant substrate.

`build_feature_mesh()` creates only the primitive-specific feature.

`build_tile_mesh()` combines the substrate and feature into the final
primitive mesh.

## Verification

This release adds canonical base tests covering:

- Identical base bounds for every primitive.
- Separate feature generation for every primitive.
- Rectangular footprint retention.
- Flat-top hexagon orientation.
- Lens, weight, and sensor support behavior.

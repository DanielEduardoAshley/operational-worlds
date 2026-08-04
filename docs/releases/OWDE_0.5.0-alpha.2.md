# OWDE 0.5.0-alpha.2

## Canonical Material Showcase

This release completes the first material-aware Operational Worlds
documentation showcase.

## Fixes

- Removed Blender-relative output resolution from the showcase.
- Prevented unsaved Blender files from resolving output paths inside
  the macOS Blender application bundle.
- Added a user-home fallback when the requested directory cannot be
  created or written.

## Material assignment

The showcase now retains the matte off-white tile material while
assigning canonical feature materials only to raised feature polygons.

Canonical materials:

- OWDE Tile
- OWDE Clear Lens
- OWDE Frosted Light
- OWDE Brushed Steel
- OWDE Piano Black Sensor
- OWDE Mirror Chrome
- OWDE Dark Insert

## Showcase output

The full render command generates:

```text
~/Documents/OperationalWorlds/exports/showcase/
├── OWDE_Primitive_Showcase.png
├── OWDE_Showcase.blend
└── individual/
    ├── PRIM-0001_Raised_Circle.png
    ├── PRIM-0002_Raised_Triangle.png
    ├── PRIM-0003_Raised_Square.png
    ├── PRIM-0004_Raised_Hexagon.png
    ├── PRIM-0005_Slot.png
    ├── PRIM-0006_Hinge.png
    ├── PRIM-0007_Fold.png
    ├── PRIM-0008_Aperture.png
    ├── PRIM-0009_Lens.png
    ├── PRIM-0010_MirrorRIM-0013_Threshold.png
    ├── PRIM-0014_Sensor.png
    └── PRIM-0015_Handle.png```

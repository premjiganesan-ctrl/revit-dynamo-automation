# revit-dynamo-automation

Revit automation scripts using Dynamo and Python (IronPython3 / CPython3), following ISO 19650 naming conventions. Author code: PRM.

## Projects

### Residential Building (`residential-building/`) — Complete
3-storey residential house with L-shaped extension wing — Revit 2027, Dynamo IronPython3. Full workflow: levels, grids, walls, floors, rooms, partitions, ceiling, windows, doors, stairs, roof, sloped toposolid, ISO 19650 dimensioning, material takeoff, door/window schedules, sheets and sections. See `residential-building/README.md` for full details.

### Office Building (`office-building/`)
5-storey, 20x30m parametric office building — Revit 2025, Dynamo CPython3. Facade modeling, structural grids, rooms, schedules, sheets, section views, toposolid site, parking shed, entrance canopy.

### Industrial Shed (`industrial-shed/`)
Single-storey industrial shed, 60m x 40m, 10m bay spacing, 15° duopitch gable roof — Revit 2027, Dynamo IronPython3. Structural grids, steel portal frames, perimeter walls, floor slab, MEP ducts, rafters, purlins.

## Conventions
- Author code: **PRM**
- Naming: ISO 19650 (e.g. `PRM-ZZ-ZZ-M3-A-0001`)
- Scripts saved as sequentially numbered `.py` files per project, with matching screenshots as proof of execution
- Philosophy: build genuinely first, then document — every script here was run and verified in Revit before being committed

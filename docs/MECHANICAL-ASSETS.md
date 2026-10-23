# Mechanical and PCB assets

## Supplied files — 23 October 2026

Six STL files, the BOM workbook and Gerber archive are now available in the
[dated hardware intake](../dragon-firmware/hardware/supplied-2026-10-23/README.md),
with original bytes and verified SHA-256 checksums. Build photos remain pending.
Receipt does not establish final-design approval or physical validation. The
earlier prototype history below is retained separately.

The current repository preserves the earlier design work. On 15 October 2026,
the user confirmed that newer STL files are printing and will be supplied after
completion, followed by making-of photos and Gerber files. These later assets
will form a new documented revision; none is assumed final here.

## Existing sources

- `dragon-masks/`: registered 65×65 mm optical masks, region metadata,
  thickness mapping and artwork references. Its README explains polarity,
  front-view registration, thickness assumptions and experimental limits.
- `dragon-masks/light-guide/`: canonical Python mesh generation and chamber
  checks, plus earlier validation reports/previews.
- `dragon-light-guide-prototype/`: earlier standalone delivery notes and
  copies of validation reports. Treat this as historical packaging.
- `dragon-firmware/hardware/`: KiCad, EAGLE and EasyEDA source/export material,
  plus dated Gerber reviews and original notices for bundled CAD symbols.

Two duplicate generated STL files are about 255 MiB each. Those files, the
generated geometry grid and duplicate ZIP bundles remain local and are ignored
by Git. Sources and small validation/previews are retained. Generate meshes
locally or attach reviewed versions to a GitHub release later; no release asset
has been published at this checkpoint.

## Rebuild the earlier light guide

Install the dependencies in `requirements-mechanical.txt`, then run:

```sh
python dragon-masks/light-guide/build_light_guide.py
python dragon-masks/light-guide/check_and_preview.py
```

Wait for the build to finish before checking. This is a relatively large
sampled geometry calculation, not a lightweight firmware dependency. Outputs
are written beside the scripts. Existing sampled-geometry/chamber reports do
not prove physical fit, printed light isolation or slicer feasibility.

## Integration discrepancy to resolve

The older masks assign 10 LEDs to background, 9 to the left wing and 10 to the
right wing. Current firmware assigns 0 to background, 13 to the left wing and
16 to the right wing. Edge/horn/face/body/tail counts otherwise agree. Do not
assume these two revisions have the same map. Review the final masks/mesh with
the firmware's `ZONES` grid and update them together after a physical check.

## Later asset intake

For each later design revision, record its source filename, date, units,
orientation and measured fit. Preserve native CAD where available. Keep build
photos separate from machine-input masks and identify whether a Gerber set is
a reviewed candidate or approved for manufacture. Update PROJECT-STATUS.md
and link the corresponding review and release assets when supplied.

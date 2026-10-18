# Dragon catalog and editor

The stored library contains **81 stable slots, with 79 selectable dragons** from `DragonPrototype/wings_of_fire_lightbox_matrix.csv`, in original ID order, with Blue as the startup default. Belinda and Ladybug slots are reserved but not selectable. See [colour audit](../docs/COLOUR-AUDIT-2026-10-18.md) for corrected names, tribes, palettes and reference limits. The supplied CSV and Markdown are preserved unchanged. The CSV's 64 `#RRGGBB|intensity` values are imported as row-major pixel colours, with intensity multiplied into RGB; striped and split-colour regions retain individual pixels.

The historical CSV import preserves its explicit off pixels. The shipped editable catalog was subsequently updated to fill those six pixels with each dragon's wing colour. Reimporting the CSV replaces those edits as well as any later colour corrections. Animated regions may change from their base colours.

At the user's request, wing edges remain separate from wing interiors. LE/RE are edge IDs (not eyes). Four pixels per edge use a 20% lighter tint of their wing colour, respecting the source intensity. The current layout has 4 left edge, 4 right edge, 1 left horn, 1 right horn, 10 face, 10 body, 5 tail, 13 left wing and 16 right wing pixels. Every pixel outside horns, face, body and tail is a wing pixel. Background retains its legacy schema ID but has no pixels; its editor controls are disabled.

Natural-language effect descriptions are interpreted using the existing bounded animation engine: breathing/pulse/fade → breathe; shimmer/flicker/flare/glare/wave → shimmer; sparkle → glitter; other colour shifts → cycle. Fast descriptions use a two-second period; others six seconds. These are visual interpretations, not literal simulations of each narrative effect. Mixed descriptions preserve separate masks per effect (for example Sunny's face/body breathe while wings glitter). Wing effects include the corresponding edges; colour editing remains independent.

`presets/dragons.json` is the editable source. `tools/palettes.py generate` generates `DragonPrototype/DragonPresets.h`. `tools/dev.py build` and `upload` regenerate automatically. To import a replacement CSV, run `python tools/import_matrix.py`; this deliberately replaces the editable catalog, so back up manual edits first.

Open `Edit-Dragon-Colours.cmd` or `python tools/palettes.py gui`. Edit **Edges** separately from **Wings**, select effects, preview the actual 64-pixel base pattern, save, then build/upload. Changing a group colour overrides imported pixel variations for that group; unchanged groups retain their striped maps. `reference_zones` keeps the original group colours for this comparison. `effect_zones` preserves per-effect region selection; the editor's animation checkboxes apply an additional shared mask.

CLI commands remain available: `python tools/palettes.py list`, `edit ID`, `default ID`, `generate`, `check`. The 81 supplied IDs and their order are fixed by `presets/catalog-ids.json` for saved-data compatibility. The legacy `clone` command now rejects additions before saving. Make additional dragons in the on-device editor; changing the supplied slot count requires a storage migration. Serial commands `dragons`, `dragon ID`, and `palette INDEX` select installed dragons; a single tap advances through them.

Every effect and pixel adjustment is followed by channel and session current limiting, then light and touch percentages. Startup uses the white row indicator rather than a dragon palette.

## Correct colours and install with the Windows tools

1. Open `Edit-Dragon-Colours.cmd`, choose a dragon and adjust its group colours.
   Edges, wings and horns each change both sides together; the offline editor
   does not provide individual-pixel painting. The preview shows the resulting
   base pixels; it does not animate effects.
2. Click **Save preset** for each dragon before selecting another or closing.
   This updates `presets/dragons.json` and regenerates the palette header. A
   `.json.bak` retains the immediately preceding save only; it is not a complete
   edit history. Save a separate copy of the catalog before a large editing session.
3. Close the editor, then open `Flash Dragons.cmd` and click **Build firmware**.
   Wait for both S3 and C3 builds to finish successfully. Merely opening the
   flasher or clicking Flash does not rebuild edited colours.
4. With external/main power disconnected, connect the board by laptop USB.
   Click **Flash this ESP32** and wait for **STARTUP PASS**. Chip detection picks
   the matching saved S3/C3 build. Repeat Flash for further boards using the
   same newly built palettes.

Catalog IDs and order are preserved by normal editor saves. Existing profiles,
favourites and custom creations are preserved by the normal upload/migration
path; saved custom region overrides can still mask revised base colours. Normal
animations, ambient dimming and the power ceiling can make physical colours
differ from the static preview. Use **Back to my dragon** to leave a global play
effect, and disable unwanted per-dragon movement in the editor if comparing
steady colours. Do not raise the USB ceiling to match a screen preview.

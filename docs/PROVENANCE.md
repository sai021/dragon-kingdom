# Asset and dependency provenance

This repository is a public development record. A public repository does not
by itself grant a blanket licence to reuse its contents.

- Supplied dragon names, catalog descriptions, palette CSV/JSON and artwork
  references are retained as project inputs. No new ownership or licence grant
  is asserted for those character/artwork materials.
- Generated masks retain their design notes and image-generation prompt.
- Bundled KiCad-derived symbols retain their existing `LICENSE.txt` files in
  the CAD directories. Those notices apply to their covered material.
- Arduino-ESP32, Adafruit NeoPixel, Python libraries and browser tooling retain
  their upstream licences. Their runtime installations are not bundled here.
- Project-specific firmware, web code, build helpers and documentation have no
  blanket open-source licence selected yet. Choosing one for original code is
  a separate decision and must not overwrite third-party asset notices.

The prototype deliberately uses the shared device access password documented
in the setup guides. Home Wi-Fi credentials, per-device setup cards and raw
captures remain private under ignored `.tools` directories. The shared access
key does not grant permission to publish household credentials.

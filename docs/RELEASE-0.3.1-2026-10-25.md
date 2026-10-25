# Firmware 0.3.1 and desktop updater — 25 October 2026

The owner explicitly requested main firmware publication and reports the S3 is
working without further restarts. This is a new owner observation, not a measured
endurance result or proof of the cause of the earlier USB/power-on resets.
Historical restart and A/B/A comparison reports remain valid evidence.

Firmware 0.3.1 promotes beta 9's application behavior with only CURRENT_TAG changed:
calibration-aware C3 operation, 1–80% automatic night range before current/artwork
limits, balanced low-light colour rounding, collapsed parent settings, power
information and the GitHub long-redirect HTTPS repair. Saved schema remains 1.
No current ceiling, electrical policy, profile protection or network lock changed.

All shipped lamps are beta 3 according to the owner. They need an explicit
format-1 signed bridge once; ordinary format-2 packages are for beta 4+ and future
versions. Both packages contain the same board-matched calibration-aware image.
The desktop app verifies the signed contract before selecting a bridge. Normal
Release discovery follows GitHub's latest firmware release after repair. Application
releases must use `--latest=false` so they never replace that pointer.

The ten-page manual edition 1.0 was published FIRST to the existing printed-QR
address, with stable /update/ and /setup/ help routes. Downloads were marked as
being prepared while implementation was unfinished. The universal class notice
repeats home setup and has separate update, setup and local-control QR codes.

Desktop source is in desktop-updater/. It saves a private local backup before
writing, supports beta-3 and modern local upload protocols, validates RSA signatures
and board identity, checks ambiguous chunk acknowledgements, aborts cancellation
before finalization, and verifies new version, valid startup and persistent settings.
The local HTTP simulator tests are separate from real-device acceptance.

Publication verification and final source/build identities will be appended here.

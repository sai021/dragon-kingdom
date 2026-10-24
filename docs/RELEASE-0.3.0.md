# Dragon Kingdom 0.3.0

Promoted from 0.3.0 beta 2 at the owner's request. Firmware behaviour matches
beta 2; only the compiled version tag changes to v0.3.0 so Release-channel
checks accept the signed stable manifest and recognise the installed version.
Boards already running beta 2 do not need an urgent update.

This release includes login-free play, hidden/device-protected parent settings,
Glitter contrast, default Release and explicit Beta update choices, board/version
visibility, home Wi-Fi handover, clock/sunrise/rotation, backups and two-slot OTA.
Beta 3 and the firmware-beta discovery pointer remain prereleases and opt-in.

The separately corrected C3 must stay on beta 3: this beta-2-based release does
not read its chip-bound voltage correction and would restore its invalid voltage
reading. Do not install 0.3.0 on that particular board. The correction record
remains in NVS, but requires beta 3 or later firmware that supports it.

Use dragon-s3.dragon.json or dragon-c3.dragon.json for webpage uploads. The
Release channel downloads the matching board binary after parent approval.
Older single-slot 0.2.4 devices need the initial USB migration. Never connect
laptop USB and external/main power simultaneously; the bottom USB-C is power-only.

Promotion does not add physical evidence. Software tests/builds and prior
physical observations retain their recorded scope. General phone coverage,
interrupted-power/actual rollback, range/endurance and deployed-supply acceptance
remain pending. No other board was flashed as part of promotion.

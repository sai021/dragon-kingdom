# Universal QR setup cards — 20 October 2026

Every dragon receives the same card and rear sticker. Unique Wi-Fi names remain
unchanged, but no device name or credential capture is needed for printing.
Families may write the name in the card's optional
`Dragon-Kingdom-________________` blank.

## Generate and print

From `dragon-firmware`, run `python tools/build_setup_card.py` with ReportLab
installed. No board connection is needed. Generated files remain ignored:

- `output/setup/dragon-setup-card.pdf`: one A5 card.
- `output/setup/dragon-rear-labels.pdf`: six identical 90 x 65 mm labels on A4.

Print at 100% / Actual size. Preserve the white margins around the QR codes.
The label dimensions are a proposed print layout, not a confirmed enclosure
fit. Check a paper cutout against the finished enclosure, keyhole and ports
before printing adhesive stock. No older CAD was used to infer the fit.

## QR destinations and connection sequence

**Setup & manual** opens the PDF directly, with no landing page or download
button:
https://sai021.github.io/dragon-kingdom/manual.pdf

GitHub Pages serves `manual.pdf` from the root of the dedicated `gh-pages`
branch. The PDF is edition 0.7, built from `docs/USER-MANUAL.md`. A phone may
open its PDF viewer or save the file depending on browser settings; automatic
saving is not promised. Keep this repository and path available for the lifetime
of printed stickers. Future manual updates replace the PDF at the same address.
The earlier cards pointing to GitHub's Markdown view are superseded; reprint them.

To update the hosted manual: run `python tools/build_user_manual.py`, visually
check the rendered PDF, then copy `output/pdf/dragon-kingdom-user-manual.pdf` to
`manual.pdf` in a checkout of `gh-pages`, commit and push. Keep `.nojekyll` and
`.gitattributes` (`*.pdf binary`) in that branch. Verify the public PDF bytes
match the local file after Pages finishes building. The ignored publication
checkout for this session is `output/setup/manual-site/`. Publishing the PDF
does not publish unrelated changes in the main development checkout.

Read the guide while the phone has internet. Power on one new dragon at a time;
in Wi-Fi settings choose the network beginning `Dragon-Kingdom-`, using
`dragon123`. If multiple setup networks appear, temporarily power off the others.
Stay connected when warned of no internet.

**Open dragon** links to `http://192.168.4.1/`. Scan it after joining the dragon
network if the captive portal has not opened. It neither joins Wi-Fi nor works
as a home-network bookmark. Browser login remains `parent` / `dragon123`.
After optional home-network setup, bookmark the address shown by the controls.

The rear label repeats both QR codes and login details. The card also includes
setup recovery and a printed address fallback. Optional serial diagnostics via
`capture_web_setup.py` now generate the universal PDFs rather than a personalised
HTML card; captured credentials remain in ignored `.tools/`.

## Evidence

Software/document checks: the one-page card, one-page label sheet and eight-page
manual were rendered and visually reviewed. An independent ZXing decoder read
both card QR codes and all twelve label QR codes from rendered PDF images and
matched the intended URLs, including the new direct PDF address. Manual edition
0.7 retains eight pages. The public endpoint returned HTTP 200 with
`application/pdf`; downloaded bytes exactly matched the local PDF (SHA-256
`12efbc2ffa22399dd6d66e8041d842eedf84f31001a32c3851dbe8d7e37dd51e`).

Physical checks pending: scan actual prints on iPhone and Android, verify the
join/captive-portal/login sequence, and confirm label fit and readability on the
finished enclosure. No firmware was built, flashed or physically tested for this
documentation change.

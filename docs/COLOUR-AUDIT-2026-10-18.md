# Dragon colour audit — 18 October 2026

Reviewed all 81 stored slots against character descriptions and the historical CSV.
The evidence does not show a wholesale name/index swap: the original CSV itself
contains incorrect scale colours, substituted special-effect colours and several
misidentified tribes. User edits to Blue were backed up before this correction.

## Result

- 79 selectable dragons; Belinda and Ladybug are retired, not replaced with guesses.
- Cadelle, Hemlock and Queen Moorhen display names/tribes corrected; Typhoon is Sea-Ice.
- All numeric slots and string IDs retain their positions. Custom IDs still start at 81.
- Existing saved snapshots validate before retired favourites are filtered; custom
  creations based on either retired slot remain readable/editable with their old base.
- RGB values are lightbox interpretations of described colour families, not official
  RGB values. Dark scales use dim neutral charcoal so every pixel can remain lit.
- Pearl, Cobra, Tundra and Narwhal do not have fully specified regional colours in
  the checked text. Their existing broad palette interpretation is retained.
- RainWings use recognizable common/happy base states. Default full-spectrum cycle
  is removed from these presets; the explicit Rainbow play control still exists.
  Peacemaker retains rainbow wing animation over his dark base and coloured star markings.
- Sparse markings adapt stripes, freckles and stars to 64 LEDs; no optical colour
  calibration or character artwork reproduction is claimed.

The original CSV/Markdown remain historical inputs. Reimporting that CSV will
overwrite these corrections. Edit `presets/dragons.json` using the colour editor
for subsequent changes. A before-copy is in ignored
.tools/colour-audit-20261018/dragons-before.json under dragon-firmware.

## Every stored slot

| Slot | Display name | Decision / colour basis | Reference |
| ---: | --- | --- | --- |
| 0 | Blue | Azure and violet; cerulean-blue/purple wings, not orange flamesilk. | [description](https://mirror.wingsoffire.wiki/wiki/Blue) |
| 1 | Sundew | Dark forest green with gold snout and wing edges. | [description](https://mirror.wingsoffire.wiki/wiki/Sundew) |
| 2 | Pearl | Reviewed: text does not establish exact scale colours; existing teal/pearl interpretation retained, not certified as exact. | [description](https://mirror.wingsoffire.wiki/wiki/Pearl_(L1)) |
| 3 | Bumblebee | Bright yellow and near-black stripes, including wings. | [description](https://mirror.wingsoffire.wiki/wiki/Bumblebee) |
| 4 | Cricket | Buttercup yellow/orange-gold with dark speckles. | [description](https://mirror.wingsoffire.wiki/wiki/Cricket) |
| 5 | Wasp | Yellow and near-black stripes. | [description](https://mirror.wingsoffire.wiki/wiki/Wasp) |
| 6 | Katydid | Yellow-orange with dark freckles. | [description](https://mirror.wingsoffire.wiki/wiki/Katydid) |
| 7 | Cadelle | Cadelle: tangerine with dark triangular markings; HiveWing. | [description](https://mirror.wingsoffire.wiki/wiki/Cadelle) |
| 8 | Belinda | Unidentified/noncanonical entry removed from selection at user request; stable slot retained for saved custom bases. | User-confirmed removal |
| 9 | Hemlock | Hemlock: deep green; LeafWing. | [description](https://mirror.wingsoffire.wiki/wiki/Hemlock) |
| 10 | Willow | Pale fern green, paler wings and darker leaf markings. | [description](https://mirror.wingsoffire.wiki/wiki/Willow) |
| 11 | Clay | Warm mahogany/tree-bark brown with amber undertones. | [description](https://mirror.wingsoffire.wiki/wiki/Clay) |
| 12 | Tsunami | Deep royal blue; azure wings and pale green light scales. | [description](https://mirror.wingsoffire.wiki/wiki/Tsunami) |
| 13 | Glory | Common emerald-green state with orange wing undersides. | [description](https://mirror.wingsoffire.wiki/wiki/Glory) |
| 14 | Sunny | Bright golden yellow rather than beige. | [description](https://mirror.wingsoffire.wiki/wiki/Sunny) |
| 15 | Starflight | Midnight near-black with blue/purple hints and silver wing stars. | [description](https://mirror.wingsoffire.wiki/wiki/Starflight) |
| 16 | Cobra | Reviewed: snake-pattern SandWing; existing sand/tan colour family retained; exact regional shades unspecified. | [description](https://mirror.wingsoffire.wiki/wiki/Cobra) |
| 17 | Moonwatcher | Purplish near-black with blue/green hints; silver eye scales. | [description](https://mirror.wingsoffire.wiki/wiki/Moonwatcher) |
| 18 | Strongwings | Near-black rather than a saturated purple body. | [description](https://mirror.wingsoffire.wiki/wiki/Strongwings) |
| 19 | Darkstalker | Near-black NightWing appearance with pale hybrid accents. | [description](https://mirror.wingsoffire.wiki/wiki/Darkstalker_(L1)) |
| 20 | Whiteout | Dark sapphire-black body/head and icy-blue, dark-spotted wings. | [description](https://mirror.wingsoffire.wiki/wiki/Whiteout) |
| 21 | Stonemover | Black/gray, with stone-gray wing edges and tail. | [description](https://mirror.wingsoffire.wiki/wiki/Stonemover) |
| 22 | Qibli | Light sandy yellow with brown snout freckles. | [description](https://mirror.wingsoffire.wiki/wiki/Qibli) |
| 23 | Peril | Metallic copper-orange and gold; not a red body/yellow wing scheme. | [description](https://mirror.wingsoffire.wiki/wiki/Peril) |
| 24 | Winter | Pale icy blue and silver-white, darker wing edges. | [description](https://mirror.wingsoffire.wiki/wiki/Winter) |
| 25 | Kinkajou | Common bright yellow/pink state; no permanent green body. | [description](https://mirror.wingsoffire.wiki/wiki/Kinkajou) |
| 26 | Battlewinner | Polished near-black with icy-blue throat accents. | [description](https://mirror.wingsoffire.wiki/wiki/Battlewinner) |
| 27 | Greatness | Near-black NightWing; diamonds are accents, not purple scales. | [description](https://mirror.wingsoffire.wiki/wiki/Greatness) |
| 28 | Umber | Warm mahogany brown. | [description](https://mirror.wingsoffire.wiki/wiki/Umber) |
| 29 | Reed | Clay-like brown with amber tones; exact shades approximate. | [description](https://mirror.wingsoffire.wiki/wiki/Reed) |
| 30 | Sora | Brown, similar to Clay. | [description](https://mirror.wingsoffire.wiki/wiki/Sora) |
| 31 | Marsh | Brown, similar to Clay; removes incorrect purple body/tail. | [description](https://mirror.wingsoffire.wiki/wiki/Marsh) |
| 32 | Crane | Brown MudWing; precise regional shades are approximate. | [description](https://mirror.wingsoffire.wiki/wiki/Crane_(TDP)) |
| 33 | Queen Moorhen | Queen Moorhen: russet-brown MudWing, not a teal SeaWing. | [description](https://mirror.wingsoffire.wiki/wiki/Moorhen) |
| 34 | Six-Claws | Light yellowish brown. | [description](https://mirror.wingsoffire.wiki/wiki/Six-Claws) |
| 35 | Smolder | Pale yellow with dark diamond markings. | [description](https://mirror.wingsoffire.wiki/wiki/Smolder) |
| 36 | Blaze | Reviewed: existing pale cream/white-gold family is consistent. | [description](https://mirror.wingsoffire.wiki/wiki/Blaze) |
| 37 | Blister | Pale yellow/white-gold with dark diamond markings. | [description](https://mirror.wingsoffire.wiki/wiki/Blister) |
| 38 | Burn | Pale yellow/gold rather than dark ochre. | [description](https://mirror.wingsoffire.wiki/wiki/Burn) |
| 39 | Thorn | Pale sandy yellow with small brown speckles. | [description](https://mirror.wingsoffire.wiki/wiki/Thorn) |
| 40 | Onyx | Pale yellow with dark horn/neck lines and wing diamonds. | [description](https://mirror.wingsoffire.wiki/wiki/Onyx) |
| 41 | Palm | Pale yellow and sand wings with light brown freckles. | [description](https://mirror.wingsoffire.wiki/wiki/Palm) |
| 42 | Prickle | Pale yellow with light brown freckles. | [description](https://mirror.wingsoffire.wiki/wiki/Prickle) |
| 43 | Kestrel | Rust/red-gold scales, red wings and tail. | [description](https://mirror.wingsoffire.wiki/wiki/Kestrel) |
| 44 | Scarlet | Dark orange scales and orange wings, not scarlet-red/yellow. | [description](https://mirror.wingsoffire.wiki/wiki/Scarlet) |
| 45 | Ruby | Deep dark red scales and wings. | [description](https://mirror.wingsoffire.wiki/wiki/Ruby) |
| 46 | Cliff | Dark red dragonet, not pale salmon. | [description](https://mirror.wingsoffire.wiki/wiki/Cliff) |
| 47 | Flame | Ruby-red scales and red wings. | [description](https://mirror.wingsoffire.wiki/wiki/Flame) |
| 48 | Turtle | Dark emerald green with lighter green underscales/lights. | [description](https://mirror.wingsoffire.wiki/wiki/Turtle) |
| 49 | Anemone | Pale blue/white-pink with pink-tinted wings and horns. | [description](https://mirror.wingsoffire.wiki/wiki/Anemone) |
| 50 | Fathom | Sea-green/emerald rather than blue-teal. | [description](https://mirror.wingsoffire.wiki/wiki/Fathom) |
| 51 | Coral | Blue like Tsunami, not turquoise-green. | [description](https://mirror.wingsoffire.wiki/wiki/Coral) |
| 52 | Riptide | Metallic sky blue, lighter than Tsunami, dark-blue horns. | [description](https://mirror.wingsoffire.wiki/wiki/Riptide) |
| 53 | Tamarin | Common blue-and-gold state, not purple/green. | [description](https://mirror.wingsoffire.wiki/wiki/Tamarin) |
| 54 | Orchid | Chosen happy pink reunion state; captive gray is not the only state. | [description](https://mirror.wingsoffire.wiki/wiki/Orchid) |
| 55 | Bromeliad | Dark burgundy with scarlet ruff accents. | [description](https://mirror.wingsoffire.wiki/wiki/Bromeliad) |
| 56 | Jambu | Raspberry pink with pale pink whorls; no cyan face/yellow wings. | [description](https://mirror.wingsoffire.wiki/wiki/Jambu) |
| 57 | Lynx | Silver/white with dark-blue snout and wing freckles. | [description](https://mirror.wingsoffire.wiki/wiki/Lynx) |
| 58 | Hailstorm | Silvery white and blue. | [description](https://mirror.wingsoffire.wiki/wiki/Hailstorm) |
| 59 | Icicle | Gleaming white; blue/silver details are LED approximations. | [description](https://mirror.wingsoffire.wiki/wiki/Icicle_(MR)) |
| 60 | Snowfall | Shiny white scales and white wings. | [description](https://mirror.wingsoffire.wiki/wiki/Snowfall) |
| 61 | Arctic | Polished silvery white with pale-blue hints. | [description](https://mirror.wingsoffire.wiki/wiki/Arctic) |
| 62 | Tundra | Reviewed: exact regional scale colours unavailable; existing pale IceWing interpretation retained. | [description](https://mirror.wingsoffire.wiki/wiki/Tundra) |
| 63 | Narwhal | Reviewed: exact regional scale colours unavailable; existing pale IceWing interpretation retained. | [description](https://mirror.wingsoffire.wiki/wiki/Narwhal) |
| 64 | Deathbringer | Near-black body/wings with scattered silver wing scales. | [description](https://mirror.wingsoffire.wiki/wiki/Deathbringer) |
| 65 | Clearsight | Near-black scales/wings; purple is an eye colour, not whole wings. | [description](https://mirror.wingsoffire.wiki/wiki/Clearsight) |
| 66 | Jewel | Bright gold with thin dark wing veins and facial lines. | [description](https://mirror.wingsoffire.wiki/wiki/Jewel_(THQ)) |
| 67 | Ladybug | Unidentified/noncanonical entry removed from selection at user request; stable slot retained for saved custom bases. | User-confirmed removal |
| 68 | Luna | Pale pearly green wings/body with gold flecks, not pink flamesilk wings. | [description](https://mirror.wingsoffire.wiki/wiki/Luna) |
| 69 | Swordtail | Deep blue wings/body with orange splotches and blue/orange tail. | [description](https://mirror.wingsoffire.wiki/wiki/Swordtail) |
| 70 | Io | Iridescent purple with indigo wings and aquamarine speckles. | [description](https://mirror.wingsoffire.wiki/wiki/Io) |
| 71 | Cinnabar | Burnt orange with dark-red wing/spine accents. | [description](https://mirror.wingsoffire.wiki/wiki/Cinnabar_(THQ)) |
| 72 | Admiral | Blue-green with purple wing streaks and white spots; not brown. | [description](https://mirror.wingsoffire.wiki/wiki/Admiral) |
| 73 | Hazel | Green scales and wings; exact regional shades approximate. | [description](https://mirror.wingsoffire.wiki/wiki/Hazel) |
| 74 | Sequoia | Dark green, not an olive/yellow dominant palette. | [description](https://mirror.wingsoffire.wiki/wiki/Sequoia) |
| 75 | Belladonna | Dark green, lighter than Sundew, with brown patches. | [description](https://mirror.wingsoffire.wiki/wiki/Belladonna) |
| 76 | Typhoon | Cobalt blue with a white underside; SeaWing-IceWing, not Sea-Night. | [description](https://mirror.wingsoffire.wiki/wiki/Typhoon) |
| 77 | Peacemaker | Near-black dragon with rainbow wing speckles, not solid purple wings. | [description](https://mirror.wingsoffire.wiki/wiki/Peacemaker) |
| 78 | Hope | Near-black with dark green underscales. | [description](https://mirror.wingsoffire.wiki/wiki/Hope) |
| 79 | Firefly | Dark purple; exact regional colours are not specified. | [description](https://mirror.wingsoffire.wiki/wiki/Firefly) |
| 80 | Mightyclaws | Near-black; removes unsupported bright-purple emphasis. | [description](https://mirror.wingsoffire.wiki/wiki/Mightyclaws) |

The machine-readable companion, `COLOUR-AUDIT-2026-10-18.json`, records the
reviewed representative regional colours. The actual pixel patterns live in
the editable catalog. Build/upload and physical appearance evidence belong in
the testing handover; this review by itself is not an LED colour measurement.

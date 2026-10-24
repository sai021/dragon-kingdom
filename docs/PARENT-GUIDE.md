# Using Dragon Kingdom

For shipping firmware **v0.3.0** and beta 3 or later. The webpage shows its installed version.
The shipped firmware mix is not yet established; older 0.2.4 instructions are in
[the historical guide](history/0.2.4-PARENT-GUIDE.md). Manual edition 0.8, 24 October 2026.
No app, account or browser login is needed for ordinary play. Keep your setup card.

## Touch play

Use the touch button on the right side. Normal power connects through the
bottom USB-C power port; the back has a keyhole-shaped mounting slot.

| Gesture | Action |
| --- | --- |
| Single tap | Next dragon in the active collection; wake if asleep |
| Double tap | Sleep or wake |
| Hold | Adjust glow in 10% steps; release and hold again to reverse direction |

The dragon also responds to room light. Its glow is limited by the available
power, so 100% does not necessarily mean the LEDs' maximum possible output.

## First phone connection

1. Scan **Setup & manual** while you have internet, then power on one new dragon and wait for startup.
2. In phone Wi-Fi settings choose **Dragon-Kingdom-** followed by six letters/numbers, using **dragon123**. If several appear, temporarily power off the others.
3. If the phone warns that the network has no internet, choose to stay connected.
4. The setup page may appear automatically. Otherwise scan **Open dragon** on the shared card or rear label. Fallback: `http://192.168.4.1`.
5. Play without logging in. For Wi-Fi, backups, updates or reset, open **Parent settings** and unlock with **dragon123**.

Your home Wi-Fi keeps its own password. Setup Wi-Fi opens at each normal startup.
**Find my Wi-Fi** offers nearby 2.4 GHz home networks. Choose a network or type
its name, enter its password, and connect. After success, rejoin home Wi-Fi and
use the dragon address displayed on the page. Open it in your normal browser and save it as a bookmark. Setup Wi-Fi closes about 15 seconds after a successful join; a radio channel change may disconnect your phone sooner.
Home Wi-Fi is optional. Internet features are not required for ordinary play.
Guest or isolated networks can prevent the phone reaching the dragon, even by
numeric address. Use a network that allows local devices to communicate, or
reopen the dragon's direct setup network. Wait for each control change or save
to finish before tapping the next control. The page shows **Please wait for your
dragon** and temporarily disables conflicting controls while an action is pending.

## Profiles and creations

**All** shows the complete collection and cannot be renamed or deleted. You
can use it without creating a profile. Optional profiles hold different favourite
collections for the same child. Add a
named profile in **My favourites & starting glow**. Choose its favourites and
starting glow, then save. **My dragon** shows those favourites plus the
profile's own creations. A new empty profile invites you to add or create one.

To create, tap **Make a dragon**, choose **Start from**, and give it a name.
The editor shows the dragon shape, without LED-grid controls. Tap a body part
or use the part list. Change its colour and magic.
Wing edges and interiors can be different. Save to see the creation on the
physical dragon. Cancel leaves the device unchanged.

Select a custom dragon and tap **Edit or copy custom dragon** to edit or copy it.
Use the search box in profile settings to find favourites without losing your
existing selections. The original supplied
dragons remain intact. Deleting a profile moves its creations into All.
There are three named profile spaces and eight custom dragon spaces shared
across the device. Play controls stay unavailable for an empty profile until
you add favourites or a creation.

If a save fails, the editor keeps its draft. If the page says the collection
changed, note your unsaved choices before reloading, then check what is saved
before trying again. Reload the page after installing a firmware update.

## Sunrise alarm

Open **Sunrise alarm**, wait for its saved fields to load, choose a wake-up time
and a 1-120 minute sunrise, tick **Wake me every day**, then **Save alarm**.
It lights the whole wings while the dragon is asleep, holds for 30 minutes and
returns to the previous lighting. Preview takes 30 seconds; Stop/touch/play
cancels the current sunrise. Untick and save to disable the daily schedule.

If loading fails, the page retries. **Set clock from my phone** can recover the
saved fields and clock. Check the time, duration and checkbox before saving.
After a power cut, internet time or reopening the page is needed. Open and save
the alarm at least once a year and after changing time zone to refresh saved
clock rules. This is a light alarm without sound.

## Reconnect or change home Wi-Fi

Power off and on normally, then join the dragon network using **dragon123** and open
`http://192.168.4.1/`. No touch hold or purple indication is needed. Saved home Wi-Fi
is attempted at startup; after success, setup closes following a short handover.
Use **Forget home Wi-Fi** to remove only the saved network, then power cycle.

Stable v0.3.0 and beta 3 need a power cycle after a later router outage. The unpublished
beta 4 candidate retries saved home Wi-Fi with bounded backoff, without reopening setup.
Touch play remains available within the startup power budget.

## Power, updates and help

The bottom USB-C port is power-only. For service, the internal controller connector
is accessible after removing one screw. Never connect laptop USB and external/main
power simultaneously. Ask the maker for service rather than changing wiring.
A weak supply can leave Wi-Fi off; check the specified supply and cable.

Download an offline signed update package while you have internet, before joining
the dragon network (which has no internet). Keep power connected during an update.
A corrected C3 must retain calibration-aware firmware: do not install stable v0.3.0
on that unit. The beta 4 candidate adds signed compatibility checks; older installed
firmware cannot enforce them. The maker must supply the appropriate transition package.

Parent **Full reset** removes saved user settings and home Wi-Fi, while retaining
unit voltage calibration. Keep a backup before reset or restore. The parent password
remains **dragon123**. Beta 4 adds a support-details download without network names,
passwords or creation names. Startup checks are separate from physical acceptance.

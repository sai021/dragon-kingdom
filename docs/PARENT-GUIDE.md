# Using Dragon Kingdom

> This guide describes the installed 0.2.4 prototype. For the new startup, parent
> authentication and update behavior, use the [0.3.0 candidate notes](NEXT-RELEASE.md).

This guide is for one child and their grown-ups using a prepared prototype.
Keep its printed setup card. No app, account or coding is needed for normal play.
The printable [user manual](../output/pdf/dragon-kingdom-user-manual.pdf) is edition
0.7 (QR setup edition), dated 20 October 2026; the [editable source](USER-MANUAL.md) covers the same steps.

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
5. Log in as `parent`, using the setup card's password.

The 18 October 2026 firmware update uses **dragon123** for both the
dragon Wi-Fi and this login. It replaces earlier random passwords after flashing;
older printed cards may still show the previous password. Your home Wi-Fi keeps
its own password.

Play directly through this network, or open **For grown-ups · Wi-Fi & help**.
**Find my Wi-Fi** offers nearby 2.4 GHz home networks. Choose a network or type
its name, enter its password, and connect. After success, rejoin home Wi-Fi and
use the dragon address displayed on the page. Save that address as a bookmark.
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

Hold the touch pad while plugging in. Keep holding through the blue startup
pulses, then release when the purple indication appears. Join the dragon
network using the card and reopen `http://192.168.4.1`.

**Forget home Wi-Fi** opens setup again and removes the saved home-network
details. It keeps the dragon's setup password and creations. A router outage
does not stop touch play or automatically open a new setup network.

## Prototype testing

This is the current prototype guide, not a finished consumer-product manual.
For the developer's laptop test, external/main power stays disconnected. Do
not connect laptop power and main power simultaneously with the current circuit.
Follow the prepared device's power instructions rather than changing its wiring.
A low-power startup can leave Wi-Fi off while touch play still works. If setup
never appears, ask the maker to check the specified supply and cable.

Keep the universal QR setup card; optionally write the device's Wi-Fi name in its blank. For this firmware,
the shared setup password is **dragon123**. Older firmware with a lost random
password needs the maker's help or an update; a parent-friendly factory-reset
flow has not been implemented.

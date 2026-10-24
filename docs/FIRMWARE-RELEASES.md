# Firmware release channels

Parent settings default to **Release**. **Beta** is an explicit choice for
experienced users who can recover the ESP32 over internal USB. Locking/reloading
returns the selector to Release. Neither channel installs without a parent
choosing Install. File upload remains available offline.

- Release resolves GitHub `releases/latest/download/dragon-{board}.manifest`.
  Publish only accepted stable versions, with tags such as `v0.3.0`. The device
  rejects beta tags from this channel. There is no stable 0.3.0 yet.
- Beta resolves `releases/download/firmware-beta/dragon-{board}.manifest`.
  The `firmware-beta` GitHub release is a prerelease used only as a discovery
  pointer. Its signed manifests name immutable tags such as `v0.3.0-beta.1`.
  The device requires a `-beta.` tag in this channel.
- Actual binaries always download from the version tag bound into the signed
  manifest, never from a mutable pointer. Both channels verify board, signature,
  full size/hash and ESP image before selecting the inactive slot.

## Publishing

1. Run Python/native/browser tests; build both ESP32 targets. Record software and
   physical evidence separately. Keep the computer USB 400 mA ceiling unchanged.
2. Set `DragonOnline::CURRENT_TAG` to the intended immutable tag, regenerate the
   embedded page with `tools/embed_web.py`, and build the final images.
3. Use the existing local release signing key with `tools/sign_update.py sign`.
   Never regenerate the trust root as part of a build. Never upload the private
   key, NVS, device credentials or serial captures.

   Example, from `dragon-firmware` (repeat for c3 with its own image):

   ```powershell
   python tools/sign_update.py sign --key PRIVATE_KEY_PATH --board s3 --image build/s3/DragonPrototype.ino.bin --output .tools/next-release/dragon-s3.dragon.json --tag v0.3.0-beta.1
   ```

4. Commit/push the source and publish a GitHub prerelease at that exact commit
   with `--prerelease --latest=false`. Upload both board `.dragon.json`, `.bin`
   and `.manifest` files plus SHA256SUMS and the release notes. Version-tagged
   assets must not be silently replaced after publication.
5. After verifying the downloaded version assets, upload the two manifests to
   the `firmware-beta` prerelease, replacing its previous pointer manifests.
   Signed tags bind the target even while board pointers are being refreshed.
   Never promote the pointer or beta release to latest stable.
6. A future stable release uses a plain version tag, explicit acceptance evidence,
   the matching compiled CURRENT_TAG and `--latest`. Publishing stable is a
   separate release decision; beta publication does not promote it.

## First update and recovery

Older 0.3.0 candidates have no channel selector. Upload the matching signed JSON
file once to obtain it. Existing 0.2.4 single-slot devices require the initial USB
migration, not a web upload of raw `.bin` files. See [USB recovery](USB-RECOVERY.md).
The 0.3.0 beta is not general physical acceptance: C3 hardware, real iPhone/Android,
interrupted power and actual bootloader rollback checks remain open.

Before internal USB recovery, disconnect all product/external power. Never
connect laptop USB and external/main power simultaneously.

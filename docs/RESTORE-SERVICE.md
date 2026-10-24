# Restore journal service recovery

A valid interrupted restore is a redo transaction: on each boot retry library,
rotation, alarm, light calibration and (for reset) Wi-Fi/parent removal. Delete the
journal only after all writes verify. A failed write or exhausted store retains
the original journal. Never replace a valid partially applied transaction with a
reset or delete it to make startup appear healthy. Address storage availability,
then use `restore retry` over confirmed internal USB and restart.

An invalid/truncated/wrong-schema journal cannot establish the intended snapshot.
Normal startup remains isolated from networking; USB diagnostics remain available.
Before deliberately abandoning an invalid journal:

1. Confirm current board and internal laptop USB only, external/main supply unplugged.
2. Run `python tools/restore_service.py --port CURRENT_PORT --usb-only`. It identifies
   the ROM, validates the existing NVS layout and independently reads the raw NVS twice
   into ignored `.tools/restore-service/`. Matching bytes and recorded hash are required.
   These private files contain credentials and personal data; never publish them.
3. Reset to runtime, recheck the current port, retain the evidence, and send
   `restore abandon-invalid EVIDENCE-SAVED`. This explicit service command refuses
   a valid journal and requires computer USB mode. It removes only invalid `pending`.
4. Restart and inspect library, alarm, rotation, ambient settings and Wi-Fi. Any
   namespace already written before corruption remains as it was. The result can
   be a mixture of old and restored settings; it is not an atomic rollback.
5. Restore a known-good user backup after startup if necessary. Unit voltage
   calibration is in a separate excluded namespace and must remain intact.

If NVS cannot even open/remove the record, retain the complete private evidence
and escalate for a reviewed storage repair. Do not erase all NVS or discard a valid
transaction. This tool does not automatically clear anything after its readback;
the service operator deliberately acknowledges preserved evidence.

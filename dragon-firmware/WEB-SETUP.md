# Wi-Fi setup and recovery

Use the current [parent guide](../docs/PARENT-GUIDE.md) for shipping v0.3.0 and beta 3.
Setup opens on normal startup, play needs no login, and Parent settings unlock with
`dragon123`. Home Wi-Fi is optional; setup Wi-Fi has no internet. A successful join
closes setup after approximately 15 seconds. Rejoin home Wi-Fi and bookmark the
`.local` address in a normal browser; the numeric fallback may change with DHCP.
Power cycle to change networks or reopen setup. No purple touch-hold gesture.

Unpublished beta 4 retries a later dropped home connection with 10-second to
5-minute backoff and 60-second attempt deadlines. It never reopens setup on a
later disconnect. Scans, queued responses and updates defer retry attempts.
The pinned core and `CONFIG_LWIP_CHECK_THREAD_SAFETY` build option remain required.
Physical phone and radio lifecycle tests remain outstanding.

Historical 0.2.4 instructions are preserved in
[the historical engineering guide](../docs/history/0.2.4-WEB-SETUP.md).

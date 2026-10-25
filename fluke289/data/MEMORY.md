# Fluke 289 memory — experimental read-only download

## Status and operation

Synthetic tests include Linux pseudoterminals with real serial handling. Piotr confirmed listing, downloading and reopening JSON from a physical V1.41 meter. Selected readings were compared with its screen; not every structure/category/firmware is validated. No delete, reset, rename, clock synchronization or meter-write commands are implemented or whitelisted.

1. Connect the meter and keep the connection active. On the meter exit memory browsing and return to LIVE; Piotr confirmed downloads were blocked in memory browsing and worked after returning to LIVE.
2. Stop application file recording.
3. Open Fluke memory and List recordings. Counters and headers are read for Measurement, MIN MAX, Peak and Recording.
4. Select a recording and Download selected recording. Choose JSON folder/name first; cancelling the dialog does not start transfer. The header is rechecked to detect changes. Recording also downloads its intervals. Successful transfer saves the full backup and shows the path.
5. Open downloaded data and chart displays available readings. A single measurement is one point, not an invented trace. Save full backup writes header, intervals and raw hexadecimal blocks.
6. Reopen JSON through Open measurements. If saving fails, data remains in window memory and Save full backup can retry elsewhere. Bottom controls remain visible in a shorter window.

LIVE pauses only during transfer and resumes afterwards. File recording is not automatically restarted. Cancellation occurs between bounded transactions. Disconnecting during transfer can cause a read error. If firmware rejects reading during RECORD/MIN MAX/Peak, stop that mode on the meter and retry; the application does not stop it remotely. Do not change/delete meter records during download.

## Format and interpretation

Read-only commands: QSLS, allowlisted QEMAP, QSMR, QMMSI, QPSI, QRSI and QSRR. Headers/intervals are binary #0 blocks using fixed lengths, field counts and a separate trailing name. A CR inside a binary number does not terminate the block. Memory numbers are not arbitrarily rounded.

Function/unit/state maps come from the meter. Unknown codes remain UNKNOWN without guessing. Unvalidated high words of interval indices/sample counts are rejected rather than ignored. Counts and sizes are bounded.

The Recording AVERAGE field is a raw accumulator requiring interpretation with its count. Until physical validation, it is not plotted as an average. It remains unchanged in accumulators and raw_hex. Known PRIMARY/MINIMUM/MAXIMUM fields are displayed as interval readings, not reconstructed internal ADC samples.

Each plotted field uses its own meter timestamp, not the interval end. Start/end remain in the backup. Lines connect available readings; unavailable internal samples are not reconstructed. The axis identifies Fluke clock UTC from the timestamp, without assuming synchronization/time-zone setup. It may differ from local LCD time.

History shows the latest 10,000 samples; JSON retains all downloaded intervals. JSON import is limited to 50 MiB. Large downloads/imports can take time. Unsupported layouts are not treated as known.

## Diagnostics and acceptance

Save diagnostics captures recent commands and raw transfer responses and may include record names/readings. Inspect before sharing and report firmware, category and failed stage (list/header/interval). Structural errors force reconnection before LIVE resumes.

Compare name, function, value, unit, decimals and time against a Measurement/MIN MAX/Peak memory screen. For Recording compare interval count and several trend points. Do not discard originals merely because download succeeded; compare and save first. The application offers no delete operation.

## Provenance

Binary format research used N0ury/dmm_util (MIT declared by that repository), especially fluke_28x_dmm_util/dmm_util.py: https://github.com/N0ury/dmm_util, and Fredrik Valeur's earlier implementation: https://github.com/fvaleur/dmm_util.

The Fluke Users Manual describes memory categories and operation: https://assets.fluke.com/manuals/287_289_umeng0100.pdf.

This is an independent implementation; dmm_util code is not imported or copied. Source research is not physical acceptance of this release.

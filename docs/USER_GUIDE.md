# User guide — Fluke 289 Live Studio

## Hardware and connection

Use a Fluke 289 and a compatible optical serial cable such as Fluke IR189USB. A generic USB IrDA networking adapter is not necessarily compatible. The meter makes measurements independently; the application polls its display data.

Attach the optical head securely, turn on the meter, click Refresh and select its port, usually `/dev/ttyUSB0`. A `/dev/serial/by-id/...` path may be more stable across reconnects. Enter an interval of 0.2–3600 seconds using a decimal point, then Connect. The default 0.5 s does not guarantee sampling at the same instant as the LCD. Disconnect closes the connection and stops active recording. Select functions, ranges and modes on the meter; the application does not control its menus or reset it.

## Readings and warnings

The large value is PRIMARY. Its unit, multiplier, decimal places and trailing zeros come from the meter. LIVE is separate and can differ during HOLD or REL. The table lists all received fields, states, attributes and raw meter timestamps.

OL, OL_MINUS, INVALID, BLANK, DISCHARGE and OPEN_TC are not replaced with ordinary numbers. OPEN_CIRCUIT, SHORT_CIRCUIT and GOOD_DIODE remain separate attributes. Unknown functions or modes retain their raw names and generate warnings rather than invented support.

The lightning icon follows only the meter's ON/OFF flag. OFF hides it; stale or missing data means the current state is unknown. An absent icon does not establish that voltage is safe. Follow the meter and its safety instructions; this software is not protective equipment.

## Bar graph and MIN MAX

The bar graph uses the reported AUTO/MANUAL range. A compatible BARGRAPH field takes priority; otherwise LIVE is shown and explicitly labelled as USB-refreshed data. It does not have the speed of the internal LCD bar graph. Unknown scales or incompatible units produce a no-data message.

In MIN MAX mode a Maximum/Average/Minimum panel replaces the bar graph. Values and formatting come from the meter, not USB-derived substitutes. Elapsed times are each reading timestamp minus the transmitted MIN MAX start time. Leaving the mode restores the bar graph; losing communication clears stale values.

The bar graph has its own physical quantity, value and range. With frequency as PRIMARY, it can show AC voltage from LIVE; this is intentional and labelled.

## Live chart and layout

Choose LIVE, PRIMARY or an available statistic field. AUTO lock shows the last minute and disables manual navigation. Clear it to zoom with the wheel and pan by dragging; enable it again to restore AUTO.

Hover shows the nearest actual sample with meter formatting and computer time, without interpolating a reading. Double-click opens full history. Known gaps and invalid readings break the trace. Antialiasing smooths pixels, not the measured data. Drag the table's top edge across its width to resize it. Layout is not yet persisted.

## Full history and navigation

Chart and history collects readings in memory even when file recording is off. Select the function/mode series, unit and visible fields. Different units are never mixed on one axis. Function, subfunction or mode changes start a separate series.

Wheel zoom anchors the time axis at the cursor; drag to pan. Double-click or Fit entire recording restores the full selected series. Last minute and Last 5 minutes provide presets. The value axis follows valid visible samples. The 1 ms minimum time view is a navigation limit, not recording resolution.

Manual navigation disables following the current meter function. Enable Follow current meter function to return automatically. Visible MIN/MAX summaries describe the view; MINIMUM/MAXIMUM/AVERAGE traces are meter statistics.

Elapsed recording time switches labels to MM:SS or HH:MM:SS while tooltips retain clock time. This does not alter timestamps, matching or exports. Memory recordings use their Fluke header start; application sessions use the first recorded point of the series. Start-aligned comparisons keep their relative axes.

Select a field in the A/B list and use Previous point or Next point. Left/right arrow keys work when the chart has focus. Navigation selects real valid readings without interpolation or wrapping. Moving outside a zoomed range pans to the selected sample. Hover and point navigation update the table to the selected sample. Memory fields may have different timestamps and appear separately.

## A/B markers

Select a field, click Set A and select a chart sample; repeat for B. The nearest valid sample is used. The panel shows A, B, time difference and B minus A. An earlier B gives a negative time difference.

Drag marker lines to move them. Drag elsewhere to pan. Esc cancels selection; Clear A/B removes both. Markers remain attached to samples during zoom; off-screen markers remain in the summary. Changing field/function/unit clears them. Markers are not saved to measurement files.

## Optional file recording and timer

Connections start in preview mode. Choose CSV for spreadsheet exchange or SQLite for a full session including raw communication, identity and errors. Start recording opens a save dialog. Stop recording closes the file but leaves LIVE active. Choose another format or file afterwards. CSV requires a new name; appending to SQLite requires confirmation. Preview history is not retroactively added to a file.

REC indicates active recording, REC OFF means none, and REC PAUSED means no current data while the file remains open. Recording can continue after communication resumes. Disk failures stop recording with a message while retaining preview.

Enable Recording duration and enter days, hours, minutes and seconds before starting. The limit starts after choosing the file and is fixed for that recording. Editing the duration fields later does not change it. Without the option recording has no time limit. The countdown includes communication outages. On expiry the file closes and LIVE remains active; Stop recording can end it sooner. An in-progress serial transaction may delay the completion message, but the deadline is checked before the next write. This timer does not control Recording inside the meter.

## Opening and exporting recordings

Open measurements loads application CSV, SQLite or a Fluke memory JSON backup into a separate read-only history window, in the background. Older database → CSV converts a SQLite session; a direct CSV needs no second export. Base values and formatting metadata reproduce readings including trailing zeros. See FORMATS.md.

History/import keeps the latest 10,000 samples; recording files and full memory backups retain their full data. Unrecorded history disappears on exit. Port, layout, A/B markers and trace selection are not persisted. USB sampling, decimal digits and zoom do not increase physical accuracy. This is display polling, not an oscilloscope.

## Meter memory

Connect, stop any file recording, and open Fluke memory. Return the meter itself from memory browsing to LIVE. List recordings, select one and Download selected recording. Choose a JSON destination before transfer; cancelling the save dialog does not start a transfer. LIVE pauses during transfer and resumes afterwards. The original stays in the meter. Save full backup can retry a failed save or create another copy. See MEMORY.md for interpretation and validation limits.

## Compare two recordings

Open Compare recordings and choose A/B files (CSV, SQLite or memory JSON). Select a series and field in each, using the same unit. Matching PRIMARY fields are selected automatically where possible. Meter time uses transmitted Fluke timestamps and avoids computer-clock differences. If unavailable, select From both series starts. This aligns origins, not a shared physical event.

A positive B offset moves B later; a negative offset moves it earlier. Compare on one chart opens coloured A/B traces with independent visibility controls, zoom, hover and markers. Names and offset appear in the title. Change settings in the selection window and open a new comparison. Source values and files remain unchanged.

The matching tolerance defaults to 0.5 s. Statistics cover the entire common period regardless of zoom or hidden traces, after applying B offset. Each A proposes its nearest valid B within tolerance. Proposals are accepted from shortest time distance first; each B is used at most once and conflicts are skipped. Matching is directional: swapping A/B can change results with different cadences. Invalid readings are excluded, without interpolation or invented points.

The summary reports pair count, equality at the coarser common resolution, mean/max absolute difference and maximum time distance. Differences use base axis units, e.g. OHM means ohms. Show pair with largest difference zooms and marks both actual samples. Different sampling times can explain differences; agreement is not accuracy or calibration.

## Comparison reports

Export report offers vector PDF and UTF-8 BOM CSV. Choose a destination. An existing output is replaced only after successful report creation; source measurement files are protected.

PDF includes both traces over the full common period, names (possibly shortened), fields, base unit, time mode, B offset, tolerance, statistics and worst pair values/times. Cairo draws the PDF. Window zoom and hidden traces do not affect it. Missing overlap or matches are stated explicitly.

CSV lists every matched pair, base values, adjusted and original meter times, signed/absolute B-A, time distance, common-resolution equality, settings and full source names. No matches gives headers only. Formula-like textual names are protected with an apostrophe. Reports compare recordings and are not calibration certificates. Check names and readings before sharing.

## Measurement library

Add folder scans only that folder by default; Include subfolders enables recursion. Add files selects individual recordings. Application CSV/SQLite and memory JSON are supported. Comparison reports and other documents are skipped; skipped file details list errors separately.

Columns show name, UTC start, function, units, duration, interval/sample count, source and file state. Memory dates use the meter clock; CSV/SQLite dates use the computer clock. Do not assume these clocks agree. Search by name, function, unit or path; filter by source and sort using column headers.

Double-click or Open selected opens history. Ctrl-select two entries and Compare two selected opens comparison. Label recording changes only the library name. Remove from list leaves files intact; refreshing a folder can add them again.

The local index is `$XDG_DATA_HOME/fluke289-live/library.sqlite3`, normally `~/.local/share/fluke289-live/library.sqlite3`. It contains paths, labels, summaries and selected folders; recordings stay where they are. The application does not scan your whole home or disk. Completed recordings, saved memory backups and opened sessions are indexed in the background. Add old recordings using their folder.

Refresh library rescans selected folders and known files, caching unchanged metadata. Missing entries remain labelled to preserve their names/paths. Refresh an actively recorded file after recording stops. Indexing does not control the meter or stop LIVE.

## About

About includes credit, version, date, build fingerprint, tests and runtime information. Guides, changelog and full GPL are available offline. Copy information copies application/environment details without measurements or the meter serial number.

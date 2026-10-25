# File formats and privacy

## CSV

UTF-8 BOM, comma separated, decimal point. Each row is one reading field within a snapshot; LIVE, PRIMARY and statistics have separate rows. Import groups snapshots by event_id, pc_utc and identity.

| Columns | Meaning |
| --- | --- |
| event_id, pc_utc, identity | event ID, computer UTC, model/firmware/serial |
| primary_function, secondary_function, modes | functions and mode flags |
| range_mode, range_unit, range_number, range_multiplier | meter-reported range |
| lightning | meter ON/OFF flag |
| reading_id | LCD field, e.g. PRIMARY |
| value_base, unit | base value and unit code |
| multiplier, decimals, digits | meter display formatting |
| state, attribute | reading state and attribute |
| meter_time_raw | original meter clock timestamp |
| display_value, display_unit, display_text | presentation with trailing zeros |
| communication_gap | first snapshot/session or after communication restart/error |

Invalid states have an empty value_base; state and attribute remain. CSV does not contain raw frames or the complete communication error history. Base values/metadata reconstruct readings even in older files without display columns. Older readers can ignore additional columns.

Text that might trigger spreadsheet formulas is apostrophe-prefixed, including some formatted negative values. The application uses value_base and metadata rather than protected display_text. Spreadsheet software may independently change types or remove zeros.

CSV is opened exclusively as a new file (x mode). Buffers flush after every snapshot; power-loss durability equivalent to SQLite transactions is not claimed.

## SQLite

`events(id INTEGER PRIMARY KEY, time TEXT, kind TEXT, data TEXT)` stores ordered events. Data is JSON and time is ISO 8601 computer UTC. Kinds are identity (model/firmware/serial), wire (TX/RX and raw ASCII), snapshot (decoded readings and raw data), and error (communication failure).

Each event has its own transaction. WAL and synchronous=FULL are enabled. Stop recording before copying the database with possible -wal/-shm sidecars; never delete these during an active session. Existing databases can be appended after confirmation.

The importer opens read only and keeps the latest 10,000 samples with identities and known gaps. Earlier data remains in the full database. Browsing does not modify originals.

## Communication gaps

New CSV repeats communication_gap=1 for fields in the first snapshot, after reidentification and after communication errors. There is no invented zero or empty sample. SQLite-to-CSV export also carries restart/error boundaries.

For old CSV without the flag, the importer estimates cadence using at most the first 2000 positive sample intervals. A pause greater than max(2 seconds, three times the median) starts a new trace. This is a conservative heuristic, not an exact outage log; irregular sampling or clock jumps can affect it. Source files remain unchanged.

## Not persisted

Markers, zoom, table height, selected traces and user annotations are not saved. Hiding traces does not filter recording: all meter fields are saved. Preview history is volatile and is not added retroactively when recording starts.

## Privacy and compatibility

Measurements, identity and serial numbers stay local. No telemetry, server or cloud upload exists. About → Copy information excludes readings and serial number, but diagnostics/databases may contain them. Inspect files before sharing. Release builds use an allowlist and exclude private sessions, virtual environments, caches and configuration. English translation does not rename protocol tokens or storage columns; earlier Polish-release measurement files remain readable.

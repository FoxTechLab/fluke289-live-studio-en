# Development, tests and releases

## License and environment

Project code/documentation is GPL-3.0-or-later. Retain copyright/SPDX headers, COPYING and attribution; describe/date modifications and supply corresponding source as required by GPL. Preserve third-party terms. Project/issues: https://github.com/chudobapiotr5/fluke289-live-studio-en.

Python >=3.12, Tk and pySerial >=3.5,<4 are required. Cairo is a system library for antialiasing/PDF. Linux/POSIX pseudoterminal tests require no physical meter; the emulator exists only for tests.

## Architecture

- protocol.py: Snapshot/Reading dataclasses, QDDA validation, tokens and dial inference.
- transport.py: exclusive serial transactions, bounds, identity and read-only command whitelist.
- worker.py: sole owner of serial/file recording; start/stop, deadlines, retries and GUI queue.
- display.py: meter multiplier/decimal formatting.
- storage.py: SQLite/direct CSV/export; history.py: bounded memory and read-only imports.
- gui.py: main window, connection/recording controls and Tk-thread widget updates.
- mini_chart.py/history_gui.py: live/full charts, fields, axes, hover, navigation and A/B.
- viewport.py/markers.py/point_navigation.py: Tk-independent interaction models.
- bargraph.py/minmax.py: reported meter data without invented missing statistics.
- trace_renderer.py: Cairo ctypes rendering on one worker with bounded queues; no Tk calls from renderer threads; newest frame only, vector fallback on failure.
- memory.py/memory_gui.py: experimental binary memory reading, listing/download and JSON backups using the same serial owner.
- library.py/library_gui.py: local index, explicit scans, filtering, labels and comparison launch.
- comparison.py/comparison_gui.py/comparison_report.py: time alignment, directional one-use matching and PDF/CSV reports.
- about.py: offline documents/build metadata; __main__.py: GUI and ports/diagnose/export/version CLI.

Never silently save preview data/raw frames; explicit CLI diagnose is the exception. Never pass Tk objects across threads or infer safety warnings from a local threshold. Protocol tokens, wire data and stored measurement columns remain language-independent.

## Tests and acceptance

```bash
python3 -m unittest discover -s tests -v
```

Tests must verify behaviour, not merely mirror code. Physical changes need DIAGNOSTICS.md acceptance recorded in VALIDATION.md. Synthetic data, source-language audits and valid metadata do not establish full GUI/hardware acceptance. Unicode filename tests intentionally retain non-ASCII sample names to verify international compatibility.

## Build

```bash
python3 tools/release.py
python3 tools/build_deb.py
python3 -m pip wheel --no-deps --no-build-isolation . --wheel-dir dist
```

Release copies canonical root/docs files into package resources for offline installed use, runs tests and records warnings/environment, hashes an explicit allowlist, writes build metadata with UTC/version/fingerprint/per-file hashes/results, and produces a source ZIP plus checksums. Generated TESTS.txt/build_info.json are excluded from their own fingerprint. Build ID is a shortened hash, not an author signature. Rebuild after changing sources. Test duration/date may vary; the same allowlisted files yield the same source hash. This script never publishes online.

The wheel needs pyproject build dependencies. Inspect packages: code, tests, docs, COPYING and resources, but no virtual environment, recordings, WAL files, private photos/configuration, credentials, session serial numbers or caches. Dependencies are installed separately.

## Debian/Ubuntu

Rootless build requires dpkg-deb. The package installs code under /usr/share/fluke289-live, launcher /usr/bin/fluke289, desktop entry, SVG/PNG icons and AppStream metadata. It declares system Python/Tk/pySerial/Cairo dependencies; no downloads occur during building and no user data or virtual environment is bundled.

Check `dpkg-deb --info`, extract into a disposable folder and run its usr/bin/fluke289 --version. This verifies structure/imports, not installation/menu rendering. A local GNOME Software DEB view uses limited package data; embedded AppStream does not guarantee icon/screenshot/license presentation. Screenshot URLs must exist publicly; full store presentation requires a suitable catalog integration.

Unimplemented: persistent UI settings, plot annotations and generic chart PNG/PDF export outside comparison reports. Do not advertise these as shipped features. English screenshots require capture of the actual English UI; old Polish screenshots must not be presented as English screenshots.

# Validation and support status

## Automated tests

TESTS.txt and the build manifest record the actual test count, result and environment. Coverage includes QDDA decoding, function/mode tokens, malformed frames, reading states, Linux pseudoterminal transport, fragmentation, ACK/timeouts/model identification, reconnect, storage/disk failures, CSV/SQLite, formatting round-trips, history, ranges, A/B, bar graph, lightning, MIN MAX, rendering, navigation, timer, library, comparison statistics, PDF/CSV reports and communication gaps.

Synthetic data and pseudoterminals are not physical meter tests. Mocked GUI/data-model tests are not visual acceptance of a complete desktop window. Piotr supplied English UI screenshots on 2026-10-25 showing live AC voltage, frequency, meter MIN MAX, crest factor, Celsius/Fahrenheit, resistance, continuity and capacitance. The remaining Polish bar-graph word was corrected from zakres to range. This is selected visual evidence, not complete GUI acceptance.

## Physical user acceptance

Piotr tested a physical FLUKE 289 V1.41 on /dev/ttyUSB0. User reports/screenshots confirmed connection, resistance, OL, function recognition, REL/reference/states, continuity/open/short attributes, approximately 230 V AC, lightning flag, manual ranges, meter MIN/MAX/AVG and times, recording/reopening, live chart/history/zoom/table resize, and responsiveness after moving blocking rendering out of the Tk thread.

This is selected practical acceptance, not a complete measurement matrix. Serial numbers and original recordings are not included in the release. The code author did not physically inventory the USB adapter model.

## Results from Polish release 1.7.0, 2026-10-25

These observations come from Piotr's files, photos and reports; they establish data agreement and application behaviour, not independent measurement accuracy. They do not constitute a fresh hardware test of English 1.8.0.

- V1.41 memory listing, Recording/Measurement downloads, JSON destination selection and reopening worked. Meter memory browsing blocked transfers; returning to LIVE restored them.
- Temperature matched 34.2 °C at 14:28:45 and 22.4 °C at 14:30:32. Recording fields now use their own timestamps. Reconstruction of every internal LCD trend sample was not established.
- Frequency matched 49.969 Hz at 15:06:12, 49.976 Hz at 15:08:00 and 49.996 Hz at 15:09:16. Parallel recordings shared 49.958–50.008 Hz extrema; 218/265 nearest pairs agreed at 0.001 Hz, maximum difference 0.001 Hz with time distances up to 0.262 s. This earlier directional matching was not simultaneous sampling.
- AC voltage matched LCD points 230.46 V at 15:35:04, 229.79 V at 15:37:33 and 229.73 V at 15:38:48. Another comparison gave 298 pairs, 232 equal at common resolution, mean difference about 0.00221477 V, maximum 0.01 V, maximum time distance about 0.106 s. Worst-pair navigation was confirmed in the UI.
- Resistance in the 500-ohm range matched 336.44 ohms. Cable-motion jumps appeared in both recordings. Recording MIN retained 335.45 ohms while PRIMARY/CSV minimum was 335.79 ohms; 0.5 s USB polling can miss brief events.
- Timed recording stopped while LIVE continued. First-to-last sample distance does not measure timer accuracy.
- Library indexed 20 CSV/SQLite/JSON sessions and opened a two-file comparison. A user's Polish PDF was rendered and visually checked for a readable one-page chart, diacritics and matching statistics.
- Previous/next navigation, elapsed time, selected-sample table updates and a voltage bar graph under a frequency PRIMARY were confirmed.
- Optical outage: an old CSV had a 6.536 s gap without zero/BLANK/OL and displayed a break after the fix. A new CSV had two explicit resume flags, 6.569 s and 16.535 s distances, 76 NORMAL PRIMARY samples and two visible breaks. Distances include detection/retry, not just head removal.
- A separate earlier USB disconnect test contained transient NORMAL 0 V, BLANK and OL. Their cause remains unknown. Recovery was visible, but this scenario is not fully validated.
- Installation of the Polish DEB and launch from its menu icon were confirmed by the user. Taskbar icon and installer presentation changes require separate desktop acceptance.

Optical/USB latency has not been independently measured. Sampling times, clocks and Recording aggregation must be considered separately. Comparisons do not calibrate the meter.

## Outstanding limitations

Every function/subfunction/mode combination on every firmware remains untested. Ubuntu 24.04/Python 3.12 is a target, not a fully accepted environment; the build report gives the actual system. Physical accuracy/calibration is not verified. USB polling cannot capture every internal sample or LCD bar-graph event. Only selected memory Recording/Measurement cases were accepted; interval averages remain raw accumulators. Full visual GUI acceptance across screen sizes, and the new English UI, remains outstanding.

Before extending support claims, execute DIAGNOSTICS.md and record firmware, OS, Python, adapter, setting and actual result. A decoder token alone never establishes hardware support.

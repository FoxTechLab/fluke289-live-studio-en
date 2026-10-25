# Protocol and support boundaries

## Transport

Fluke 289 uses a compatible optical serial adapter at 115200 bit/s, 8 data bits, no parity, 1 stop bit, no flow control. This is serial IR, not IrDA networking. Worker is the sole serial owner and Linux opens the port exclusively.

Live operation uses ID and QDDA. QM is read-whitelisted but does not replace QDDA in the GUI. No RI/DS/RMP or other setting-changing commands are sent. Commands end in CR; responses contain a CR-terminated ACK and a separate data line. ACK 0/1/2/5 and unknown ACK errors are handled. CRLF, fragmentation and empty trailing terminators are tolerated. Transactions are bounded by time and a 32768-byte line limit. Experimental read-only memory commands are documented in MEMORY.md.

ID must identify exactly FLUKE 289 with firmware and serial fields. Fluke 287 compatibility is not claimed.

## QDDA and formatting

The decoder preserves primary/secondary function, auto/manual range, range unit and number, multiplier, lightning flag, MIN MAX start, variable mode flags and readings. Each reading has ID, base value, unit, display multiplier, decimals, digits, state, attribute and meter timestamp. Counts are checked, with at most 64 modes and 64 readings.

Unknown function/subfunction/mode names remain raw with warnings. Invalid numbers, NaN, infinity and malformed structures produce errors, not samples.

Values are base-unit numbers. Display uses the meter multiplier and decimal count, not an arbitrary automatic prefix: 0.005029 VAC with multiplier -3 and three decimals becomes 5.029 mVAC. Decimal constructed from textual number representation preserves trailing zeros. No LCD image is transmitted; unit symbols are text-rendered.

PRIMARY is the main (possibly held/relative) result. LIVE is separate. MINIMUM/MAXIMUM/AVERAGE come from the meter, not USB statistics. Invalid states or sentinel values around 9.99999999e37 are not plotted as normal numbers.

There is no mechanical dial-position field. The labelled inference uses the active function; LIMBO/unknown yields no established position. Silence alone does not prove OFF.

## Bar graph, time and warning

QDDA lists BARGRAPH among possible IDs but does not guarantee it. Use a compatible BARGRAPH if received, otherwise LIVE on the reported range scale, with source labelled. Incompatible units or unknown nonlinear scales are not guessed.

Computer UTC timestamps mean receive/record time; the meter clock is separate and is not assumed synchronized. MIN MAX times are reading timestamp minus minMaxStartTime, without mapping to the system clock. Missing or invalid time bases display a dash.

Lightning follows meter ON/OFF, not a local threshold. Stale data means unknown current status. USB/software does not replace the meter's safety indications.

## Errors and limits

Communication errors close the port and retry with increasing delays up to 30 s, checking ID again. Storage errors stop recording but preserve preview. Gaps are not interpolated and no synthetic measurements are added. A 0.5 s polling interval does not capture all internal meter changes; response time also affects cadence.

No remote function/menu control, resets or TrendCapture image download is supported. Tests and observations are not calibration, certification or validation of every function/firmware combination. Primary references: THIRD_PARTY.md.

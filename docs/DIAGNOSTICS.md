# Diagnostics and physical Fluke 289 acceptance

## USB and permissions

Check the cable model (IR189USB or an explicitly compatible adapter), manufacturer and revision. Secure the head and shield it from strong light.

```bash
lsusb
ls -l /dev/serial/by-id/
id
bash ./run.sh ports
sudo dmesg --ctime | tail -60
```

Do not assume a particular VID/PID or USB chip. Record VID/PID, driver and port. Generic networking IrDA may not provide a serial interface. Do not install arbitrary Windows drivers on Ubuntu.

For Permission denied, check the device group and dialout membership and log out/in fully after changes. For Device or resource busy, close other serial clients. Check `fuser /dev/ttyUSB0` and `systemctl status ModemManager`. Do not disable ModemManager globally without establishing that it opens this port and whether other devices need it.

## Identify the model and protocol

Disconnect the GUI, turn on the meter and run:

```bash
bash ./run.sh diagnose /dev/ttyUSB0 --timeout 3 --database acceptance.sqlite3
```

Expect TX ID, RX 0, RX FLUKE 289,<firmware>,<serial>; then TX QDDA, RX 0 and one long data line. Diagnose prints and stores complete communication in SQLite.

No response: check port, power, optical alignment, cable and light; USB enumeration alone does not validate the optical path. Other models are deliberately rejected. ACK 1/2 for QDDA requires firmware/raw logs, not a claim of support based on QM. ACK 5 means no data in that state: return to the normal measurement screen and retry. For truncated data secure the cable and increase diagnostic timeout/polling interval; retain raw response.

## Dial and menu matrix

Record OS/Python, cable model and VID/PID, firmware, meter identification and date. Do not mark OK without comparing the physical display. For each position test normal readings and every available menu subfunction.

| Position | Compare | Result |
| --- | --- | --- |
| LoZ V AC | primary/secondary, unit, range | pending |
| V AC | above plus available Hz/dB/filter/crest | pending |
| mV AC | function, readings, unit, range | pending |
| V DC / AC+DC | AC/DC combinations and additional fields | pending |
| mV DC / temperature | mV, combinations and temperature | pending |
| ohms / continuity / conductance | function, short/open states | pending |
| diode / capacitance | function, attribute, overload | pending |
| A / mA | function and unit vs display | pending |
| microamps | function and unit vs display | pending |
| 50 ohms | OHMS_LOW function | pending |

Electrical tests must follow the Fluke manual using suitable sources/circuits. Hazardous voltage is unnecessary for basic protocol verification.

Compare PRIMARY/LIVE, AUTO/MANUAL range, secondary reading and available HOLD/AUTO_HOLD/REL/REL percent/MIN MAX/AVG/Peak/RECORD. Change functions during polling: the next valid response must update the displayed function; transitions can yield LIMBO/no data. The dial label remains an inference, not an extra protocol field.

## Resilience and data

1. Connect without recording: verify PREVIEW and no new measurement file. Start a test CSV/SQLite, disconnect USB and check error/stale-value clearing and preservation of existing data.
2. Reconnect at the same stable path. A new ID must precede resumed readings; gaps must contain no invented samples.
3. Enable HOLD; compare PRIMARY/LIVE and preserved HOLD flags.
4. Safely provoke an invalid state such as an open thermocouple. CSV must contain the state and an empty value rather than a huge sentinel.
5. Restart and export the database. Compare positive/negative values, mV/microamps/kilohms, display metadata and raw logs.
6. Stop recording: LIVE continues and the file stops growing. Start another format without disconnecting. Disconnect during a query must complete after its bounded timeout and release the port.
7. Process-crash tests belong in disposable databases. Stop recording before moving SQLite files with WAL/SHM sidecars.

## Reporting

Include ports/diagnose output, firmware, adapter, physical dial/menu setting and a disposable test database. Logs may contain serial numbers and measurements; inspect them before sharing and exclude unrelated sessions.

Actual build environment and test results are in TESTS.txt. Physical observations from the Polish release are in VALIDATION.md. A graphical session is required for visual acceptance; a headless test cannot confirm window appearance. Ubuntu 24.04/Python 3.12 and the complete hardware matrix remain to be confirmed.

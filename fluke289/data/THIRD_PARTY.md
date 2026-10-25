# Third-party components and reference material

Source packages contain project code, tests and documentation, not Python, system libraries, pySerial, drivers, meter firmware or copies of Fluke manuals.

| Component | Role | License/source |
| --- | --- | --- |
| Python and standard library | interpreter, SQLite/JSON/CSV/ctypes/threads | Python/PSF licenses: https://docs.python.org/3/license.html |
| Tcl/Tk | tkinter windows | separate permissive Tcl/Tk terms shipped by the system: https://www.tcl-lang.org/software/tcltk/license.html |
| pySerial | serial communication | BSD-3-Clause, Chris Liechti and contributors: https://github.com/pyserial/pyserial/blob/master/LICENSE.txt |
| Cairo | antialiasing/vector PDF | LGPL 2.1 or MPL 1.1 as distributed: https://cairographics.org/ |
| SQLite | session engine via Python | author's public-domain declaration: https://www.sqlite.org/copyright.html |

Project GPL does not replace dependency licenses. Bundling dependencies/interpreters requires their terms and applicable sources. Current sources distribute project code and install dependencies separately.

Communication follows Fluke's protocol specification, without copying libsigrok/QtDMM. Memory research also used https://github.com/N0ury/dmm_util and https://github.com/fvaleur/dmm_util; commands/binary layouts were independently implemented without importing their code. See docs/MEMORY.md. Tests use short example ASCII responses from the specification, identified in test sources. Manufacturer documents remain the manufacturer's materials and are not licensed under this project's GPL.

References:
- Fluke 289/287 Remote Interface Specification (2007), mirror: https://www.uniteng.com/neildocs/facilities/Fluke289_remote_spec28X.pdf
- Users Manual: https://assets.fluke.com/manuals/287_289_umeng0100.pdf
- Calibration Manual: https://media.fluke.com/b1d069ee-f650-436e-9a3a-b10800c1817d_original%20file.pdf
- IR189USB: https://www.fluke.com/en/product/accessories/adapters/fluke-ir189usb
- GNU GPL v3: https://www.gnu.org/licenses/gpl-3.0.html

COPYING is the unchanged GPL v3 text, Copyright (C) 2007 Free Software Foundation, Inc. GPL-3.0-or-later licensing does not imply membership in the GNU Project.

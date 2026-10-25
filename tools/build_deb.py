#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Piotr
"""Build a rootless Debian binary package, without bundling measurements or venv."""
import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from fluke289 import __version__

DESKTOP='''[Desktop Entry]
Version=1.0
Type=Application
Name=Fluke 289 Live Studio
Comment=Measurements, recordings and plots for Fluke 289
Exec=fluke289
TryExec=fluke289
Icon=fluke289-live
Terminal=false
Categories=Science;Electronics;
Keywords=Fluke;multimeter;measurement;multimetr;pomiary;
StartupNotify=true
StartupWMClass=Fluke289Live
'''

LAUNCHER='''#!/usr/bin/python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Piotr
from pathlib import Path
import sys
# Relative to /usr/bin so an extracted package can also be smoke-tested.
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'share/fluke289-live'))
from fluke289.__main__ import main
raise SystemExit(main())
'''

def build():
    info=json.loads((ROOT/'fluke289/data/build_info.json').read_text())
    if info['version']!=__version__:raise SystemExit('Run tools/release.py for the current version first.')
    version=__version__+'-1';dist=ROOT/'dist';dist.mkdir(exist_ok=True)
    destination=dist/f'fluke289-live_{version}_all.deb'
    with tempfile.TemporaryDirectory(prefix='fluke289-deb-') as tmp:
        stage=Path(tmp)/'package';app=stage/'usr/share/fluke289-live/fluke289';app.mkdir(parents=True)
        for p in (ROOT/'fluke289').glob('*.py'):shutil.copy2(p,app/p.name)
        shutil.copytree(ROOT/'fluke289/data',app/'data')
        doc=stage/'usr/share/doc/fluke289-live';doc.mkdir(parents=True)
        for name in ['COPYING','AUTHORS.md','THIRD_PARTY.md','README.md','CHANGELOG.md','TESTS.txt']:shutil.copy2(ROOT/name,doc/name)
        shutil.copytree(ROOT/'docs',doc/'manual')
        (doc/'copyright').write_text('Fluke 289 Live Studio\nCopyright (C) 2026 Piotr\nLicense: GPL-3.0-or-later\nFull license: COPYING in this directory.\nIndependent project, not official Fluke software.\n',encoding='utf-8')
        with (doc/'changelog.Debian.gz').open('wb') as f:
            f.write(gzip.compress(f'fluke289-live ({version}) unstable; urgency=low\n\n  * Desktop package for build {info["build_id"]}.\n\n -- Piotr  Sun, 25 Oct 2026 12:00:00 +0000\n'.encode(),mtime=0))
        launcher=stage/'usr/bin/fluke289';launcher.parent.mkdir(parents=True);launcher.write_text(LAUNCHER)
        desktop=stage/'usr/share/applications/fluke289-live.desktop';desktop.parent.mkdir(parents=True);desktop.write_text(DESKTOP,encoding='utf-8')
        icon=stage/'usr/share/icons/hicolor/scalable/apps/fluke289-live.svg';icon.parent.mkdir(parents=True);shutil.copy2(ROOT/'fluke289/data/fluke289-live.svg',icon)
        png=stage/'usr/share/icons/hicolor/128x128/apps/fluke289-live.png';png.parent.mkdir(parents=True);shutil.copy2(ROOT/'fluke289/data/fluke289-live.png',png)
        metadata=stage/'usr/share/metainfo/io.github.chudobapiotr5.fluke289_live.metainfo.xml';metadata.parent.mkdir(parents=True);shutil.copy2(ROOT/'fluke289/data'/metadata.name,metadata)
        control=stage/'DEBIAN';control.mkdir()
        size=sum(p.stat().st_size for p in (stage/'usr').rglob('*') if p.is_file())//1024+1
        (control/'control').write_text(f'''Package: fluke289-live
Version: {version}
Section: science
Priority: optional
Architecture: all
Maintainer: Piotr
Homepage: https://github.com/chudobapiotr5/fluke289-live-studio-en
Installed-Size: {size}
Depends: python3 (>= 3.12), python3-tk, python3-serial, libcairo2
Recommends: fonts-dejavu-core
Description: Fluke 289 measurements, recordings and comparison
 Interface language: English.
 Independent GNU GPL-3.0-or-later desktop application for GNU/Linux.
 Live readings, memory download, recording timer, library, plots,
 comparison and PDF/CSV reports. Does not modify meter memory.
 .
 Developed and tested by Piotr with assistance from OpenAI Codex.
 Source code and releases: github.com/chudobapiotr5/fluke289-live-studio-en
 Requires a physical Fluke 289 and a compatible optical USB adapter.
 Independent project, not affiliated with Fluke.
''',encoding='utf-8')
        for p in stage.rglob('*'):p.chmod(0o755 if p.is_dir() else 0o644)
        launcher.chmod(0o755)
        if shutil.which('desktop-file-validate'):subprocess.run(['desktop-file-validate',str(desktop)],check=True)
        subprocess.run(['dpkg-deb','--root-owner-group','--build',str(stage),str(destination)],check=True)
    print(destination)
    return destination

if __name__=='__main__':build()

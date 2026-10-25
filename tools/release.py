#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Piotr
# This program comes with NO WARRANTY; see COPYING for license terms.
"""Build a documented, tested source release from an explicit file allowlist."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fluke289 import __version__

ROOT_FILES = ['README.md', 'COPYING', 'AUTHORS.md', 'THIRD_PARTY.md',
              'CHANGELOG.md', 'DIAGNOSTICS.md', 'TESTS.txt', 'MANIFEST.in',
              'pyproject.toml', 'run.sh', '.gitignore']


def source_files():
    files = [ROOT / name for name in ROOT_FILES]
    for directory in ['fluke289', 'tests', 'tools']:
        files += sorted((ROOT / directory).glob('*.py'))
    files += sorted((ROOT / 'docs').glob('*.md'))
    files += sorted((ROOT / 'docs').glob('screenshot-*.png'))
    files += sorted(p for p in (ROOT / 'fluke289' / 'data').glob('*') if p.is_file())
    return sorted(set(files))


def stage_documents():
    data = ROOT / 'fluke289' / 'data'
    data.mkdir(exist_ok=True)
    for name in ['README.md', 'COPYING', 'AUTHORS.md', 'THIRD_PARTY.md', 'CHANGELOG.md']:
        shutil.copyfile(ROOT / name, data / name)
    for source in (ROOT / 'docs').glob('*.md'):
        shutil.copyfile(source, data / source.name)
    # Tests also verify the resources; an initial report exists before the run.
    if not (ROOT / 'TESTS.txt').exists(): (ROOT / 'TESTS.txt').write_text('Raport w przygotowaniu.\n')
    shutil.copyfile(ROOT / 'TESTS.txt', data / 'TESTS.txt')


def main():
    stage_documents()
    result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                            cwd=ROOT, capture_output=True, text=True)
    log = result.stdout + result.stderr
    print(log)
    if result.returncode:
        raise SystemExit('Build stopped: tests failed.')
    count_match = re.search(r'Ran (\d+) tests?', log)
    if not count_match: raise SystemExit('Test count missing from report.')
    count = int(count_match.group(1))
    now = datetime.now(timezone.utc)
    date = now.date().isoformat()
    environment = f'{platform.freedesktop_os_release().get("PRETTY_NAME", platform.system())}; Python {platform.python_version()}'
    report = f'Fluke 289 Live Studio {__version__}\nUTC date: {date}\nEnvironment: {environment}\nAutomated tests: {count}, OK\n\n'+log
    report += '\nPhysical meter acceptance: selected features confirmed by Piotr on Fluke 289 V1.41.\nFull scope and limitations: docs/VALIDATION.md.\nFull Ubuntu 24.04 acceptance and automated visual GUI acceptance have not been performed.\n'
    (ROOT / 'TESTS.txt').write_text(report, encoding='utf-8')
    shutil.copyfile(ROOT / 'TESTS.txt', ROOT / 'fluke289/data/TESTS.txt')
    files = source_files()
    hashed = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in files if p.name not in {'build_info.json', 'TESTS.txt'}}
    digest = hashlib.sha256(json.dumps(hashed, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    build = {'version': __version__, 'date': date, 'build_id': date.replace('-', '')+'.'+digest[:12],
             'source_sha256': digest, 'author': 'Piotr',
             'author_credit': 'Software Development, Design & Testing by Piotr',
             'cooperation': 'OpenAI Codex', 'license': 'GPL-3.0-or-later',
             'tests': {'count': count, 'status': 'OK'}, 'test_environment': environment,
             'hash_excludes': ['TESTS.txt (root and resource)', 'build_info.json'], 'files': hashed}
    manifest = ROOT / 'fluke289/data/build_info.json'
    manifest.write_text(json.dumps(build, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    dist = ROOT / 'dist'
    dist.mkdir(exist_ok=True)
    archive = dist / f'fluke289-live-{__version__}-{build["build_id"]}-source.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in source_files(): z.write(path, 'fluke289/'+str(path.relative_to(ROOT)))
    with zipfile.ZipFile(archive) as z:
        if z.testzip(): raise SystemExit('Archive error')
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    (dist / 'SHA256SUMS').write_text(checksum+'  '+archive.name+'\n')
    print('Build:', build['build_id'])
    print('Source SHA-256:', digest)
    print('Archive:', archive)

if __name__ == '__main__': main()

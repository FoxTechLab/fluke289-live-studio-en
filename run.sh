#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ ! -x .venv/bin/python ]]; then
  echo 'First complete the installation described in README.md.' >&2
  exit 1
fi
if ! .venv/bin/python -c 'import serial' 2>/dev/null; then
  echo 'pySerial is missing. Run this in the application folder:' >&2
  echo '  .venv/bin/python -m pip install .' >&2
  exit 1
fi
exec .venv/bin/python -m fluke289 "$@"

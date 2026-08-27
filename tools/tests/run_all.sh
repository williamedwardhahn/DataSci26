#!/bin/bash
# Run the whole test suite. Pass a python interpreter as $1 to use a prepared
# environment (see tools/tests/README.md); defaults to python3.
set -u
cd "$(dirname "$0")/../.."
PY="${1:-python3}"
fail=0
line() { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }

line "static — notebook structure and Python syntax"
"$PY" tools/tests/test_static.py || fail=1

line "consistency — README schedule, plan, headers, assets"
"$PY" tools/tests/test_consistency.py || fail=1

line "pipeline — determinism and idempotency"
./tools/tests/test_pipeline.sh || fail=1

line "interactive — HTML/JS in the browser labs"
if command -v node >/dev/null; then node tools/tests/test_interactive.js || fail=1
else echo "  SKIP (node not installed)"; fi

line "assets — datasets and PDFs"
"$PY" tools/tests/test_assets.py || fail=1

line "links — every external URL"
"$PY" tools/tests/test_links.py || fail=1

line "execute — run every lab notebook"
if "$PY" -c "import nbclient" 2>/dev/null; then "$PY" tools/tests/test_execute.py || fail=1
else echo "  SKIP (nbclient not installed — see tools/tests/README.md)"; fi

printf '\n'
[ $fail -eq 0 ] && echo "ALL SUITES PASS" || echo "SOME SUITES FAILED"
exit $fail

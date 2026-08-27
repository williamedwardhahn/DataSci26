#!/bin/bash
# The lab notebooks are generated. Verify the pipeline is deterministic and idempotent:
# labs/ on disk must match exactly what a fresh rebuild from _source/ produces.
set -u
cd "$(dirname "$0")/../.."
fail=0

echo "--- 1. capture working-tree state ---"
before=$(find labs -name '*.ipynb' | sort | xargs shasum -a 256 | shasum -a 256 | cut -d' ' -f1)
echo "    labs/ digest: ${before:0:16}"

echo "--- 2. rebuild from _source/ ---"
python3 tools/build_labs.py  >/dev/null || { echo "    build_labs.py FAILED"; fail=1; }
python3 tools/modernize.py   >/dev/null || { echo "    modernize.py FAILED";  fail=1; }
python3 tools/fix_links.py   >/dev/null || { echo "    fix_links.py FAILED";  fail=1; }
after=$(find labs -name '*.ipynb' | sort | xargs shasum -a 256 | shasum -a 256 | cut -d' ' -f1)
echo "    labs/ digest: ${after:0:16}"
if [ "$before" = "$after" ]; then echo "    PASS  labs/ matches a fresh rebuild from _source/"
else echo "    FAIL  labs/ differs from a fresh rebuild (hand-edited, or a non-deterministic pass)"; fail=1; fi

echo "--- 3. idempotency: run the patch passes again ---"
python3 tools/modernize.py >/dev/null
python3 tools/fix_links.py >/dev/null
again=$(find labs -name '*.ipynb' | sort | xargs shasum -a 256 | shasum -a 256 | cut -d' ' -f1)
if [ "$after" = "$again" ]; then echo "    PASS  patch passes are idempotent"
else echo "    FAIL  re-running modernize/fix_links changed the output"; fail=1; fi

echo "--- 4. every planned lab exists ---"
n=$(python3 -c "import sys;sys.path.insert(0,'tools');from labs_plan import PLAN;print(len(PLAN))")
got=$(ls labs/*.ipynb 2>/dev/null | wc -l | tr -d ' ')
if [ "$n" = "$got" ]; then echo "    PASS  $got/$n labs present"
else echo "    FAIL  plan has $n labs, labs/ has $got"; fail=1; fi

echo "--- 5. every source range referenced by the plan resolves ---"
python3 - <<'PY' || fail=1
import sys, os, json
sys.path.insert(0, 'tools')
from labs_plan import PLAN
bad = 0
for entry in PLAN:
    w, slug = entry[0], entry[1]
    sources = entry[7]          # (week, slug, title, blurb, objectives, interactive, homework, sources[, extra])
    for path, a, b in sources:
        p = os.path.join('_source', 'notebooks', path)
        if not os.path.exists(p):
            print(f'    FAIL  lab{w:02d}: missing source {path}'); bad += 1; continue
        n = len(json.load(open(p))['cells'])
        if b > n:
            print(f'    FAIL  lab{w:02d}: {path} range {a}-{b} exceeds {n} cells'); bad += 1
print('    PASS  all source ranges resolve' if not bad else f'    {bad} bad range(s)')
sys.exit(1 if bad else 0)
PY

echo
[ $fail -eq 0 ] && echo "pipeline: PASS" || echo "pipeline: FAIL"
exit $fail

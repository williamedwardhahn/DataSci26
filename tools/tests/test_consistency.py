"""Cross-check the README schedule, the lab plan, the built labs, and the assets."""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from labs_plan import PLAN

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


readme = open(os.path.join(ROOT, 'README.md')).read()
rows = re.findall(r'^\|\s*(\d+)\s*\|\s*\[(\d+)\]\(labs/([^)]+)\)\s*\|\s*([^|]+?)\s*\|',
                  readme, re.M)
check(len(rows) == len(PLAN), f'README schedule has {len(rows)} lab rows, plan has {len(PLAN)}')

plan_by_week = {w: (slug, title) for w, slug, title, *_ in PLAN}
for wk, num, fname, topic in rows:
    wk, num = int(wk), int(num)
    check(wk == num, f'week {wk}: row links lab {num}')
    check(os.path.exists(os.path.join(ROOT, 'labs', fname)),
          f'week {wk}: README links labs/{fname} which does not exist')
    slug, title = plan_by_week.get(wk, ('', ''))
    check(fname == f'lab{wk:02d}_{slug}.ipynb',
          f'week {wk}: README filename {fname} != plan slug {slug}')
    # the schedule topic should track the lab title (case/punctuation-insensitive)
    norm = lambda s: re.sub(r'[^a-z0-9]+', ' ', s.lower()).strip()
    check(norm(topic).startswith(norm(title)[:18]) or norm(title).startswith(norm(topic)[:18]),
          f'week {wk}: README topic "{topic}" does not match lab title "{title}"')

# lab headers must state the right week and title
for w, slug, title, *_ in PLAN:
    p = os.path.join(ROOT, 'labs', f'lab{w:02d}_{slug}.ipynb')
    check(os.path.exists(p), f'lab {w}: {os.path.basename(p)} missing')
    if not os.path.exists(p):
        continue
    head = ''.join(json.load(open(p))['cells'][0]['source'])
    check(head.startswith(f'# Lab {w:02d} — {title}'),
          f'lab {w}: header does not read "# Lab {w:02d} — {title}"')

# every interactive lab referenced by a lab header and by the index must exist
idx = open(os.path.join(ROOT, 'interactive', 'index.html')).read()
on_disk = {os.path.basename(p) for p in glob.glob(os.path.join(ROOT, 'interactive', '*.html'))}
linked = set(re.findall(r'href="([\w.\-]+\.html)"', idx))
check(linked <= on_disk, f'index.html links missing files: {sorted(linked - on_disk)}')
orphans = on_disk - linked - {'index.html'}
check(not orphans, f'interactive labs not listed in index.html: {sorted(orphans)}')

# project + setup must exist and be non-trivial
for rel in ('project/README.md', 'setup/README.md'):
    p = os.path.join(ROOT, rel)
    check(os.path.exists(p) and len(open(p).read()) > 1000, f'{rel} missing or too short')

# archive integrity: the provenance note in each lab must point at real files
for p in sorted(glob.glob(os.path.join(ROOT, 'labs', '*.ipynb'))):
    tail = ''.join(json.load(open(p))['cells'][-1]['source'])
    for src in re.findall(r'`(_source/notebooks/[^`]+\.ipynb)`', tail):
        check(os.path.exists(os.path.join(ROOT, src)),
              f'{os.path.basename(p)}: provenance points at missing {src}')

if fails:
    print(f'{len(fails)} FAILURES')
    for f in fails:
        print('  ' + f)
    sys.exit(1)
print(f'PASS — README schedule, {len(PLAN)} lab headers, interactive index, '
      f'project/setup docs, and provenance all consistent')

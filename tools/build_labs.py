"""Assemble the course lab notebooks from archived source sections.

Re-runnable: rewrites labs/*.ipynb from _source/notebooks/ using labs_plan.PLAN.
"""
import json, os, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, '_source', 'notebooks')
OUT = os.path.join(ROOT, 'labs')
sys.path.insert(0, HERE)
from labs_plan import PLAN

SETUP = ("# Run this first, every session.\n"
         "!pip install -q git+https://github.com/williamedwardhahn/mpcr\n"
         "from mpcr import *\n"
         "import torch\n"
         "\n"
         "# Every lab is device-agnostic: it runs on a GPU runtime or a plain CPU one.\n"
         "device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')\n"
         "print('Running on:', device)")


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": text.splitlines(keepends=True)}


def clean(cells):
    """Drop empties, collapse consecutive duplicates, drop stray install cells."""
    out, prev = [], None
    for c in cells:
        s = ''.join(c.get('source', [])).strip()
        if not s or s == prev:
            continue
        if re.fullmatch(r'(!pip install .*|from mpcr import \*|\s*)+', s):
            continue
        c = {**c, 'metadata': {}}
        if c.get('cell_type') == 'code':
            c['outputs'], c['execution_count'] = [], None
        out.append(c)
        prev = s
    return out


def build(week, slug, title, blurb, objectives, interactive, homework, sources):
    head = [f"# Lab {week:02d} — {title}", "", f"*{blurb}*", "", "## Objectives", ""]
    head += [f"{i}. {o}" for i, o in enumerate(objectives, 1)]
    if interactive:
        head += ["", "## Interactive labs for this week", ""]
        head += [f"- [`{os.path.basename(p)}`]({p})" for p in interactive]
    head += ["", "---"]

    cells = [md('\n'.join(head)), code(SETUP)]
    used = []
    for path, a, b in sources:
        full = os.path.join(SRC, path)
        src = json.load(open(full))['cells'][a:b]
        kept = clean(src)
        cells += kept
        used.append((path, a, b, len(kept)))

    hw = ["---", "", "## Homework", ""]
    hw += [f"{i}. {h}" for i, h in enumerate(homework, 1)]
    hw += ["", "Submit as a markdown report in your course GitHub repo, with plots committed alongside it.", ""]
    hw += ["<details><summary>Where this lab came from</summary>", ""]
    hw += [f"- `_source/notebooks/{p}` cells {a}–{b} ({n} kept)" for p, a, b, n in used]
    hw += ["", "</details>"]
    cells.append(md('\n'.join(hw)))

    nb = {"cells": cells,
          "metadata": {"colab": {"provenance": [], "toc_visible": True},
                       "kernelspec": {"name": "python3", "display_name": "Python 3"},
                       "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 0}
    dst = os.path.join(OUT, f"lab{week:02d}_{slug}.ipynb")
    json.dump(nb, open(dst, 'w'), indent=1)
    return dst, sum(n for *_, n in used), len(cells)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    total = 0
    for spec in PLAN:
        dst, kept, n = build(*spec)
        total += kept
        print(f"  {os.path.basename(dst):48} {n:4} cells ({kept} from archive)")
    print(f"\n{len(PLAN)} labs built, {total} archived cells carried forward")

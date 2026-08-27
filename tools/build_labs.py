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

# The labs used to open with `from mpcr import *`, which pip-installed three packages
# at import time, required google.colab, and built every tensor on device='cuda'.
# Everything they actually used is reproduced here, in one self-contained cell.
SETUP_CORE = '''# --- setup: run this cell first, every session ---------------------------------
import builtins as __builtin__
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.functional import *

import torchvision
from torchvision import datasets, models, transforms
from torchvision.models import *

from scipy import stats, signal, integrate
from sympy import Symbol

from skimage import io
from skimage import io as skio
from skimage.transform import resize
from skimage.util import montage
from imageio.v2 import imread

from IPython.display import display, HTML

# One device for the whole notebook. A GPU runtime is faster, but nothing here
# requires one -- switch with Runtime -> Change runtime type -> T4 GPU.
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def GPU(data):
    """A learnable float tensor on the active device."""
    return torch.tensor(data, requires_grad=True, dtype=torch.float, device=device)


def GPU_data(data):
    """A fixed (non-learnable) float tensor on the active device."""
    return torch.tensor(data, requires_grad=False, dtype=torch.float, device=device)


print('Running on:', device)'''

# Labs that log to Weights & Biases; wandb is not preinstalled in Colab.
WANDB_LABS = {10, 13, 14}

WANDB_EXTRA = ("\n\n# This lab logs experiments to Weights & Biases.\n"
               "!pip install -q wandb\n"
               "import wandb as wb")

# A GPU runtime is much faster for these, though no longer required.
GPU_RECOMMENDED = {10, 11, 13, 14}


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
        # dead bootstrap cells left commented out in the source
        if all(l.strip().startswith('#') or not l.strip() for l in s.splitlines()) \
                and ('mpcr' in s or 'pip install' in s):
            continue
        c = {**c, 'metadata': {}}
        if c.get('cell_type') == 'code':
            c['outputs'], c['execution_count'] = [], None
        out.append(c)
        prev = s
    return out


def build(week, slug, title, blurb, objectives, interactive, homework, sources, extra=()):
    head = [f"# Lab {week:02d} — {title}", "", f"*{blurb}*", "", "## Objectives", ""]
    head += [f"{i}. {o}" for i, o in enumerate(objectives, 1)]
    if interactive:
        head += ["", "## Interactive labs for this week", ""]
        head += [f"- [`{os.path.basename(p)}`]({p})" for p in interactive]
    if week in GPU_RECOMMENDED:
        head += ["", "> Runs on CPU, but a **GPU runtime is much faster** for this one: "
                     "*Runtime \u2192 Change runtime type \u2192 T4 GPU*"]
    head += ["", "---"]

    setup = SETUP_CORE + (WANDB_EXTRA if week in WANDB_LABS else '')
    cells = [md('\n'.join(head)), code(setup)]
    used = []
    for path, a, b in sources:
        full = os.path.join(SRC, path)
        src = json.load(open(full))['cells'][a:b]
        kept = clean(src)
        cells += kept
        used.append((path, a, b, len(kept)))

    for kind, text in extra:
        cells.append(md(text) if kind == 'md' else code(text))

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

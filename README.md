# Mathematics of Data Science

**DataSci26 · Fall 2026 · Florida Atlantic University**

An image is a number. A model is a line. Training is a walk downhill.

This course goes from `2 + 2` in a Colab cell to retraining a convolutional network on images you
collected yourself, in fourteen weeks, without skipping the mathematics in between.

Everything runs in a browser. There is nothing to install.

---

## Start here

1. **[Setup guide](setup/)** — Colab, GitHub, and an AI assistant. Do this before Week 2.
2. **[Lab 01](labs/lab01_python-and-colab.ipynb)** — open it in Colab and start running cells.
3. **[Final project](project/)** — read it now. You pick your problem in Week 8.

---

## Schedule

| Wk | Lab | Topic | Interactive | Project |
|:--:|---|---|---|---|
| 1 | [01](labs/lab01_python-and-colab.ipynb) | Python, Colab & your toolchain | | |
| 2 | [02](labs/lab02_numpy-and-simulation.ipynb) | NumPy, vectors & simulating a deck of cards | | |
| 3 | [03](labs/lab03_randomness-and-prngs.ipynb) | Randomness & pseudorandom number generators | | |
| 4 | [04](labs/lab04_normal-distribution.ipynb) | The normal distribution | | |
| 5 | [05](labs/lab05_monte-carlo.ipynb) | Monte Carlo methods | | |
| 6 | [06](labs/lab06_probability-paradoxes.ipynb) | Probability paradoxes | | |
| 7 | [07](labs/lab07_images-as-matrices.ipynb) | Images as matrices | [image](interactive/image1.html) · [colors](interactive/colors.html) · [bits](interactive/bit_depth.html) · [gamma](interactive/gamma.html) | |
| 8 | [08](labs/lab08_image-combinatorics.ipynb) | Image combinatorics & hyperastronomical numbers | [combinatorics](interactive/pixelcombo.html) | **pick your problem** |
| 9 | [09](labs/lab09_linear-fit.ipynb) | Linear fit with real data | [matmul](interactive/matrix_multiplication_lab.html) | **D1 — pitch deck** |
| 10 | [10](labs/lab10_gradient-descent.ipynb) | Gradient descent in PyTorch | | **D2 — website** |
| 11 | [11](labs/lab11_mnist-linear-classifier.ipynb) | MNIST & linear classifiers | | |
| 12 | [12](labs/lab12_convolution.ipynb) | Convolution | [convolution](interactive/Conv1_a.html) · [pooling](interactive/pool.html) | **D3 — notebook** |
| 13 | [13](labs/lab13_alexnet.ipynb) | AlexNet: filters, feature maps & transfer learning | [architecture](interactive/alexnet.html) | |
| 14 | [14](labs/lab14_autoencoders-and-generative.ipynb) | Autoencoders & generative models | | **D4 — poster** |
| 15 | — | Project talks | | **D5 — talk** |

The arc: **weeks 1–6** build the probability and simulation foundation · **weeks 7–8** establish
that images are just arrays · **weeks 9–11** fit models to data, by hand and then by gradient
descent · **weeks 12–14** stack those pieces into a convolutional network and run it backwards.

---

## How the course works

**Labs.** One notebook per week. They are meant to be *run*, cell by cell, with you changing
numbers and seeing what breaks. Reading them does nothing.

**Homework.** Every lab ends with two tasks. Both are written up as a markdown report and pushed
to your GitHub repo. Plots go in the repo next to the report.

**Interactive labs.** Nine browser tools at [`interactive/`](interactive/index.html) that show
the thing the notebook is computing. Use them when a concept will not sit still.

**Project.** Five deliverables from Week 8 on. See [`project/`](project/).

**AI assistants** are allowed everywhere, including on work you submit — with one condition: you
can explain every line you hand in. See the [setup guide](setup/) for the full policy.

---

## Repository layout

```
labs/          14 week-by-week Colab notebooks
interactive/   9 self-contained browser labs + index
project/       final project specification
setup/         tool setup guide
tools/         the build scripts that assemble labs/ from _source/
_source/       archive of six years of prior course material — see _source/INDEX.md
```

`_source/` is the raw material this course was refactored from: 92 notebooks recovered from
six years of Colab links, plus the HTML labs, PDFs, datasets, and every prior syllabus.
It is kept in the repo so any lab can be traced back to where it came from — each lab notebook
ends with a collapsed note naming its source cells.

## Rebuilding the labs

The lab notebooks are assembled, not hand-maintained. To change what goes into a week, edit
[`tools/labs_plan.py`](tools/labs_plan.py) and re-run:

```bash
python3 tools/build_labs.py     # compose labs/ from _source/notebooks/
python3 tools/modernize.py      # patch archived cells to current PyTorch APIs
```

Both are idempotent. Hand-edits to `labs/*.ipynb` are overwritten by a rebuild — change the plan,
not the output.

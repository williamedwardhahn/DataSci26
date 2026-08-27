# Final Project

You will take one network — **AlexNet** — and apply it to a problem you actually care about.

The project runs the whole second half of the semester. It is delivered in **five pieces**, each
building on the last. Nothing is thrown away between deliverables: the slides become the poster,
the notebook becomes the results section, the website is where all of it lives.

Pick your problem by **Week 8**. It should be something where images carry the answer — crop
disease, coral bleaching, sorting parts, reading gauges, identifying species, spotting defects.
If you can photograph it or find a public dataset of it, it works.

---

## Deliverable 1 — Pitch Deck  *(due Week 9)*

A Google Slides deck, split evenly:

**Half 1 — the problem.** What it is, who has it, why it matters, what it costs. Show real
examples of the data. If someone is currently solving this by hand, say how long it takes them.

**Half 2 — the approach.** AlexNet layer by layer, in your own words. What goes in (input size,
preprocessing), what comes out, and how it trains — loss, optimizer, learning rate, epochs.

Set sharing to *anyone with the link can view*. Submit the link on Canvas.

---

## Deliverable 2 — Project Website  *(due Week 10)*

A GitHub Pages site. Not a repo with a README — a site people can read.

- A page on the problem and motivation
- A page on the technical approach
- Sections for visualizations, results, and takeaways

Plain HTML, Markdown, or a Jekyll theme are all fine. Submit the repo URL **and** the live URL.

---

## Deliverable 3 — Colab Notebook  *(due Week 12)*

The working implementation. It must run top to bottom without errors on a fresh runtime.

1. **Implement AlexNet**, adapted to your dataset.
2. **Load your own data** from Drive or GitHub. Your dataset, related to your problem.
3. **Preprocess properly** — resize to 224×224, normalize, and augment (flips, rotations,
   color jitter) where it makes sense.
4. **Train and validate** on a real split. Track accuracy and loss per epoch. Save your weights.
5. **Run the experiments** and report what each one shows:
   - two batch sizes (e.g. 16 vs. 64)
   - two learning rates (e.g. 1e-3 vs. 1e-4)
   - with augmentation vs. without
   - one alternative architecture (ResNet18 or VGG16) for comparison
6. **Log everything to Weights & Biases** — accuracy, loss, confusion matrix.
7. **Interpret the results.** Plots are not conclusions. Say what happened and why.

Set sharing to *anyone with the link can view*. Submit the Colab link.

---

## Deliverable 4 — Scientific Poster  *(due Week 14)*

A conference-style poster, built in Google Slides at 48″ × 36″
(*File → Page setup → Custom*).

Sections: title and authors · problem statement · methods · experiments and results ·
discussion · conclusions and future work.

Your results section should carry the four experiments from Deliverable 3 as charts or tables.
Search "FAU Google Slides poster template" for a starting layout.

---

## Deliverable 5 — Talk  *(Week 15)*

Ten minutes plus questions, presented to the class from your poster and slides.

Be able to answer: *why AlexNet and not something else?* · *what did your experiments actually
show?* · *where does your model fail, and what would you do about it?*

---

## Grading

| Deliverable | Weight |
|---|---|
| 1 — Pitch deck | 15% |
| 2 — Website | 15% |
| 3 — Colab notebook | 35% |
| 4 — Poster | 20% |
| 5 — Talk | 15% |

The notebook carries the most weight because it is the only deliverable that has to be *true*.

---

## Where to start

- `../labs/lab13_alexnet.ipynb` — loading, inspecting, and retraining AlexNet
- `../interactive/alexnet.html` — every layer and shape, interactively
- `../_source/notebooks/MathData25/Alexnet_Final_Project_Template__1R8l5OgR.ipynb` — prior template
- `../_source/datasets/toast/` — a tiny two-class dataset to test your pipeline before your real data

## Funding your project

If the work is good, it can be funded. Both open to undergraduates:

- [FAU Wave](https://www.fau.edu/innovation-and-business-development/fau-wave/)
- [OURI Undergraduate Grants](https://www.fau.edu/ouri/undergraduate-grants/)

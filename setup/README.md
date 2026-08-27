# Setup — do this before Week 2

Three tools. All free, all browser-based, nothing to install.

| Tool | What it is for |
|---|---|
| **Google Colab** | where you write and run every line of Python in this course |
| **GitHub** | where your work lives, and where your project website is hosted |
| **An AI assistant** | Claude or ChatGPT — your always-available tutor |

---

## 1. Google Colab

1. Go to [colab.research.google.com](https://colab.research.google.com) and sign in with a Google account.
2. **New notebook.**
3. Check the runtime: *Runtime → Change runtime type → Python 3*. Leave the accelerator on **CPU**
   for now; you will switch to **T4 GPU** starting Week 10.

Paste this into a cell and run it (`Shift+Enter`):

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
plt.plot(x, np.sin(x))
plt.title("If you can see this curve, Colab works")
plt.show()
```

**Know these four things:** `Shift+Enter` runs a cell · cells share one memory, so order matters ·
*Runtime → Restart* clears everything · a notebook that only runs top-to-bottom-in-order is the
only kind that counts.

---

## 2. GitHub

1. Sign up at [github.com](https://github.com). Pick a username you will not mind putting on a résumé.
2. Create a **public** repo named `datasci26` and check *Add a README file*.
3. Turn on Pages: *Settings → Pages → Source: Deploy from a branch → main / (root)*.
4. Wait about a minute, then visit `https://YOUR-USERNAME.github.io/datasci26/`.

That URL is where every homework report goes this semester. Get it working now, not in Week 6.

To submit work: open your repo, **Add file → Upload files**, drag in your notebook and plots, commit.
That is enough. You do not need the command line for this course.

---

## 3. An AI assistant

Use [Claude](https://claude.ai) or [ChatGPT](https://chatgpt.com). Either is fine.

Try these three, in order, and notice how the answers differ:

> Explain what a convolution does to an image, to someone who knows what a matrix is.

> Write Python that loads a grayscale image from a URL and prints its shape and dtype.

> I got `IndexError: index 3 is out of bounds for axis 0 with size 3`. What did I do wrong?

**How to use it in this course.** Ask it to explain, to debug, and to show you an alternative
approach. Ask it *why*, then check what it told you against the notebook.

**The rule.** You may use AI for anything you submit, but you must be able to explain every line
you hand in. If you cannot walk me through it, it is not yours. Cite it when it wrote something
substantial — a line in your README is enough.

---

## Checklist

- [ ] Colab runs and plots a curve
- [ ] GitHub repo `datasci26` exists and is public
- [ ] GitHub Pages site loads at `https://YOUR-USERNAME.github.io/datasci26/`
- [ ] AI assistant account works
- [ ] Your Pages URL submitted on Canvas

---

## Next: Google Drive

Once all three tools work, read **[drive.md](drive.md)**. It covers getting your own
dataset into Colab, laying it out so `ImageFolder` finds your classes, and saving
trained weights somewhere that survives the session ending. You need it from Week 13.

## Week 2 follow-up

Once the above works, stretch each tool once:

**Colab** — make a styled scatter plot with `s=`, `c=`, `alpha=`, and `plt.colorbar()`.
Change the colormap from `viridis` to `plasma` and to `cool`.

**GitHub** — add a second page to your site and link it from the front page.

**AI assistant** — ask it to load the Iris dataset, train a decision tree, and print the accuracy.
Then ask it to plot the decision boundary for two features. Run both. Find one thing it got wrong
or did clumsily, and fix it yourself.

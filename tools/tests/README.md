# Tests

Seven suites. Run them all:

```bash
./tools/tests/run_all.sh                 # static/consistency/pipeline/interactive/links
./tools/tests/run_all.sh /path/to/python # add asset + execution suites
```

| Suite | Checks | Needs |
|---|---|---|
| `test_static.py` | every cell parses (via IPython's real transformer), no stored outputs, header/setup/homework present | — |
| `test_consistency.py` | README schedule ↔ `labs_plan.py` ↔ lab headers ↔ interactive index ↔ provenance | — |
| `test_pipeline.sh` | rebuilding from `_source/` reproduces what is committed; patch passes are idempotent | — |
| `test_interactive.js` | every `<script>` in the browser labs parses; pages are self-contained | node |
| `test_links.py` | every external URL resolves; bot-blocked hosts reported separately | network |
| `test_assets.py` | datasets open as images and load as a torchvision `ImageFolder`; PDFs are PDFs | pillow, torchvision |
| `test_execute.py` | runs each lab notebook and classifies failures as `BUG`, `colab-only`, `gpu-only`, `network`, `needs-stdin` | full env |

## Environment for the execution suite

The labs are self-contained — no course package, nothing to install from GitHub —
so the test environment is just the scientific stack:

```bash
uv venv --python 3.12 testenv
VIRTUAL_ENV=testenv uv pip install numpy pandas matplotlib scipy sympy requests \
  torch torchvision scikit-image imageio pillow \
  nbformat nbclient ipykernel wandb
testenv/bin/python -m ipykernel install --user --name python3

./tools/tests/run_all.sh testenv/bin/python
```

Cells that call `drive.mount` or `files.upload` raise `ModuleNotFoundError` off-Colab;
the harness classifies those as `colab-only` rather than failures. If you would rather
they fail cleanly, drop a stub on the path:

```bash
SITE=$(testenv/bin/python -c "import site;print(site.getsitepackages()[0])")
mkdir -p "$SITE/google/colab" && touch "$SITE/google/__init__.py"
cat > "$SITE/google/colab/__init__.py" <<'EOF'
class _D:
    def mount(self, *a, **k): raise RuntimeError("Colab-only")
drive = _D()
class _F:
    def upload(self, *a, **k): raise RuntimeError("Colab-only")
    def download(self, *a, **k): raise RuntimeError("Colab-only")
files = _F()
EOF
```

## Reading the execution results

Only `BUG` counts as a failure. The other categories are cells that cannot work
outside Colab or off a GPU and are expected to fail locally:

- **`colab-only`** — Drive mount, `files.upload`, `apt-get`, webcam capture, `wandb.login`
- **`gpu-only`** — a cell that genuinely needs CUDA (for example loading a checkpoint that was
  serialized from a GPU tensor). The labs themselves are device-agnostic
- **`network`** — transient fetch failures
- **`needs-stdin`** — cells that call `input()`

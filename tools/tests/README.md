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

The labs target Colab. To run them off-Colab you need the scientific stack plus
a stub for `google.colab`, which `mpcr` imports at module level:

```bash
uv venv --python 3.12 testenv
VIRTUAL_ENV=testenv uv pip install numpy matplotlib torch torchvision scikit-image \
  imageio scipy pandas pillow seaborn nbformat nbclient ipykernel requests \
  torchsummary scikit-learn opencv-python-headless nltk wget barbar flashtorch pip
VIRTUAL_ENV=testenv uv pip install "git+https://github.com/williamedwardhahn/mpcr"
testenv/bin/python -m ipykernel install --user --name python3

# mpcr does `from google.colab import drive` at import time
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

./tools/tests/run_all.sh testenv/bin/python
```

`pip` is required in the venv because `mpcr` shells out to
`python -m pip install` for `flashtorch`, `barbar`, and `wandb` at import time.

## Reading the execution results

Only `BUG` counts as a failure. The other categories are cells that cannot work
outside Colab or off a GPU and are expected to fail locally:

- **`colab-only`** — Drive mount, `files.upload`, `apt-get`, webcam capture, `wandb.login`
- **`gpu-only`** — `mpcr`'s `GPU()`/`GPU_data()` build tensors on `device='cuda'` unconditionally,
  so labs 10, 11, 13, and 14 need a GPU runtime
- **`network`** — transient fetch failures
- **`needs-stdin`** — cells that call `input()`

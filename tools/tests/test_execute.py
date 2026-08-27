"""Execute lab notebooks and classify every failure.

Usage:  test_execute.py [lab-number ...]      (default: all)

Cells that can only work inside Colab (Drive mount, file upload, webcam, wandb
login) are expected to fail off-Colab and are reported separately from real bugs.
"""
import json, os, re, sys, glob, tempfile, traceback

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

COLAB_ONLY = re.compile(
    r'drive\.mount|files\.upload|files\.download|google\.colab|cv2\.VideoCapture|'
    r'wandb\.login|wandb\.init|\bwb\.init|\bwb\.log|eval_js|Javascript\(|getUserMedia|'
    r'from IPython\.display import Javascript|!apt-get|!apt |apt-get install', re.I)
NEEDS_INPUT = re.compile(r'(?<!\.)\binput\s*\(')


def classify(src, err, unbound=(), gpu_failed=False):
    m = re.match(r"NameError: name '(\w+)' is not defined", err or '')
    if m and m.group(1) in unbound:
        return 'cascade'
    e = err or ''
    name = e.split(':')[0].strip()
    # a cell we interrupted for overrunning the per-cell budget
    if name in ('KeyboardInterrupt', 'CellTimeoutError') or 'timed out' in e:
        return 'too-slow-on-cpu'
    # wandb needs an interactive login; it is configured per-student in Colab
    if 'No API key configured' in e or 'wandb' in e.lower():
        return 'needs-credentials'
    if COLAB_ONLY.search(src):
        return 'colab-only'
    if NEEDS_INPUT.search(src):
        return 'needs-stdin'
    if name in ('URLError', 'HTTPError', 'ConnectionError', 'ConnectTimeout',
                'ReadTimeout', 'gaierror', 'SSLError', 'RemoteDisconnected',
                'TimeoutError', 'timeout', 'IncompleteRead'):
        return 'network'
    # Second-order GPU cascade: mpcr's GPU()/GPU_data() failed, so what should be a
    # CUDA tensor is still a numpy array and every tensor method on it now fails.
    if gpu_failed and (
            "'numpy.ndarray' object has no attribute" in e
            or 'must be Tensor, not numpy.ndarray' in e
            or 'should be Tensor Image' in e
            or 'sub-type of ndarray' in e
            or 'cannot reshape array of size' in e):
        return 'cascade'
    if 'CUDA' in (err or '') or 'cuda' in (err or ''):
        return 'gpu-only'
    if 'out of memory' in (err or '').lower():
        return 'resource'
    return 'BUG'


def run(path, timeout=180, workdir=None):
    """Execute one notebook. `workdir` is the kernel's cwd -- never the repo, or
    the labs will litter it with MNIST downloads and generated pages."""
    import nbformat
    from nbclient import NotebookClient
    from nbclient.exceptions import CellExecutionError

    nb = nbformat.read(path, as_version=4)
    # the setup cell pip-installs from GitHub every run; the test env already has it
    for c in nb.cells:
        if c.cell_type == 'code' and 'pip install' in c.source and 'mpcr' in c.source:
            c.source = '\n'.join(l for l in c.source.splitlines()
                                 if not l.strip().startswith('!'))
    nb.cells.insert(0, nbformat.v4.new_code_cell(
        "import matplotlib; matplotlib.use('Agg')\n"
        "import warnings; warnings.filterwarnings('ignore')"))

    client = NotebookClient(nb, timeout=timeout, kernel_name='python3',
                            allow_errors=True, interrupt_on_timeout=True,
                            resources={'metadata': {'path': workdir or ROOT}})
    client.execute()

    results, unbound, gpu_failed = [], set(), False
    for i, c in enumerate(nb.cells):
        if c.cell_type != 'code':
            continue
        err = next((o for o in c.get('outputs', []) if o.output_type == 'error'), None)
        if not err:
            continue
        full = f"{err.ename}: {err.evalue}"
        kind = classify(c.source, full, unbound, gpu_failed)
        if kind == 'gpu-only':
            gpu_failed = True
        # names this cell would have bound had it run are now poisoned downstream
        for name in re.findall(r'^\s*(?:for\s+)?([A-Za-z_]\w*)\s*(?:,\s*\w+\s*)?=(?!=)',
                               c.source, re.M):
            unbound.add(name)
        for name in re.findall(r'^\s*(?:def|class)\s+(\w+)', c.source, re.M):
            unbound.add(name)
        for name in re.findall(r'^\s*(?:from\s+[\w.]+\s+)?import\s+(.+)$', c.source, re.M):
            for part in name.split(','):
                unbound.add(part.strip().split(' as ')[-1].strip().split('.')[0])
        results.append((i, kind, full.replace('\n', ' ')[:150],
                        c.source.strip().splitlines()[0][:70] if c.source.strip() else ''))
    return len([c for c in nb.cells if c.cell_type == 'code']), results


def main():
    wanted = sys.argv[1:]
    labs = sorted(glob.glob(os.path.join(ROOT, 'labs', '*.ipynb')))
    if wanted:
        labs = [p for p in labs if any(f'lab{int(w):02d}_' in os.path.basename(p) for w in wanted)]

    grand = {}
    # one scratch cwd for the whole run: notebooks download MNIST and write files,
    # and none of that belongs in the repository
    harness_errors = []
    scratch = tempfile.mkdtemp(prefix='datasci26-exec-')
    print(f'kernel working directory: {scratch}\n')
    for p in labs:
        name = os.path.basename(p)
        try:
            total, fails = run(p, workdir=scratch)
        except Exception as e:
            print(f'{name}: HARNESS ERROR {type(e).__name__}: {e}')
            harness_errors.append(name)
            continue
        buckets = {}
        for i, kind, msg, first in fails:
            buckets.setdefault(kind, []).append((i, msg, first))
        bugs = len(buckets.get('BUG', []))
        ok = total - len(fails)
        status = 'PASS' if bugs == 0 else f'{bugs} BUG(S)'
        summary = ', '.join(f'{k}:{len(v)}' for k, v in sorted(buckets.items()) if k != 'BUG')
        print(f'{name:46} {ok:3}/{total:<3} ran   {status}' + (f'   [{summary}]' if summary else ''))
        for i, msg, first in buckets.get('BUG', []):
            print(f'      cell {i:3}: {msg}')
            print(f'                 > {first}')
        grand[name] = (total, ok, bugs)

    tb = sum(v[2] for v in grand.values())
    print(f'\n{len(grand)}/{len(labs)} labs, {sum(v[0] for v in grand.values())} code cells, '
          f'{sum(v[1] for v in grand.values())} ran clean, {tb} real bug(s)')
    if harness_errors:
        print(f'{len(harness_errors)} lab(s) did not run at all: ' + ', '.join(harness_errors))
    return 1 if (tb or harness_errors or len(grand) != len(labs)) else 0


if __name__ == '__main__':
    sys.exit(main())

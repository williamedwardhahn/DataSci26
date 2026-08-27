"""Post-build pass: update archived cells to current PyTorch / torchvision APIs.

Applied to labs/*.ipynb after build_labs.py. Idempotent.
"""
import json, glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RULES = [
    # torchvision weights API (pretrained= was removed)
    (r'alexnet\(\s*pretrained\s*=\s*True\s*\)',
     'alexnet(weights=AlexNet_Weights.DEFAULT)',
     'torchvision weights API'),
    (r'(\w+)\(\s*pretrained\s*=\s*True\s*\)',
     r'\1(weights="DEFAULT")',
     'torchvision weights API'),
    # autograd.Variable was merged into Tensor in PyTorch 0.4
    (r'Variable\(\s*randn\((.*?)\),\s*requires_grad\s*=\s*True\s*\)',
     r'torch.randn(\1, requires_grad=True)',
     'Variable -> Tensor'),
    (r'Variable\(\s*(.+?)\.cuda\(\)\s*\)',
     r'\1.to(device)',
     'Variable + .cuda -> .to(device)'),
    (r'torch\.tensor\(\s*(\w+)\s*\)\.cuda\(\s*\d*\s*\)',
     r'\1.to(device)',
     'redundant torch.tensor + .cuda'),
    # Pad the block-convolution kernel to the 5x5 block size. Anchored to the start of a
    # line: the same expression also appears commented out in the direct-convolution cell,
    # where the kernel is 3x3 and must stay that way.
    (r'(?m)^a=np\.matrix\(\[\[1,2,1\],\[0,0,0\],\[-1,-2,-1\]\]\)$',
     'a = np.zeros((5, 5))                       # kernel must match the 5x5 block size\n'
     'a[1:4, 1:4] = [[1, 2, 1], [0, 0, 0], [-1, -2, -1]]   # 3x3 Sobel, zero-padded',
     'kernel padded to block size'),
    # Several archived cells redefine GPU()/GPU_data() with a hardcoded CUDA device,
    # shadowing the device-aware versions from the setup cell. Honour `device` instead.
    (r"device\s*=\s*torch\.device\(\s*['\"]cuda['\"]\s*\)", 'device=device',
     'hardcoded cuda device -> active device'),
    # skimage dropped `multichannel=` in 0.19 in favour of `channel_axis=`
    (r'multichannel\s*=\s*True', 'channel_axis=-1', 'skimage multichannel -> channel_axis'),
    # imageio/skimage now return an animated GIF as a (frames, H, W, C) stack, so the
    # old `image[:, 0:700, :]` slices the wrong axes. Reduce to the first frame.
    (r'(?m)^([ \t]*)(\w+)\s*=\s*((?:skio|io|imageio)\.imread\(["\'][^"\']*\.gif["\']\))\s*$',
     r'\1\2 = \3\n\1\2 = \2[0] if \2.ndim == 4 else \2  # animated GIF -> first frame',
     'GIF read returns a frame stack'),
    # device-agnostic: .cuda() hard-fails on a CPU runtime
    (r'\.cuda\(\s*\d*\s*\)', '.to(device)', '.cuda -> .to(device)'),
    (r'Variable\(\s*([^()]*(?:\([^()]*\))?[^()]*)\s*\)', r'\1', 'Variable -> Tensor'),
]

# Straight text rewrites for archived cells that are simply wrong on current stacks.
REWRITE = [
    # display/HTML moved out of IPython.core.display in IPython 8
    ('from IPython.core.display import display, HTML',
     'from IPython.display import display, HTML',
     'IPython.core.display -> IPython.display'),
    # The block-convolution demo never ran: the kernel is 3x3 but the blocks are 5x5
    # (the image is resized to 150x700, which only divides by 5), so reshape(25, -1)
    # raises -- and even at the right size, `blocks_vec * a1` does not reduce over the
    # block. Zero-pad the kernel to the block size and take the dot product per block.
    ('a1 = a.reshape(25, -1)',
     'a1 = np.asarray(a).reshape(-1)             # flatten the kernel to one weight per pixel',
     'kernel flattened to a vector'),
    ('z=blocks_vec*a1',
     'z = (blocks_vec * a1).sum(axis=2)          # dot product of each block with the kernel',
     'block dot product now reduces'),
    # This annealing variant of the random walk has its three initialisers commented
    # out -- it relied on w*_best still being in memory from the previous cell's run.
    # Top to bottom it raises NameError, so restore them.
    ('# w0_best = 0\n# w1_best = 0\n# w2_best = 0',
     'w0_best = 0\nw1_best = 0\nw2_best = 0',
     'restored commented-out initialisers'),
    # the source has this import commented out, so view_as_windows is never defined
    ('blocks = view_as_windows(image, block_shape)',
     'from skimage.util import view_as_windows\n'
     'blocks = view_as_windows(image, block_shape)',
     'restore commented-out view_as_windows import'),
    # the `wget` module is never imported anywhere; use the stdlib instead
    ('wget.download(url,"W.data")',
     'urllib.request.urlretrieve(url, "W.data")',
     'undefined wget -> urllib'),
]

# Cells that inspect a name before anything binds it -- live-coding leftovers that
# break a top-to-bottom run. (lab prefix, exact source, name that must not be bound yet)
DROP_UNBOUND = [
    ('lab12', 'l.shape', 'l'),
]

# Lab-scoped rules: (lab prefix, regex, replacement, label)
LAB_RULES = [
    # lab11's random-search loops run up to 10,000,000 iterations, and each one is a
    # matmul over all 60,000 MNIST images. They never ran before -- GPU_data() raised
    # first -- so nobody noticed. Capped at a size that finishes; the lesson is the
    # shape of the curve, not the iteration count. Raise them if you have the time.
    ('lab11', r'range\((?:100000|1000000|10000000)\)', 'range(10000)',
     'capped a search loop that cannot finish'),
]

# Rules that only apply after a given cell. Live-coding notebooks change the shape of
# a variable partway through and the cells above never get updated.
# (lab prefix, anchor regex, regex, replacement, label)
AFTER_RULES = [
    # lab11 concatenates a bias row onto X, making it 785 rows. Every weight matrix
    # built after that is still hardcoded to 784 and the matmul fails. Derive the
    # width from X instead, which is right on both sides of the bias cell.
    ('lab11', r'X\s*=\s*torch\.concatenate\(\[bias\s*,\s*X\]\)',
     r'\b784\b', 'X.shape[0]', 'weight width derived from X, not hardcoded 784'),
]

IMPORT_FIX = ('from torchvision.models import alexnet',
              'from torchvision.models import alexnet, AlexNet_Weights')


GIF_MARK = 'animated GIF -> first frame'


def patch(text):
    changes = []
    for old, new, label in REWRITE:
        if old not in text:
            continue
        # An "augmenting" rewrite keeps `old` and prepends to it (e.g. adds a missing
        # import). Re-running must not stack the addition, so skip if it is already there.
        if old in new:
            addition = new.split(old)[0]
            if addition and addition in text:
                continue
        text = text.replace(old, new)
        changes.append((label, 1))
    if 'urllib.request.urlretrieve' in text and 'import urllib' not in text:
        text = 'import urllib.request\n' + text
        changes.append(('add urllib import', 1))
    for rx, rep, label in RULES:
        if label == 'GIF read returns a frame stack' and GIF_MARK in text:
            continue                      # already guarded; do not append it twice
        new, n = re.subn(rx, rep, text)
        if n:
            changes.append((label, n))
            text = new
    if 'AlexNet_Weights' in text and IMPORT_FIX[0] in text and IMPORT_FIX[1] not in text:
        text = text.replace(IMPORT_FIX[0], IMPORT_FIX[1])
        changes.append(('AlexNet_Weights import', 1))
    return text, changes


def main():
    total = 0
    for p in sorted(glob.glob(os.path.join(ROOT, 'labs', '*.ipynb'))):
        nb = json.load(open(p))
        base = os.path.basename(p)
        touched = []

        for prefix, anchor, rx, rep, label in AFTER_RULES:
            if not base.startswith(prefix):
                continue
            start = None
            for i, c in enumerate(nb['cells']):
                if c['cell_type'] == 'code' and re.search(anchor, ''.join(c['source'])):
                    start = i
                    break
            if start is None:
                continue
            for i, c in enumerate(nb['cells'][start + 1:], start=start + 1):
                if c['cell_type'] != 'code':
                    continue
                new, n = re.subn(rx, rep, ''.join(c['source']))
                if n:
                    c['source'] = new.splitlines(keepends=True)
                    touched.append((i, [(label, n)]))

        for prefix, rx, rep, label in LAB_RULES:
            if not base.startswith(prefix):
                continue
            for i, c in enumerate(nb['cells']):
                if c['cell_type'] != 'code':
                    continue
                new, n = re.subn(rx, rep, ''.join(c['source']))
                if n:
                    c['source'] = new.splitlines(keepends=True)
                    touched.append((i, [(label, n)]))

        # drop live-coding leftovers that reference a name nothing has bound yet
        for prefix, exact, name in DROP_UNBOUND:
            if not base.startswith(prefix):
                continue
            bound = False
            keep = []
            for c in nb['cells']:
                src = ''.join(c['source'])
                if c['cell_type'] == 'code' and src.strip() == exact and not bound:
                    print(f'  {base}: dropped `{exact}` (nothing binds {name} yet)')
                    continue
                if c['cell_type'] == 'code' and re.search(rf'^\s*{name}\s*=(?!=)', src, re.M):
                    bound = True
                keep.append(c)
            if len(keep) != len(nb['cells']):
                nb['cells'] = keep
                touched.append((-1, [('drop unbound inspection', 1)]))
        for i, c in enumerate(nb['cells']):
            if c['cell_type'] != 'code':
                continue
            s = ''.join(c['source'])
            new, changes = patch(s)
            if changes:
                c['source'] = new.splitlines(keepends=True)
                touched.append((i, changes))
        if touched:
            json.dump(nb, open(p, 'w'), indent=1)
            total += len(touched)
            print(f"  {os.path.basename(p)}")
            for i, ch in touched:
                print(f"     cell {i:3}: " + ", ".join(f"{l} x{n}" for l, n in ch))
    print(f"\n{total} cells modernized")


if __name__ == '__main__':
    main()

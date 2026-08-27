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
    # device-agnostic: .cuda() hard-fails on a CPU runtime
    (r'\.cuda\(\s*\d*\s*\)', '.to(device)', '.cuda -> .to(device)'),
    (r'Variable\(\s*([^()]*(?:\([^()]*\))?[^()]*)\s*\)', r'\1', 'Variable -> Tensor'),
]

IMPORT_FIX = ('from torchvision.models import alexnet',
              'from torchvision.models import alexnet, AlexNet_Weights')


def patch(text):
    changes = []
    for rx, rep, label in RULES:
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
        touched = []
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

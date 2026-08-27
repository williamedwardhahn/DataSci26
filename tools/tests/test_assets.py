"""Check the shipped datasets and PDFs actually open."""
import glob, os, sys

try:
    from PIL import Image
except ImportError:
    print('SKIP — pillow not installed'); sys.exit(0)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
fails = []

print('--- image datasets ---')
for ds in ('_source/datasets/toast', '_source/datasets/catdog'):
    d = os.path.join(ROOT, ds)
    imgs = [p for p in glob.glob(os.path.join(d, '**', '*'), recursive=True)
            if os.path.isfile(p) and not p.endswith('.md')]
    good, bad = 0, []
    sizes = []
    for p in imgs:
        try:
            with Image.open(p) as im:
                im.verify()
            with Image.open(p) as im:
                sizes.append(im.size); good += 1
        except Exception as e:
            bad.append((os.path.relpath(p, ROOT), type(e).__name__))
    classes = sorted({os.path.basename(os.path.dirname(p)) for p in imgs})
    print(f'  {ds:28} {good}/{len(imgs)} open   classes={classes}')
    if sizes:
        w = [s[0] for s in sizes]; h = [s[1] for s in sizes]
        print(f'  {"":28} sizes {min(w)}x{min(h)} .. {max(w)}x{max(h)}')
    for rel, err in bad:
        fails.append(f'{rel}: {err}')

print('--- torchvision can build an ImageFolder from them ---')
try:
    from torchvision import datasets, transforms
    tf = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor()])
    for ds, sub in (('_source/datasets/toast', 'train'), ('_source/datasets/catdog', 'train')):
        root = os.path.join(ROOT, ds, sub)
        if not os.path.isdir(root):
            fails.append(f'{ds}/{sub} not a directory'); continue
        d = datasets.ImageFolder(root, transform=tf)
        x, y = d[0]
        print(f'  {ds+"/"+sub:34} {len(d):3} images, {len(d.classes)} classes {d.classes}, tensor {tuple(x.shape)}')
except ImportError:
    print('  SKIP — torchvision not installed')
except Exception as e:
    fails.append(f'ImageFolder: {type(e).__name__}: {e}')

print('--- pdfs ---')
for p in sorted(glob.glob(os.path.join(ROOT, '_source', 'pdfs', '*.pdf'))):
    with open(p, 'rb') as f:
        head = f.read(5)
    size = os.path.getsize(p)
    ok = head == b'%PDF-'
    print(f'  {"ok " if ok else "BAD"} {os.path.basename(p):42} {size/1e6:6.2f} MB')
    if not ok:
        fails.append(f'{os.path.basename(p)}: not a PDF (magic {head!r})')

print()
if fails:
    print(f'{len(fails)} FAILURES')
    for f in fails: print('  ' + f)
    sys.exit(1)
print('PASS — all datasets and PDFs valid')

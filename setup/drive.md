# Using Google Drive with Colab

Colab runtimes are temporary. Anything you write to the runtime's own disk is gone
when the session ends — usually within a few hours, sooner if you close the tab.
Google Drive is how your data and your trained models survive that.

You will need this from **Week 13** onward, and for the whole final project.

---

## 1. Mount your Drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

Run it, click the link, pick your account, approve. Your Drive then appears at:

```
/content/drive/MyDrive/
```

That is the same "My Drive" you see at drive.google.com. A file you drop in the
browser shows up at that path in Colab within a few seconds.

You have to re-run `drive.mount` in every new session. It is not permanent.

---

## 2. Lay your dataset out like this

Make a folder in your Drive named `datasci26`, and inside it put your project data
in **one folder per class**:

```
MyDrive/datasci26/mydata/
├── train/
│   ├── healthy/      ← 30+ images
│   └── diseased/     ← 30+ images
└── test/
    ├── healthy/      ← 10+ images
    └── diseased/     ← 10+ images
```

The folder names *become* the class labels. Nothing else configures them. Keep them
lowercase, no spaces — `class_to_idx` sorts them alphabetically, so `burnt` is 0 and
`good` is 1.

Put images in `test/` that are **not** in `train/`. If the same photo appears in both,
your accuracy number is meaningless.

---

## 3. Copy it to local disk before training

This is the part people get wrong. Drive is mounted over the network, and reading a
few thousand small image files through it is slow enough to dominate your training
time. Zip the folder once, and unzip it onto the runtime's local disk:

```python
# one-time, on your own machine: zip mydata/ and put mydata.zip in Drive
!cp '/content/drive/MyDrive/datasci26/mydata.zip' /content/
!unzip -q /content/mydata.zip -d /content/data
DATA = '/content/data/mydata'
```

Now every epoch reads from local disk. Do this once per session; it takes seconds
and can turn a 20-minute epoch into a 40-second one.

Keep the *data* on local disk and the *results* on Drive.

---

## 4. Load it

```python
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

train_tf = transforms.Compose([
    transforms.Resize((224, 224)),          # AlexNet expects 224x224
    transforms.RandomHorizontalFlip(),      # augmentation: train only
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

test_tf = transforms.Compose([              # no augmentation on test
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

train_set = datasets.ImageFolder(f'{DATA}/train', transform=train_tf)
test_set  = datasets.ImageFolder(f'{DATA}/test',  transform=test_tf)

train_loader = DataLoader(train_set, batch_size=32, shuffle=True,  num_workers=2)
test_loader  = DataLoader(test_set,  batch_size=32, shuffle=False, num_workers=2)

print(train_set.classes)        # ['diseased', 'healthy']
print(train_set.class_to_idx)   # {'diseased': 0, 'healthy': 1}
print(len(train_set), len(test_set))
```

Always print those three lines. If `classes` is wrong, your folder layout is wrong,
and every number after this point is wrong too.

Those normalization constants are the ImageNet statistics AlexNet was trained with.
Use them whenever you start from pretrained weights.

---

## 5. Point AlexNet at your classes

A pretrained AlexNet ends in a 1000-way layer for ImageNet. Replace it:

```python
import torch.nn as nn
from torchvision.models import alexnet, AlexNet_Weights

net = alexnet(weights=AlexNet_Weights.DEFAULT)
net.classifier[6] = nn.Linear(4096, len(train_set.classes))
net = net.to(device)
```

To train only the new head and leave the learned features alone:

```python
for p in net.features.parameters():
    p.requires_grad = False
```

---

## 6. Save your work back to Drive

```python
import torch, os

OUT = '/content/drive/MyDrive/datasci26/results'
os.makedirs(OUT, exist_ok=True)

torch.save(net.state_dict(), f'{OUT}/alexnet_run1.pt')   # weights
plt.savefig(f'{OUT}/accuracy_curve.png', dpi=150)        # a figure
```

Reload them later — in a completely new session — with:

```python
net = alexnet()
net.classifier[6] = nn.Linear(4096, 2)
net.load_state_dict(torch.load(f'{OUT}/alexnet_run1.pt', weights_only=True))
net.eval()
```

`weights_only=True` is the safe default in current PyTorch. Keep it.

Save a checkpoint **every few epochs**, not just at the end. Colab will disconnect
you mid-run at some point this semester, and an unsaved four-hour run is gone.

---

## 7. Three alternatives worth knowing

**Small dataset? Use GitHub instead.** Under ~50 MB, commit it to your project repo
and skip Drive entirely. It is reproducible, it needs no mounting, and anyone can
rerun your notebook:

```python
!git clone -q https://github.com/YOUR-USERNAME/YOUR-REPO
DATA = 'YOUR-REPO/data'
```

**One shared file by link.** For a single file already shared "anyone with the link":

```python
import urllib.request
FILE_ID = '1AbC...'      # the long id in the sharing URL
urllib.request.urlretrieve(
    f'https://drive.google.com/uc?export=download&id={FILE_ID}', 'data.zip')
```

**Images pasted into Google Slides.** The trick from Lab 07 — build a deck, paste
your images onto slides, share it "anyone with the link", and pull every slide down
as an array. Good for a quick dataset you assemble by hand in ten minutes.

---

## Troubleshooting

| What you see | What it means |
|---|---|
| `FileNotFoundError` on a path that exists | You did not re-run `drive.mount` in this session |
| `MessageError: Error: credential propagation was unsuccessful` | Re-run the mount cell and complete the popup; check the pop-up blocker |
| `Found 0 files in subfolders` | Path points at the parent, not at `train/`; or the images sit loose instead of in per-class folders |
| Only one class in `classes` | Your other class folder is empty, or misspelled |
| Training crawls | You are reading from `/content/drive/...` — copy to `/content/` first (§3) |
| `.ipynb_checkpoints` shows up as a class | `!rm -rf {DATA}/train/.ipynb_checkpoints` |
| Session died, work gone | Checkpoint to Drive every few epochs (§6) |

---

## Checklist before you train

- [ ] Drive mounted this session
- [ ] Data unzipped to `/content/`, not read over the mount
- [ ] `train_set.classes` prints exactly the classes you expect
- [ ] No image appears in both `train/` and `test/`
- [ ] `results/` folder exists in Drive
- [ ] Runtime set to T4 GPU

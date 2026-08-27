"""Week-by-week composition plan: each lab is assembled from sections of the archived notebooks."""

# (week, slug, title, blurb, objectives[], interactive[], homework[],
#  sources[(path, start, end)], extra[(kind, text)])

ALEXNET_TRANSFER = [
 ('md', """---

## Transfer learning: retrain AlexNet on your own images

Everything above inspects a network that already works. Now we point it at a problem
it has never seen.

We use the classic ants-vs-bees set — 245 training photos, 153 for validation. Small
enough to train on a CPU runtime, hard enough to be interesting.

Swap in your own folder and nothing else changes. **The folder names are the class
labels:**

```
mydata/
├── train/burnt/ ...   train/good/ ...
└── val/burnt/   ...   val/good/  ...
```

See [`../setup/drive.md`](../setup/drive.md) for getting your own data in from Drive."""),

 ('code', """import os, urllib.request, zipfile

if not os.path.isdir('hymenoptera_data'):
    urllib.request.urlretrieve(
        'https://download.pytorch.org/tutorial/hymenoptera_data.zip', 'hym.zip')
    zipfile.ZipFile('hym.zip').extractall('.')

DATA = 'hymenoptera_data'          # <- point this at your own folder in Drive"""),

 ('code', """from torch.utils.data import DataLoader

train_tf = transforms.Compose([
    transforms.Resize((224, 224)),           # AlexNet's input size
    transforms.RandomHorizontalFlip(),       # augmentation: training only
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

val_tf = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

train_set = datasets.ImageFolder(f'{DATA}/train', transform=train_tf)
val_set   = datasets.ImageFolder(f'{DATA}/val',   transform=val_tf)

train_loader = DataLoader(train_set, batch_size=16, shuffle=True)
val_loader   = DataLoader(val_set,   batch_size=16)"""),

 ('code', """# Always check this before training. If the classes are wrong, everything after is wrong.
print(train_set.classes)
print(train_set.class_to_idx)
print(len(train_set), 'train /', len(val_set), 'val')"""),

 ('code', """images, targets = next(iter(train_loader))
print(images.shape)                          # (batch, 3, 224, 224)
plot(montage(images[:9, 0, :, :].numpy()))   # `plot` is defined earlier in this lab"""),

 ('md', """Those normalization numbers are the ImageNet statistics AlexNet was trained on. Use
them whenever you start from pretrained weights.

AlexNet ends in a 1000-way layer, one output per ImageNet class. Replace that last
layer with one that has an output per class of *yours*. Everything before it — the
filters and feature maps you just visualised — is kept."""),

 ('code', """net = alexnet(weights=AlexNet_Weights.DEFAULT)
net.classifier[6] = nn.Linear(4096, len(train_set.classes))
net = net.to(device)
net.classifier"""),

 ('code', """# Freeze the learned features; train only the new head.
for p in net.features.parameters():
    p.requires_grad = False

optimizer = torch.optim.Adam(net.classifier.parameters(), lr=1e-4)
loss_fn = nn.CrossEntropyLoss()"""),

 ('code', """for epoch in range(3):
    net.train()
    total = 0.0
    for x, t in train_loader:
        x, t = x.to(device), t.to(device)
        optimizer.zero_grad()
        loss = loss_fn(net(x), t)
        loss.backward()
        optimizer.step()
        total += loss.item()
    print(f'epoch {epoch}  loss {total/len(train_loader):.4f}')"""),

 ('code', """net.eval()
correct = n = 0
with torch.no_grad():
    for x, t in val_loader:
        x, t = x.to(device), t.to(device)
        correct += (net(x).argmax(1) == t).sum().item()
        n += t.shape[0]
print(f'validation accuracy: {correct}/{n} = {correct/n:.1%}')"""),

 ('md', """Three epochs on a frozen backbone should land in the 90s. ImageNet contains neither
of these classes — what you retrained is one 4096-to-2 layer sitting on features that
already knew what edges and texture are.

Save the weights so a new session can pick them up (see `drive.md` §6)."""),

 ('code', """torch.save(net.state_dict(), 'alexnet_antsbees.pt')

# reload into a fresh model
net2 = alexnet()
net2.classifier[6] = nn.Linear(4096, len(train_set.classes))
net2.load_state_dict(torch.load('alexnet_antsbees.pt', weights_only=True))
net2.eval()
print('reloaded')"""),
]


PLAN = [
 (1, "python-and-colab", "Python, Colab & Your Toolchain",
  "Everything runs in the browser. By the end of today you can compute, name things, make a vector, and draw a graph.",
  ["Use Colab as a calculator and know how a notebook actually executes",
   "Create variables and reason about integer vs. float division and modular arithmetic",
   "Build a NumPy vector and plot y = mx + b",
   "Have GitHub, Colab, and an AI assistant set up and connected"],
  [], ["Work through every cell; change a number in at least five of them and note what happened.",
       "Push a `README.md` to a new GitHub repo with a plot you made and one sentence about it."],
  [("Math24/Lab_1__1aCFpU60.ipynb", 0, 59)]),

 (2, "numpy-and-simulation", "NumPy, Vectors & Simulating a Deck of Cards",
  "NumPy is the language the rest of the course is written in. We use a card deck as the first real simulation.",
  ["Index, slice, and reshape NumPy arrays",
   "Generate and manipulate arrays without writing Python loops",
   "Represent a deck of cards as an array and deal random hands",
   "Write a function that scores a hand"],
  [], ["Extend the hand ranker to detect a full house.",
       "Estimate P(flush) by dealing 100,000 hands. Compare to the exact value."],
  [("Math24/Lab_1__1aCFpU60.ipynb", 59, 124)]),

 (3, "randomness-and-prngs", "Randomness & Pseudorandom Number Generators",
  "Computers cannot make random numbers. Understanding what they make instead is the foundation for everything statistical.",
  ["Implement a linear congruential generator from scratch",
   "See how a bad seed or bad modulus destroys randomness",
   "Use NumPy's generator correctly and reproducibly",
   "Test a stream of numbers for uniformity"],
  [], ["Find LCG parameters that produce a visibly short cycle. Plot it.",
       "Write a paragraph: what would break in Lab 5 if your PRNG were biased?"],
  [("Math24/Lab_2__1IEV3ROU.ipynb", 3, 22),
   ("Probability_Statistics/Lab_#4__1SyGqBZT.ipynb", 36, 86)]),

 (4, "normal-distribution", "The Normal Distribution",
  "Where the bell curve comes from, why it is everywhere, and how to generate one from uniform noise.",
  ["Build a normal distribution by summing uniform random variables",
   "See the Central Limit Theorem happen numerically",
   "Compute and interpret mean, variance, and standard deviation",
   "Fit a normal curve to a histogram"],
  [],
  ["Sum 2, 5, and 50 uniforms. Plot all three histograms on one figure.",
   "Collect 30 real measurements of something. Is the distribution normal? Argue with a plot."],
  [("Math24/Lab_2__1IEV3ROU.ipynb", 22, 87)]),

 (5, "monte-carlo", "Monte Carlo Methods",
  "If you can sample it, you can estimate it. We compute pi and e from nothing but random numbers.",
  ["Estimate pi by sampling points in a square",
   "Estimate e from random draws",
   "Understand why Monte Carlo error shrinks as 1/sqrt(N)",
   "Visualize an estimate converging"],
  [], ["Plot your pi estimate vs. N on a log axis. Does the error follow 1/sqrt(N)?",
       "Use Monte Carlo to estimate the area of a shape that has no closed-form area."],
  [("Math24/Lab_2__1IEV3ROU.ipynb", 89, 110),
   ("Math24/Lab_4__1aYRkPer.ipynb", 0, 50)]),

 (6, "probability-paradoxes", "Probability Paradoxes",
  "Four problems where intuition is confidently wrong, and the simulation that settles each one.",
  ["Simulate the Birthday Paradox and find the crossover point",
   "Settle Monty Hall by experiment rather than argument",
   "Compute the house edge in craps",
   "Solve the Collector's Card Paradox (how many packs to complete the set?)"],
  [], ["Pick one paradox. Write a short report with your simulation, a plot, and the exact answer.",
       "Post the report to your GitHub Pages site."],
  [("Math24/Lab_3__1e17k65M.ipynb", 1, 51)]),

 (7, "images-as-matrices", "Images as Matrices",
  "An image is a number. Once you believe that, every operation in the rest of the course is arithmetic.",
  ["Load an image from a URL and from Google Slides into a NumPy array",
   "Read shape, dtype, and channel order without guessing",
   "Slice, crop, and recolor an image by indexing",
   "Convert between binary, grayscale, and RGB"],
  ["../interactive/image1.html", "../interactive/colors.html",
   "../interactive/bit_depth.html", "../interactive/gamma.html"],
  ["Load a photo you took. Produce grayscale, single-channel, and posterized versions.",
   "Explain in two sentences what gamma correction changed about your image."],
  [("MathData24/Notebook_1__10W-q3ZJ.ipynb", 0, 36),
   ("MathData24/Notebook_2__1dbvmhpa.ipynb", 27, 37)]),

 (8, "image-combinatorics", "Image Combinatorics & Hyperastronomical Numbers",
  "How many images are there? The answer reframes what a neural network is actually doing.",
  ["Count the binary, grayscale, and RGB images of a given size",
   "Work with numbers larger than the number of atoms in the universe",
   "Understand image space as a space you can never search by brute force",
   "Connect combinatorics to why learning is necessary"],
  ["../interactive/pixelcombo.html"],
  ["Compute the number of distinct 32x32 RGB images. Compare to the number of atoms in the observable universe.",
   "If you sampled a billion random images per second since the Big Bang, what fraction of 8x8 binary images would you have seen?"],
  [("MathData24/Notebook_2__1dbvmhpa.ipynb", 37, 171)]),

 (9, "linear-fit", "Linear Fit with Real Data",
  "You collect the data yourself. Then you fit a line to it and defend the fit.",
  ["Collect a real dataset as a class and load it from a spreadsheet",
   "Fit a line with scipy.stats.linregress and interpret every returned value",
   "Compute and read residuals",
   "Report a slope with an uncertainty, not just a number"],
  ["../interactive/matrix_multiplication_lab.html"],
  ["Collect at least 20 paired measurements of something physical. Fit a line. Report slope, r-value, and residuals.",
   "State plainly what the slope means in the units of your experiment."],
  [("Math24/Lab_6__1_Z8yjN6.ipynb", 17, 105)]),

 (10, "gradient-descent", "Gradient Descent in PyTorch",
  "The same line from Lab 9, refit by an algorithm that scales to a hundred million parameters.",
  ["Write y = mx + b as a PyTorch model with learnable parameters",
   "Define a loss and minimize it by gradient descent",
   "Watch the loss curve and diagnose a bad learning rate",
   "Confirm the learned parameters match the closed-form fit"],
  [], ["Run the same fit at three learning rates. Plot all three loss curves on one figure.",
       "Break it on purpose: find a learning rate that diverges, and explain why."],
  [("MathDataSci/MNIST_Linear__1MEC07x5.ipynb", 15, 136)]),

 (11, "mnist-linear-classifier", "MNIST & Linear Classifiers",
  "Ten thousand handwritten digits, and a classifier with no hidden layers that still gets most of them right. The search loops here are capped so the lab finishes — raise them and watch what changes.",
  ["Load MNIST and display a montage",
   "Build a linear classifier from a single matrix multiply",
   "Understand the role of the bias term",
   "Measure accuracy honestly on held-out data"],
  [], ["Train to at least 85% test accuracy and report your confusion matrix.",
       "Show three digits your model gets wrong and argue why they are hard."],
  [("MathDataSci/MNIST__19M60mQf.ipynb", 0, 147)]),

 (12, "convolution", "Convolution",
  "One operation, applied everywhere, is what separates a linear classifier from vision.",
  ["Convolve an image with a handmade kernel and predict the result first",
   "Recognize edge, blur, and sharpen kernels by their numbers",
   "Implement convolution as a block/matrix operation",
   "Apply random filters and read the feature maps"],
  ["../interactive/Conv1_a.html", "../interactive/pool.html"],
  ["Design a kernel that detects diagonal edges. Show it working on a real photo.",
   "Convolve one image with 10 random filters. Display filters and feature maps side by side."],
  [("MathDataSci_Fall23/Conv1__1kf0i0P2.ipynb", 0, 185)]),

 (13, "alexnet", "AlexNet: Filters, Feature Maps & Transfer Learning",
  "Open up a network that already works, look at what it learned, then retrain it on your own images.",
  ["Load a pretrained AlexNet and inspect its layers and shapes",
   "Visualize first-layer filters and intermediate feature maps",
   "Preprocess arbitrary images into the tensor the network expects",
   "Retrain the final layer on a dataset you assembled"],
  ["../interactive/alexnet.html"],
  ["Assemble a two-class image dataset of your own (30+ images per class) and retrain AlexNet on it.",
   "Report accuracy and show the feature maps for one correct and one incorrect prediction."],
  [("MathData24/Feature_Maps__1GayNzpg.ipynb", 0, 117)],
  # The archived retrain section is spliced from a second notebook that reuses `y`
  # for the network's output while the feature-map cells above use it for a pixel
  # coordinate, and it pulls its 50 images from a Google Slides deck that no longer
  # exists. Rebuilt here on the toast dataset that ships with the course -- which is
  # also the shape Deliverable 3 asks for.
  ALEXNET_TRANSFER),

 (14, "autoencoders-and-generative", "Autoencoders & Generative Models",
  "Run the network backwards. Compression, reconstruction, and generating images that never existed.",
  ["Build a dense autoencoder on MNIST and inspect the latent code",
   "Extend it to a convolutional autoencoder",
   "Sample the latent space to generate new digits",
   "Understand the leap from autoencoder to modern generative models"],
  [], ["Train an autoencoder with a 2-dimensional latent space and plot the latent grid.",
       "Generate 16 digits that are not in the dataset. Show them."],
  [("MathDataSci_Fall23/Autoencoder_and_GAN__1plbvxqA.ipynb", 0, 164)]),
]

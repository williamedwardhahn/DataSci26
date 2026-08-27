# Resize Image

[Colab Version](https://colab.research.google.com/drive/1EHX1OIS-b7DHXhhWoxiWsHITjmzNzBAg?usp=sharing)

```python 
import matplotlib.pyplot as plt
import numpy as np
from skimage.io import imread
from skimage.transform import resize
```

```python
url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Claude_Monet%2C_Saint-Georges_majeur_au_cr%C3%A9puscule.jpg/800px-Claude_Monet%2C_Saint-Georges_majeur_au_cr%C3%A9puscule.jpg'
im = imread(url)
plt.imshow(im);
im = resize(im,(512,512))
plt.imshow(im);
```


This Python code snippet demonstrates how to use the `matplotlib`, `numpy`, and `scikit-image` libraries to download an image from a URL, resize it, and display it using `matplotlib.pyplot`.

Here's a step-by-step explanation of the code:

1. Import the necessary libraries:
   - `import matplotlib.pyplot as plt`: This imports the `matplotlib` library under the alias `plt`, which is commonly used for creating plots and displaying images.
   - `import numpy as np`: This imports the `numpy` library under the alias `np`, which is used for numerical operations and array manipulations.
   - `from skimage.io import imread`: This imports the `imread` function from the `skimage.io` module, which is part of the scikit-image library and is used to read images.
   - `from skimage.transform import resize`: This imports the `resize` function from the `skimage.transform` module, which is used for resizing images.

2. Define a URL:
   ```python
   url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Claude_Monet%2C_Saint-Georges_majeur_au_cr%C3%A9puscule.jpg/800px-Claude_Monet%2C_Saint-Georges_majeur_au_cr%C3%A9puscule.jpg'
   ```
   This URL points to an image hosted on Wikimedia Commons.

3. Read and display the original image:
   ```python
   im = imread(url)
   plt.imshow(im)
   ```
   - `im = imread(url)`: This line reads the image from the specified URL using the `imread` function and stores it in the variable `im`.
   - `plt.imshow(im)`: This line displays the original image using `plt.imshow`. This is a quick way to visualize the image.

4. Resize and display the resized image:
   ```python
   im = resize(im, (512, 512))
   plt.imshow(im)
   ```
   - `im = resize(im, (512, 512))`: This line resizes the `im` image to have dimensions 512x512 pixels using the `resize` function. The result is stored back in the `im` variable.
   - `plt.imshow(im)`: This line displays the resized image. The second call to `plt.imshow` replaces the original image displayed with the resized one, allowing you to visualize the resized image.

In summary, this code fetches an image from a URL, displays the original image, resizes it to 512x512 pixels, and then displays the resized version of the image using `matplotlib`. This can be useful for various image processing tasks and visualizations.

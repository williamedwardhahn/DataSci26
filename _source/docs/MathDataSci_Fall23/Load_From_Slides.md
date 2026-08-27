

```shell
apt-get install poppler-utils
pip install pdf2image
```

```python
from pdf2image import convert_from_path
import requests
import matplotlib.pyplot as plt
import numpy as np
from skimage.io import imread
from skimage.transform import resize
```

```python
def plot(x):
    fig, ax = plt.subplots()
    im = ax.imshow(x, cmap = 'gray')
    ax.axis('off')
    fig.set_size_inches(5, 5)
    plt.show()

def get_google_slide(url):
    url_head = "https://docs.google.com/presentation/d/"
    url_body = url.split('/')[5]
    page_id = url.split('.')[-1]
    return url_head + url_body + "/export/pdf?id=" + url_body + "&pageid=" + page_id

def get_slides(url):
    url = get_google_slide(url)
    r = requests.get(url, allow_redirects=True)
    open('file.pdf', 'wb').write(r.content)
    images = convert_from_path('file.pdf', 500)
    return images
```


```python
Data_Deck = "https://docs.google.com/presentation/d/12NWxIiiMua9mB6Lsj09JiyxC1FHvcO2Mrhf4jkOQeYo/edit#slide=id.g1e604f0493b_0_26"
```

```python
image_list = get_slides(Data_Deck)

n = len(image_list)

for i in range(n):

    plot(image_list[i])
    print(np.array(image_list[i]).shape)
```


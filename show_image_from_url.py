from skimage import io as io
import matplotlib.pyplot as plt

def plot(x):
    fig, ax = plt.subplots()
    im = ax.imshow(x, cmap = 'gray')
    ax.axis('off')
    fig.set_size_inches(8, 8)
    plt.show()

image = io.imread("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS1zTygfOH8uRpwJhrnBqkaBBm8yPBzBSmO_yjrrxjThazouWvHFhSEAHQaLkNl9gXjsPFdyEgAyH4VKNYmVUiK57hfJmBXUiXzep7dZdVHNQ&s=10")
plot(image)


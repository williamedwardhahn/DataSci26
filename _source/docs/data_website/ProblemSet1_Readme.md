[Code Here](https://colab.research.google.com/drive/1PFowg9BEhZlhrzj4WvoNkmLvsGuuS1xR?usp=sharing)

### Importing Libraries
```python
import numpy as np
import matplotlib.pyplot as plt
import torch
from torchvision import datasets
from skimage.util import montage
!pip install wandb
import wandb as wb
from skimage.io import imread
```
- `numpy`: Numerical Python library for array manipulations
- `matplotlib.pyplot`: For plotting
- `torch`: PyTorch library for tensors and deep learning
- `torchvision.datasets`: Download and load various datasets
- `skimage.util`: Used for creating a montage of images
- `wandb`: Weights and Biases library for experiment tracking (Note: `!pip install wandb` installs it)
- `skimage.io`: For reading images

### Utility Functions

1. **GPU(data)**: Moves a tensor to the GPU and sets `requires_grad=True`
2. **GPU_data(data)**: Moves a tensor to the GPU but doesn't require gradients
3. **plot(x)**: Plots a 2D array or tensor using matplotlib
4. **montage_plot(x)**: Creates a montage of 2D arrays and then plots it

### Loading Datasets
```python
train_set = datasets.MNIST('./data', train=True, download=True)
test_set = datasets.MNIST('./data', train=False, download=True)
```
- Downloads and loads the MNIST dataset for training and testing. Other datasets like KMNIST and FashionMNIST are commented out but can be used as well.

### Preprocessing
```python
X = train_set.data.numpy()
X_test = test_set.data.numpy()
Y = train_set.targets.numpy()
Y_test = test_set.targets.numpy()

X = X[:,None,:,:]/255
X_test = X_test[:,None,:,:]/255
```
- Converts the training and testing data to numpy arrays and scales them by dividing by 255.

### Montage Plot
```python
montage_plot(X[125:150,0,:,:])
```
- Creates and shows a montage of a subset of the MNIST images.

### Reshaping Data
```python
X = X.reshape(X.shape[0],784)
X_test = X_test.reshape(X_test.shape[0],784)
```
- Reshapes the data to a 2D array where each row is a flattened image.

### GPU Transfer
```python
X = GPU_data(X)
Y = GPU_data(Y)
X_test = GPU_data(X_test)
Y_test = GPU_data(Y_test)
```
- Transfers the data to the GPU.

### Simple Model Run
- Initializes a random weight matrix `M` and performs matrix multiplication with the input `X`.
- Computes the accuracy based on the maximum value's index and updates the best weight matrix `m_best` if the accuracy improves.

### Main Loop
```python
for i in range(100000):
    ...
```
- Runs the model 100,000 times, each time perturbing the best weight matrix slightly and checking if this improves accuracy.

This code is an example of an experimental setup for training a very rudimentary "neural network" without using any optimization algorithm like SGD or any activation functions. The model is just a matrix multiplication followed by an argmax operation.

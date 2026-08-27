import os
import sys
import time
import copy
import json
import pylab
import torch
import random
import imageio
import requests
import subprocess
import torchvision
import numpy as np
import pandas as pd
import seaborn as sns
from imageio import *
import urllib.request
import torch.nn as nn
from PIL import Image
from scipy import stats
from torch import matmul
import torchvision.utils
from scipy import signal
from bisect import bisect
import torch.optim as optim
from skimage import io as io
from numpy import linalg as LA
from google.colab import drive
from torchvision import models
from skimage import io as skio
import torch.nn.functional as F
import matplotlib.pyplot as plt
from torchvision.models import *
from torchsummary import summary
from skimage.util import montage
from torch.nn.functional import *
from random import random, randint
from torchvision import transforms
from torch.autograd import Variable
from torch.optim import lr_scheduler
from skimage.transform import resize
from sklearn.decomposition import PCA
from torchvision.datasets import MNIST
from mpl_toolkits.mplot3d import Axes3D
from torch.utils.data import DataLoader
from torchvision.utils import save_image
from sklearn.metrics import roc_auc_score
from torchvision import models, transforms
from urllib.request import Request, urlopen
import torchvision.transforms as transforms
from torchvision import datasets, transforms
from sklearn.metrics import confusion_matrix
from torch.utils.data import Dataset, DataLoader
from torchvision import datasets, models, transforms
from sklearn.linear_model import LogisticRegression as LR
from mpl_toolkits.axes_grid1.axes_rgb import make_rgb_axes, RGBAxes
from torch.utils.data import DataLoader, TensorDataset, random_split
from torchvision.transforms.functional import normalize


subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flashtorch'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'barbar'])


from flashtorch.utils import apply_transforms
from flashtorch.saliency import Backprop
import itertools
from barbar import Bar
from skimage import io as io
import matplotlib.pyplot as plt
from scipy import signal
from skimage.color import rgb2hsv
import cv2
from skimage.util import montage

subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'wandb'])
import wandb as wb

import nltk
nltk.download('punkt')
from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()




def plot(x):
    if type(x) == torch.Tensor :
        x = x.cpu().detach().numpy()

    fig, ax = plt.subplots()
    im = ax.imshow(x, cmap = 'gray')
    ax.axis('off')
    fig.set_size_inches(5, 5)
    plt.show()

def montage_plot(x):
    x = np.pad(x, pad_width=((0, 0), (1, 1), (1, 1)), mode='constant', constant_values=0)
    plot(montage(x))

def GPU(data):
    return torch.tensor(data, requires_grad=True, dtype=torch.float, device=torch.device('cuda'))

def GPU_data(data):
    return torch.tensor(data, requires_grad=False, dtype=torch.float, device=torch.device('cuda'))
def one_hot(y):
    y2 = GPU_data(torch.zeros((y.shape[0],10)))
    for i in range(y.shape[0]):
        y2[i,int(y[i])] = 1
    return y2



def softmax(x):
    s1 = torch.exp(x - torch.max(x,1)[0][:,None])
    s = s1 / s1.sum(1)[:,None]
    return s



def cross_entropy(outputs, labels):            
    return -torch.sum(softmax(outputs).log()[range(outputs.size()[0]), labels.long()])/outputs.size()[0]  



def randn_trunc(s): #Truncated Normal Random Numbers
    mu = 0 
    sigma = 0.1
    R = stats.truncnorm((-2*sigma - mu) / sigma, (2*sigma - mu) / sigma, loc=mu, scale=sigma)
    return R.rvs(s)


def acc(out,y):
    with torch.no_grad():
        return (torch.sum(torch.max(out,1)[1] == y).item())/y.shape[0]




def GPU(data):
    return torch.tensor(data, requires_grad=True, dtype=torch.float, device=torch.device('cuda'))

def GPU_data(data):
    return torch.tensor(data, requires_grad=False, dtype=torch.float, device=torch.device('cuda'))



def plot(x):
    if type(x) == torch.Tensor :
        x = x.cpu().detach().numpy()

    fig, ax = plt.subplots()
    im = ax.imshow(x, cmap = 'gray')
    ax.axis('off')
    fig.set_size_inches(10, 10)
    plt.show()
    
    
def montage_plot(x):
    x = np.pad(x, pad_width=((0, 0), (1, 1), (1, 1)), mode='constant', constant_values=0)
    plot(montage(x))    


def get_batch(mode):
    b = c.b
    if mode == "train":
        r = np.random.randint(X.shape[0]-b) 
        x = X[r:r+b,:,:,:]
        y = Y[r:r+b]
    elif mode == "test":
        r = np.random.randint(X_test.shape[0]-b)
        x = X_test[r:r+b,:,:,:]
        y = Y_test[r:r+b]
    return x,y



def vizvec(x): 

    fig, ax = plt.subplots()

    min_val, max_val = 0, 15

    ax.matshow(x, cmap=plt.cm.Blues)
    
    plt.axis('off')

    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            c = x[i,j]
            ax.text(j, i, str(c), va='center', ha='center')


def gradient_step(w):

    for j in range(len(w)): 

            w[j].data = w[j].data - c.h*w[j].grad.data
            
            w[j].grad.data.zero_()


def make_plots():
    
    acc_train = acc(model(x,w),y)
    
    xt,yt = get_batch('test')

    acc_test = acc(model(xt,w),yt)

    wb.log({"acc_train": acc_train, "acc_test": acc_test})
    
    
    
    
def log_arch():
    c.f_s0 = c.f_s[0]
    c.f_s1 = c.f_s[1]
    c.f_s2 = c.f_s[2]
    c.f_s3 = c.f_s[3]
    c.f_s4 = c.f_s[4]
    c.f_s5 = c.f_s[5]

    c.f_n0 = c.f_n[0]
    c.f_n1 = c.f_n[1]
    c.f_n2 = c.f_n[2]
    c.f_n3 = c.f_n[3]
    c.f_n4 = c.f_n[4]
    c.f_n5 = c.f_n[5]
    c.f_n6 = c.f_n[6]


def to_img(x):
    x = 0.5 * (x + 1)
    x = x.clamp(0, 1)
    return x

def show_image(img):
    img = to_img(img)
    npimg = img.numpy()
    plt.imshow(np.transpose(npimg, (1, 2, 0)))

    
    
def backprop(model):
    if model == 'D':
        d_optimizer.zero_grad()
        d_loss.backward()
        d_optimizer.step()

    elif model ==  'G':
        g_optimizer.zero_grad()
        g_loss.backward()
        g_optimizer.step()
        
        
def tokenize(sentence):
    """
    split sentence into array of words/tokens
    a token can be a word or punctuation character, or number
    """
    return nltk.word_tokenize(sentence)
def stem(word):
    """
    stemming = find the root form of the word
    examples:
    words = ["organize", "organizes", "organizing"]
    words = [stem(w) for w in words]
    -> ["organ", "organ", "organ"]
    """
    return stemmer.stem(word.lower())
def bag_of_words(tokenized_sentence, words):
    """
    return bag of words array:
    1 for each known word that exists in the sentence, 0 otherwise
    example:
    sentence = ["hello", "how", "are", "you"]
    words = ["hi", "hello", "I", "you", "bye", "thank", "cool"]
    bog   = [  0 ,    1 ,    0 ,   1 ,    0 ,    0 ,      0]
    """
    # stem each word
    sentence_words = [stem(word) for word in tokenized_sentence]
    # initialize bag with 0 for each word
    bag = np.zeros(len(words), dtype=np.float32)
    for idx, w in enumerate(words):
        if w in sentence_words: 
            bag[idx] = 1

    return bag



#https://github.com/yu4u/convnet-drawer

import math
from abc import ABCMeta, abstractmethod
import os
import sys
import matplotlib.pyplot as plt

from matplotlib import animation, rc
from IPython.display import HTML

def make_ani(A):

    fig, ax = plt.subplots()
    im = ax.imshow(A[0,:,:])

    def animate(data, im):
        im.set_data(data)

    def step():
        for i in range(A.shape[0]):
            data = A[i,:,:]
            yield data

    return animation.FuncAnimation(fig, animate, step, interval=100, repeat=True, fargs=(im,))




def scale(x, out_range=(0, 1)):
    domain = np.min(x), np.max(x)
    y = (x - (domain[1] + domain[0]) / 2) / (domain[1] - domain[0])
    return y * (out_range[1] - out_range[0]) + (out_range[1] + out_range[0]) / 2



class Line:
    def __init__(self, x1, y1, x2, y2, color=(0, 0, 0), width=1, dasharray=None):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.color = color
        self.width = width
        self.dasharray = dasharray

    def get_svg_string(self):
        stroke_dasharray = self.dasharray if self.dasharray else "none"
        return '<line x1="{}" y1="{}" x2="{}" y2="{}" stroke-width="{}" stroke-dasharray="{}" stroke="rgb{}"/>\n'.format(
            self.x1, self.y1, self.x2, self.y2, self.width, stroke_dasharray, self.color)


class Text:
    def __init__(self, x, y, body, color=(0, 0, 0), size=20):
        self.x = x
        self.y = y
        self.body = body
        self.color = color
        self.size = size

    def get_svg_string(self):
        return '<text x="{}" y="{}" font-family="arial" font-size="{}px" ' \
               'text-anchor="middle" fill="rgb{}">{}</text>\n'.format(self.x, self.y, self.size, self.color, self.body)


class Model:
    def __init__(self, input_shape):
        self.layers = []

        if len(input_shape) != 3:
            raise ValueError("input_shape should be rank 3 but received  {}".format(input_shape))

        self.feature_maps = []
        self.x = None
        self.y = None
        self.width = None
        self.height = None

        self.feature_maps.append(FeatureMap3D(*input_shape))

    def add_feature_map(self, layer):
        if isinstance(self.feature_maps[-1], FeatureMap3D):
            h, w = self.feature_maps[-1].h, self.feature_maps[-1].w
            filters = layer.filters if layer.filters else self.feature_maps[-1].c

            if isinstance(layer, GlobalAveragePooling2D):
                self.feature_maps.append(FeatureMap1D(filters))
            elif isinstance(layer, Flatten):
                self.feature_maps.append(FeatureMap1D(h * w * filters))
            elif isinstance(layer, Deconv2D):
                if layer.padding == "same":
                    new_h = h * layer.strides[0]
                    new_w = w * layer.strides[1]
                else:
                    new_h = h * layer.strides[0] + max(layer.kernel_size[0] - layer.strides[0], 0)
                    new_w = w * layer.strides[1] + max(layer.kernel_size[1] - layer.strides[1], 0)
                self.feature_maps.append(FeatureMap3D(new_h, new_w, filters))
            else:
                if layer.padding == "same":
                    new_h = math.ceil(h / layer.strides[0])
                    new_w = math.ceil(w / layer.strides[1])
                else:
                    new_h = math.ceil((h - layer.kernel_size[0] + 1) / layer.strides[0])
                    new_w = math.ceil((w - layer.kernel_size[1] + 1) / layer.strides[1])
                self.feature_maps.append(FeatureMap3D(new_h, new_w, filters))
        else:
            self.feature_maps.append(FeatureMap1D(layer.filters))

    def add(self, layer):
        self.add_feature_map(layer)
        layer.prev_feature_map = self.feature_maps[-2]
        layer.next_feature_map = self.feature_maps[-1]
        self.layers.append(layer)

    def build(self):
        left = 0

        for feature_map in self.feature_maps:
            right = feature_map.set_objects(left)
            left = right + inter_layer_margin

        for i, layer in enumerate(self.layers):
            layer.set_objects()

        # get bounding box
        self.x = - bounding_box_margin - 30
        self.y = min([f.get_top() for f in self.feature_maps]) - text_margin - text_size \
            - bounding_box_margin
        self.width = self.feature_maps[-1].right + bounding_box_margin * 2 + 30 * 2
        # TODO: automatically calculate the ad-hoc offset "30" from description length
        self.height = - self.y * 2 + text_size

    def save_fig(self, filename):
        self.build()
        string = '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" ' \
                 'width= "{}" height="{}" '.format(self.width, self.height) + \
                 'viewBox="{} {} {} {}">\n'.format(self.x, self.y, self.width, self.height)

        for feature_map in self.feature_maps:
            string += feature_map.get_object_string()

        for layer in self.layers:
            string += layer.get_object_string()

        string += '</svg>'
        f = open(filename, 'w')
        f.write(string)
        f.close()


class FeatureMap:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.left = None
        self.right = None
        self.objects = None

    @abstractmethod
    def set_objects(self, left):
        pass

    def get_object_string(self):
        return get_object_string(self.objects)

    @abstractmethod
    def get_top(self):
        pass

    @abstractmethod
    def get_bottom(self):
        pass


class FeatureMap3D(FeatureMap):
    def __init__(self, h, w, c):
        self.h = h
        self.w = w
        self.c = c
        super(FeatureMap3D, self).__init__()

    def set_objects(self, left):
        self.left = left
        c_ = math.pow(self.c, channel_scale)
        self.right, self.objects = get_rectangular(self.h, self.w, c_, left, line_color_feature_map)
        x = (left + self.right) / 2
        y = self.get_top() - text_margin
        self.objects.append(Text(x, y, "{}x{}x{}".format(self.h, self.w, self.c), color=text_color_feature_map,
                                 size=text_size))

        return self.right

    def get_left_for_conv(self):
        return self.left + self.w * ratio * math.cos(theta) / 2

    def get_top(self):
        return - self.h / 2 + self.w * ratio * math.sin(theta) / 2

    def get_bottom(self):
        return self.h / 2 - self.w * ratio * math.sin(theta) / 2

    def get_right_for_conv(self):
        x = self.left + self.w * ratio * math.cos(theta) / 4
        y = - self.h / 4 + self.w * ratio * math.sin(theta) / 4

        return x, y


class FeatureMap1D(FeatureMap):
    def __init__(self, c):
        self.c = c
        super(FeatureMap1D, self).__init__()

    def set_objects(self, left):
        self.left = left
        c_ = math.pow(self.c, channel_scale)
        self.right = left + one_dim_width
        # TODO: reflect text length to right
        x1 = left
        y1 = - c_ / 2
        x2 = left + one_dim_width
        y2 = c_ / 2
        line_color = line_color_feature_map
        self.objects = []
        self.objects.append(Line(x1, y1, x1, y2, line_color))
        self.objects.append(Line(x1, y2, x2, y2, line_color))
        self.objects.append(Line(x2, y2, x2, y1, line_color))
        self.objects.append(Line(x2, y1, x1, y1, line_color))
        self.objects.append(Text(left + one_dim_width / 2, - c_ / 2 - text_margin, "{}".format(
            self.c), color=text_color_feature_map, size=text_size))

        return self.right

    def get_top(self):
        return - math.pow(self.c, channel_scale) / 2

    def get_bottom(self):
        return math.pow(self.c, channel_scale) / 2


class Layer:
    __metaclass__ = ABCMeta

    def __init__(self, filters=None, kernel_size=None, strides=(1, 1), padding="valid"):
        self.filters = filters
        self.kernel_size = kernel_size
        self.strides = strides
        self.padding = padding
        self.objects = []
        self.prev_feature_map = None
        self.next_feature_map = None
        self.description = None

    @abstractmethod
    def get_description(self):
        return None

    def set_objects(self):
        c = math.pow(self.prev_feature_map.c, channel_scale)
        left = self.prev_feature_map.get_left_for_conv()
        start1 = (left + c,
                  -self.kernel_size[0] + self.kernel_size[1] * ratio * math.sin(theta) / 2
                  + self.kernel_size[0] / 2)
        start2 = (left + c + self.kernel_size[1] * ratio * math.cos(theta),
                  -self.kernel_size[1] * ratio * math.sin(theta) / 2 + self.kernel_size[0] / 2)
        end = self.next_feature_map.get_right_for_conv()
        line_color = line_color_layer
        left, self.objects = get_rectangular(self.kernel_size[0], self.kernel_size[1], c, left, color=line_color)
        self.objects.append(Line(start1[0], start1[1], end[0], end[1], color=line_color))
        self.objects.append(Line(start2[0], start2[1], end[0], end[1], color=line_color))

        x = (self.prev_feature_map.right + self.next_feature_map.left) / 2
        y = max(self.prev_feature_map.get_bottom(), self.next_feature_map.get_bottom()) + text_margin \
            + text_size

        for i, description in enumerate(self.get_description()):
            self.objects.append(Text(x, y + i * text_size, "{}".format(description),
                                     color=text_color_layer, size=text_size))

    def get_object_string(self):
        return get_object_string(self.objects)


class Conv2D(Layer):
    def get_description(self):
        return ["conv{}x{}, {}".format(self.kernel_size[0], self.kernel_size[1], self.filters),
                "stride {}".format(self.strides)]


class Deconv2D(Layer):
    def get_description(self):
        return ["deconv{}x{}, {}".format(self.kernel_size[0], self.kernel_size[1], self.filters),
                "stride {}".format(self.strides)]


class PoolingLayer(Layer):
    def __init__(self, pool_size=(2, 2), strides=None, padding="valid"):
        if not strides:
            strides = pool_size
        super(PoolingLayer, self).__init__(kernel_size=pool_size, strides=strides, padding=padding)


class AveragePooling2D(PoolingLayer):
    def get_description(self):
        return ["avepool{}x{}".format(self.kernel_size[0], self.kernel_size[1]),
                "stride {}".format(self.strides)]


class MaxPooling2D(PoolingLayer):
    def get_description(self):
        return ["maxpool{}x{}".format(self.kernel_size[0], self.kernel_size[1]),
                "stride {}".format(self.strides)]


class GlobalAveragePooling2D(Layer):
    def __init__(self):
        super(GlobalAveragePooling2D, self).__init__()

    def get_description(self):
        return ["global avepool"]

    def set_objects(self):
        x = (self.prev_feature_map.right + self.next_feature_map.left) / 2
        y = max(self.prev_feature_map.get_bottom(), self.next_feature_map.get_bottom()) + text_margin \
            + text_size

        for i, description in enumerate(self.get_description()):
            self.objects.append(Text(x, y + i * text_size, "{}".format(description),
                                     color=text_color_layer, size=text_size))


class Flatten(Layer):
    def __init__(self):
        super(Flatten, self).__init__()

    def get_description(self):
        return ["flatten"]

    def set_objects(self):
        x = (self.prev_feature_map.right + self.next_feature_map.left) / 2
        y = max(self.prev_feature_map.get_bottom(), self.next_feature_map.get_bottom()) + text_margin \
            + text_size

        for i, description in enumerate(self.get_description()):
            self.objects.append(Text(x, y + i * text_size, "{}".format(description),
                                     color=text_color_layer, size=text_size))


class Dense(Layer):
    def __init__(self, units):
        super(Dense, self).__init__(filters=units)

    def get_description(self):
        return ["dense"]

    def set_objects(self):
        x1 = self.prev_feature_map.right
        y11 = - math.pow(self.prev_feature_map.c, channel_scale) / 2
        y12 = math.pow(self.prev_feature_map.c, channel_scale) / 2
        x2 = self.next_feature_map.left
        y2 = - math.pow(self.next_feature_map.c, channel_scale) / 4
        line_color = line_color_layer
        self.objects.append(Line(x1, y11, x2, y2, color=line_color, dasharray=2))
        self.objects.append(Line(x1, y12, x2, y2, color=line_color, dasharray=2))

        x = (self.prev_feature_map.right + self.next_feature_map.left) / 2
        y = max(self.prev_feature_map.get_bottom(), self.next_feature_map.get_bottom()) + text_margin \
            + text_size

        for i, description in enumerate(self.get_description()):
            self.objects.append(Text(x, y + i * text_size, "{}".format(description),
                                     color=text_color_layer, size=text_size))


def get_rectangular(h, w, c, dx=0, color=(0, 0, 0)):
    p = [[0, -h],
         [w * ratio * math.cos(theta), -w * ratio * math.sin(theta)],
         [c, 0]]

    dy = w * ratio * math.sin(theta) / 2 + h / 2
    right = dx + w * ratio * math.cos(theta) + c
    lines = []

    for i, [x1, y1] in enumerate(p):
        for x2, y2 in [[0, 0], p[(i + 1) % 3]]:
            for x3, y3 in [[0, 0], p[(i + 2) % 3]]:
                lines.append(Line(x2 + x3 + dx, y2 + y3 + dy, x1 + x2 + x3 + dx, y1 + y2 + y3 + dy,
                                  color=color))

    for i in [1, 6, 8]:
        lines[i].dasharray = 1

    return right, lines


def get_object_string(objects):
    return "".join([obj.get_svg_string() for obj in objects])


def save_model_to_file(model, filename):
    model.build()
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111, aspect='equal')
    ax1.axis('off')
    plt.xlim(model.x, model.x + model.width)
    plt.ylim(model.y + model.height, model.y)
    fig = plt.gcf()
    fig.set_size_inches(25, 25)

    for feature_map in model.feature_maps + model.layers:
        for obj in feature_map.objects:
            if isinstance(obj, Line):
                if obj.dasharray == 1:
                    linestyle = ":"
                elif obj.dasharray == 2:
                    linestyle = "--"
                else:
                    linestyle = "-"
                plt.plot([obj.x1, obj.x2], [obj.y1, obj.y2], color=[c / 255 for c in obj.color], lw=obj.width,
                         linestyle=linestyle)
            elif isinstance(obj, Text):
                ax1.text(obj.x, obj.y, obj.body, horizontalalignment="center", verticalalignment="bottom",
                         size=2 * obj.size / 3, color=[c / 255 for c in obj.color])

    plt.savefig(filename)

theta = - math.pi / 6
ratio = 0.5
bounding_box_margin = 15
inter_layer_margin = 10
text_margin = 3
channel_scale = 3 / 5
text_size = 14
one_dim_width = 4
line_color_feature_map = (0, 0, 0)
line_color_layer = (0, 0, 255)
text_color_feature_map = (0, 0, 0)
text_color_layer = (0, 0, 0)

# def main():
#     model = Model(input_shape=(128, 128, 3))
#     model.add(Conv2D(32, (11, 11), (2, 2), padding="same"))
#     model.add(MaxPooling2D((2, 2)))
#     model.add(Conv2D(64, (7, 7), padding="same"))
#     model.add(AveragePooling2D((2, 2)))
#     model.add(Conv2D(128, (3, 3), padding="same"))
#     model.add(MaxPooling2D((2, 2)))
#     model.add(Conv2D(256, (3, 3), padding="same"))
#     model.add(Conv2D(512, (3, 3), padding="same"))
#     model.save_fig("test.svg")


# if __name__ == '__main__':
#     main()





def drawnet(insize,f_num,f_size):

    model = Model(input_shape=(insize, insize, 1))
    model.add(Conv2D(f_num[1], (f_size[0],f_size[0])))
    model.add(Conv2D(f_num[2], (f_size[1],f_size[1])))
    model.add(Conv2D(f_num[3], (f_size[2],f_size[2])))
    model.add(Conv2D(f_num[4], (f_size[3],f_size[3])))
    model.add(Conv2D(f_num[5], (f_size[4],f_size[4])))
    model.add(Conv2D(f_num[6], (f_size[5],f_size[5])))
    save_model_to_file(model, "example.pdf")
    
    
    


    
    
    
def get_uniprot_data(kw1, kw2, numxs):
    '''Goes to the uniprot website and searches for 
       data with the keyword given. Returns the data 
       found up to limit elements.'''

    kws = [kw1, kw2]
    Protein_data = {}
            
    for i in range(2):
        kw = kws[i]
        url1 = 'http://www.uniprot.org/uniprot/?query'
        url2 = '&columns=sequence&format=tab&limit={}'.format(numxs)
        query_complete = url1 + kw + url2
        request = Request(query_complete)
        response = urlopen(request)
        data = response.read()
        data = str(data, 'utf-8')
        data = data.split('\n')
        data = data[1:-1]
        Protein_data[str(i)] = list(map(lambda x:x.lower(),data))

    x, y = Protein_data['0'], Protein_data['1']
        
    return x, y




def process_strings(c):
    '''Takes in a list of sequences 'c' and turns each one
       into a list of numbers.'''
       
    X = []
            
    for  m, seq in enumerate(c):
        x = [] 
        for letter in seq:
            x.append(max(ord(letter)-97, 0))
        
        X.append(x)
        
    return X


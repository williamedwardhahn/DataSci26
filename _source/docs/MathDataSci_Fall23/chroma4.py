import cv2
import numpy as np
import requests
from io import BytesIO

def load_image_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        image_data = np.asarray(bytearray(response.content), dtype="uint8")
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
        return image
    else:
        print(f"Failed to load image from {url}")
        return None

def smooth_chroma_key(image, selected_color, threshold, alpha):
    lower_bound = np.array(selected_color) - threshold
    upper_bound = np.array(selected_color) + threshold
    mask = cv2.inRange(image, lower_bound, upper_bound)
    mask = cv2.GaussianBlur(mask, (15, 15), 0).astype(np.float32) / 255.0
    result = np.zeros_like(image).astype(np.float32)
    image_f = image.astype(np.float32)
    result = (mask[:, :, None] * image_f) + ((1 - mask[:, :, None]) * alpha * image_f)
    result = result.astype(np.uint8)
    return result

def on_mouse_click(event, x, y, flags, param):
    global selected_color
    if event == cv2.EVENT_LBUTTONDOWN:
        selected_color = image[y, x, :].tolist()
        print(f"Selected color: {selected_color}")
        cv2.setTrackbarPos('R', 'Sliders', selected_color[2])
        cv2.setTrackbarPos('G', 'Sliders', selected_color[1])
        cv2.setTrackbarPos('B', 'Sliders', selected_color[0])
        update()

def update(*args):
    r = cv2.getTrackbarPos('R', 'Sliders')
    g = cv2.getTrackbarPos('G', 'Sliders')
    b = cv2.getTrackbarPos('B', 'Sliders')
    alpha = cv2.getTrackbarPos('Alpha', 'Sliders') / 100.0
    threshold = cv2.getTrackbarPos('Threshold', 'Sliders')
    selected_color = [b, g, r]
    result = smooth_chroma_key(image, selected_color, threshold, alpha)
    cv2.imshow('Smooth Chroma Key Result', result)

# Replace this URL with the URL of the image you want to load
image_url = 'https://static.wixstatic.com/media/c3d52c_b0f94b73e1604de0bdebec3123d8a6f9~mv2.jpg'


image = load_image_from_url(image_url)

if image is not None:
    cv2.imshow('Original Image', image)
    cv2.setMouseCallback('Original Image', on_mouse_click)
    cv2.namedWindow('Sliders')
    cv2.createTrackbar('R', 'Sliders', 0, 255, update)
    cv2.createTrackbar('G', 'Sliders', 0, 255, update)
    cv2.createTrackbar('B', 'Sliders', 0, 255, update)
    cv2.createTrackbar('Alpha', 'Sliders', 50, 100, update)
    cv2.createTrackbar('Threshold', 'Sliders', 100, 255, update)
    update()  # Initialize
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Could not load the image.")




# backend/app/ocr/preprocess.py
import cv2
import numpy as np
import math

def load_image_bytes(bytes_data):
    arr = np.frombuffer(bytes_data, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img

def to_grayscale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def clahe_equalize(gray):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    return clahe.apply(gray)

def denoise(img):
    return cv2.fastNlMeansDenoising(img, h=10)

def adaptive_threshold(img):
    return cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY,11,2)

def deskew(img):
    coords = np.column_stack(np.where(img > 0))
    if coords.size == 0:
        return img
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = img.shape[:2]
    M = cv2.getRotationMatrix2D((w/2,h/2), angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w,h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def preprocess_image_bytes(bytes_data, for_screenshot=True):
    img = load_image_bytes(bytes_data)
    gray = to_grayscale(img)
    gray = clahe_equalize(gray)
    gray = denoise(gray)
    if not for_screenshot:
        th = adaptive_threshold(gray)
        th = deskew(th)
        return th
    else:
        return gray

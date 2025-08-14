from PIL import Image
import cv2
import numpy as np

class ResizeWithReplicatePadding:
    def __init__(self, target_size):
        self.target_size = target_size

    def __call__(self, img):
        if not isinstance(img, Image.Image):
            raise TypeError("Input should be a PIL Image")

        w, h = img.size
        scale = self.target_size / max(w, h)
        new_w, new_h = int(w * scale), int(h * scale)
        img = img.resize((new_w, new_h), Image.BILINEAR)

        img_np = np.array(img)
        pad_w = self.target_size - new_w
        pad_h = self.target_size - new_h
        left = pad_w // 2
        right = pad_w - left
        top = pad_h // 2
        bottom = pad_h - top

        img_padded = cv2.copyMakeBorder(img_np, top, bottom, left, right, cv2.BORDER_REPLICATE)
        img_pil = Image.fromarray(img_padded)

        return img_pil
import cv2 as cv
import numpy as np
from skimage import color

# Gartic's 18-color palette in BGR format
gartic_colors_bgr = {
    "black":       (0, 0, 0),
    "dark_gray":   (102, 102, 102),
    "dark_blue":   (205, 80, 0),
    "white":       (255, 255, 255),
    "gray":        (170, 170, 170),
    "blue":        (255, 201, 38),
    "dark_green":  (32, 116, 1),
    "dark_red":    (0, 0, 153),
    "dark_brown":  (18, 65, 150),
    "green":       (60, 176, 17),
    "red":         (19, 0, 255),
    "orange":      (41, 120, 255),
    "brown":       (28, 112, 176),
    "dark_purple": (78, 0, 153),
    "dark_skin":   (87, 90, 203),
    "yellow":      (38, 193, 255),
    "pink":        (143, 0, 255),
    "skin":        (168, 175, 254)
}

# Reverse mapping: BGR tuple to color name
gartic_bgr_colornames = {val: key for key, val in gartic_colors_bgr.items()}


def get_closest_gartic_color_ciede2000(bgr_pixel):
    """
    Find the closest Gartic color to a given BGR pixel using CIEDE2000 color difference.

    Args:
        bgr_pixel (tuple): A single pixel in BGR format (e.g., (255, 0, 0)).

    Returns:
        tuple: (closest_color_bgr, color_name)
    """
    # Convert BGR to normalized RGB [0, 1]
    rgb_pixel = np.array(bgr_pixel[::-1], dtype=np.float32) / 255.0
    lab_pixel = color.rgb2lab(rgb_pixel[np.newaxis, np.newaxis, :])[0][0]

    # Convert all Gartic BGR colors to LAB
    bgr_list = list(gartic_colors_bgr.values())
    color_names_list = list(gartic_colors_bgr.keys())

    rgb_array = np.array([bgr[::-1] for bgr in bgr_list], dtype=np.float32) / 255.0
    lab_array = color.rgb2lab(rgb_array[np.newaxis, :, :])[0]

    # Compute CIEDE2000 distances
    distances = color.deltaE_ciede2000(lab_pixel[np.newaxis, :], lab_array)
    closest_index = np.argmin(distances)

    return bgr_list[closest_index], color_names_list[closest_index]


def to_gartic_colors(img: cv.typing.MatLike, step: int = 1) -> np.ndarray:
    """
    Convert a BGR image to use only the closest Gartic palette colors.
    Works by downsampling every `step` pixels to speed up the process.

    Args:
        img (cv.typing.MatLike): Input image in BGR format.
        step (int): Size of square patch to process at once. Larger = faster, lower quality.

    Returns:
        np.ndarray: New image where each patch is filled with the closest Gartic color.
    """
    h, w = img.shape[:2]
    out = np.zeros_like(img)

    for y in range(0, h, step):
        for x in range(0, w, step):
            pixel = tuple(img[y, x])  # Current BGR pixel
            gcolor, _ = get_closest_gartic_color_ciede2000(pixel)

            # Fill the entire step x step block with the closest color
            out[y:y+step, x:x+step] = gcolor

    return out

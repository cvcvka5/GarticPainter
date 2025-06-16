import cv2 as cv
import numpy as np
from skimage import color

# BGR tuples for Gartic colors
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

def get_closest_gartic_color_ciede2000(bgr_pixel):
    """
    Fast CIEDE2000-based color matcher for BGR pixels using scikit-image.

    Args:
        bgr_pixel (tuple): The input BGR color (0-255).
        gartic_colors_bgr (dict): Dictionary of color_name: (B, G, R) tuples.

    Returns:
        tuple: Closest color from gartic_colors_bgr in BGR format.
    """
    # Convert single BGR to RGB, then normalize to 0-1
    rgb_pixel = np.array(bgr_pixel[::-1], dtype=np.float32) / 255.0
    lab_pixel = color.rgb2lab(rgb_pixel[np.newaxis, np.newaxis, :])[0][0]

    # Convert all Gartic BGRs to RGB and normalize
    bgr_list = list(gartic_colors_bgr.values())
    rgb_array = np.array([bgr[::-1] for bgr in bgr_list], dtype=np.float32) / 255.0
    lab_array = color.rgb2lab(rgb_array[np.newaxis, :, :])[0]

    # Compute CIEDE2000 distances
    distances = color.deltaE_ciede2000(lab_pixel[np.newaxis, :], lab_array)
    closest_index = np.argmin(distances)

    return bgr_list[closest_index]

def to_gartic_colors(img: cv.typing.MatLike, step: int = 1) -> np.ndarray:
    """
    Convert each pixel of an image to the nearest Gartic color.
    Processes pixels with a stride defined by step, filling blocks for speed.

    Args:
        img (cv.typing.MatLike): Input BGR image.
        step (int): Pixel step size for downsampling.

    Returns:
        numpy.ndarray: Image converted to Gartic colors.
    """
    h, w = img.shape[:2]
    out = np.zeros_like(img)

    for y in range(0, h, step):
        for x in range(0, w, step):
            pixel = tuple(img[y, x])                  # Get pixel BGR
            gcolor = get_closest_gartic_color_ciede2000(pixel) # Find closest Gartic color

            # Fill block to speed up conversion
            out[y:y+step, x:x+step] = gcolor

    return out

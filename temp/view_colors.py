import cv2 as cv
import numpy as np


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

for color, bgr in gartic_colors_bgr.items():
    cv.imshow(color, np.full((300, 300, 3), bgr, dtype=np.uint8))
    cv.waitKey(0)
    cv.destroyAllWindows()
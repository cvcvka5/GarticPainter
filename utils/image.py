import numpy as np
import cv2 as cv

def to_opencv_img(buffer) -> cv.typing.MatLike:
    """
    Convert raw image bytes buffer to an OpenCV image (BGR).

    Args:
        buffer (bytes): Image data in bytes.

    Returns:
        cv.typing.MatLike: Decoded OpenCV image.
    """
    npimg = np.frombuffer(buffer, np.uint8)      # Convert bytes to 1D uint8 array
    img = cv.imdecode(npimg, cv.IMREAD_COLOR)   # Decode image to BGR format
    return img

def resize_img(img: cv.typing.MatLike, width, height):
    """
    Resize image to specified width and height using area interpolation.

    Args:
        img (cv.typing.MatLike): Input OpenCV image.
        width (int): Target width.
        height (int): Target height.

    Returns:
        cv.typing.MatLike: Resized image.
    """
    return cv.resize(img, (width, height), interpolation=cv.INTER_AREA)

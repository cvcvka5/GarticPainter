import numpy as np
import cv2 as cv

def to_opencv_img(buffer) -> cv.typing.MatLike:
    """
    Convert raw image bytes buffer to an OpenCV image (BGR).

    Args:
        buffer (bytes): Raw image data in bytes (e.g., from reading a file or network).

    Returns:
        cv.typing.MatLike: Decoded image in OpenCV BGR format.
    """
    # Convert bytes buffer to a 1D numpy array of type uint8
    npimg = np.frombuffer(buffer, np.uint8)
    # Decode the image data into an OpenCV BGR image matrix
    img = cv.imdecode(npimg, cv.IMREAD_COLOR)
    return img

def resize_img(img: cv.typing.MatLike, width, height):
    """
    Resize the input image to the given width and height using area interpolation.

    Args:
        img (cv.typing.MatLike): Input image in BGR format.
        width (int): Desired width in pixels.
        height (int): Desired height in pixels.

    Returns:
        cv.typing.MatLike: Resized image.
    """
    # Use cv.INTER_AREA for shrinking images (generally better quality)
    return cv.resize(img, (width, height), interpolation=cv.INTER_AREA)

def denoise_image_preserve_color(
    img: np.ndarray, 
    h: int = 10, 
    h_color: int = 10, 
    template_size: int = 7, 
    search_size: int = 21
) -> np.ndarray:
    """
    Apply fast Non-local Means Denoising to remove noise from a color image while preserving details.

    Args:
        img (np.ndarray): Noisy input image in BGR format.
        h (int): Parameter regulating filter strength for luminance (brightness). Higher h = stronger denoising.
        h_color (int): Filter strength for color components. Higher values remove more color noise but risk color loss.
        template_size (int): Size of template patch used for denoising. Must be odd number.
        search_size (int): Size of window used to search for similar blocks. Must be odd and larger than template_size.

    Returns:
        np.ndarray: Denoised BGR image.
    """
    # fastNlMeansDenoisingColored performs denoising on each channel separately preserving color fidelity
    return cv.fastNlMeansDenoisingColored(
        img,
        None,
        h,
        h_color,
        template_size,
        search_size
    )

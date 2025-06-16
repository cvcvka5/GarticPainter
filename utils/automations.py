from pynput import mouse
import mss
import numpy as np
from utils.color import gartic_colors_bgr
import pyautogui #TODO remove
import time #TODO remove

def get_border_clicks():
    """
    Listen for 4 mouse clicks and return their (x, y) positions.

    Returns:
        List[Tuple[int, int]]: List of 4 (x, y) coordinates in order clicked.
    """
    clicks = []
    max_clicks = 2

    def on_click(x, y, button, pressed):
        if pressed:
            clicks.append((x, y))  # Record click position
            if len(clicks) >= max_clicks:
                return False  # Stop listener after 4 clicks

    with mouse.Listener(on_click=on_click) as listener:
        listener.join()  # Wait until 4 clicks are captured

    return clicks[:4]  # Return first 4 clicks


def get_bbox_from_clicks(clicks):
    """
    Calculate bounding box dimensions and edges from 4 corner clicks.

    Args:
        clicks (List[Tuple[int, int]]): List of 4 (x, y) points.

    Returns:
        dict: Bounding box with width, height, left, right, top, bottom.
    """
    xs = [x for x, y in clicks]
    ys = [y for x, y in clicks]
    left, right = min(xs), max(xs)    # Horizontal bounds
    top, bottom = min(ys), max(ys)    # Vertical bounds
    width = right - left
    height = bottom - top
    return {"width": width, "height": height, "left": left, "right": right, "top": top, "bottom": bottom}


def screenshot_region_numpy(left, top, width, height):
    """
    Capture a screen region as a NumPy array in BGR format (no alpha).

    Args:
        left (int): Left coordinate of capture region.
        top (int): Top coordinate of capture region.
        width (int): Width of capture region.
        height (int): Height of capture region.

    Returns:
        numpy.ndarray: Screenshot image as (H, W, 3) BGR NumPy array.
    """
    with mss.mss() as sct:
        monitor = {"left": left, "top": top, "width": width, "height": height}
        sct_img = sct.grab(monitor)  # Capture screen region

        img_np = np.array(sct_img)   # Convert to numpy array (BGRA)

        img_bgr = img_np[:, :, :3]   # Drop alpha channel, keep BGR

        return img_bgr


def get_gartic_colors_palette(colors_bbox: dict) -> dict:
    colors_bbox = colors_bbox.copy()
    width, height, left, right, top, bottom = list(colors_bbox.values())
    color_names = list(gartic_colors_bgr.keys())
    color_xy = {}
    
    i = 0
    for y_offset in np.arange(0, height, height/6):
        for x_offset in np.arange(0, width, width/3):
            x = left+x_offset+20
            y = top+y_offset+20
            color_xy[color_names[i]] = (x, y)
            i += 1   
            
    return color_xy
            
def test_color_palette(color_xy_points: dict):
    for color_name, xy in color_xy_points.items():
        pyautogui.moveTo(*xy)
        pyautogui.leftClick()
        time.sleep(.1)
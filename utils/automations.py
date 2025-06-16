from pynput import mouse, keyboard
import mss
import numpy as np
from utils.color import gartic_colors_bgr, gartic_bgr_colornames
import pyautogui
import time
import cv2 as cv
import winsound
import win32api, win32con


def get_border_clicks():
    """
    Waits for the user to click twice on the screen and returns the positions of those clicks.

    Returns:
        List[Tuple[int, int]]: Two (x, y) coordinates of the clicked screen points.
    """
    clicks = []
    max_clicks = 2

    def on_click(x, y, button, pressed):
        if pressed:
            clicks.append((x, y))  # Save click position
            if len(clicks) >= max_clicks:
                return False  # Stop listener when two clicks are received

    # Start mouse listener
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    return clicks[:2]


def get_bbox_from_clicks(clicks):
    """
    Calculates a bounding box from two (x, y) screen coordinates.

    Args:
        clicks (List[Tuple[int, int]]): Two corners of a rectangle.

    Returns:
        dict: Bounding box with keys width, height, left, right, top, bottom.
    """
    xs = [x for x, y in clicks]
    ys = [y for x, y in clicks]
    left, right = min(xs), max(xs)
    top, bottom = min(ys), max(ys)
    width = right - left
    height = bottom - top

    return {"width": width, "height": height, "left": left, "right": right, "top": top, "bottom": bottom}


def screenshot_region_numpy(left, top, width, height):
    """
    Captures a screenshot of the specified region of the screen.

    Args:
        left (int): X coordinate of top-left corner.
        top (int): Y coordinate of top-left corner.
        width (int): Width of capture box.
        height (int): Height of capture box.

    Returns:
        numpy.ndarray: Screenshot image in BGR format.
    """
    with mss.mss() as sct:
        monitor = {"left": left, "top": top, "width": width, "height": height}
        sct_img = sct.grab(monitor)
        img_np = np.array(sct_img)  # Convert raw BGRA to NumPy
        img_bgr = img_np[:, :, :3]  # Remove alpha channel
        return img_bgr


def get_gartic_colors_palette(colors_bbox: dict) -> dict:
    """
    Returns estimated (x, y) screen coordinates for each Gartic color in a palette grid.

    Args:
        colors_bbox (dict): Bounding box of the palette grid.

    Returns:
        dict: Mapping of color name to its (x, y) screen location.
    """
    colors_bbox = colors_bbox.copy()
    width, height, left, right, top, bottom = list(colors_bbox.values())
    color_names = list(gartic_colors_bgr.keys())
    color_xy = {}

    # Iterate grid: 3 columns x 6 rows
    i = 0
    for y_offset in np.arange(0, height, height / 6):
        for x_offset in np.arange(0, width, width / 3):
            x = left + x_offset + 20
            y = top + y_offset + 20
            color_xy[color_names[i]] = (x, y)
            i += 1

    return color_xy


def test_color_palette(color_xy_points: dict):
    """
    Test clicking every color in the given palette.

    Args:
        color_xy_points (dict): Mapping of color names to screen coordinates.
    """
    for color_name, xy in color_xy_points.items():
        pyautogui.moveTo(*xy)
        pyautogui.leftClick()
        time.sleep(0.04)


def mouse_drag(start, end):
    """
    Simulates a mouse drag operation from one point to another.

    Args:
        start (tuple): (x, y) starting position.
        end (tuple): (x, y) ending position.
    """
    win32api.SetCursorPos(start)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(0.005)
    win32api.SetCursorPos(end)
    time.sleep(0.005)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


def draw_img_with_box(
    gartic_img: cv.typing.MatLike,
    palette_xys: dict,
    drawing_bbox: dict,
    step: int = 5
):
    """
    Simulates drawing the given image using rectangular brush strokes in a drawing area.

    Args:
        gartic_img (cv.Mat): Preprocessed image using Gartic color palette.
        palette_xys (dict): Mapping of color name to screen position.
        drawing_bbox (dict): Bounding box of drawing canvas on screen.
        step (int): Vertical step between drawing lines (resolution/speed tradeoff).
    """
    drawing_area_left = drawing_bbox["left"]
    drawing_area_top = drawing_bbox["top"]
    stop_drawing = False

    # Allow stopping drawing with 'q' key
    def on_press(key):
        nonlocal stop_drawing
        try:
            if key.char == 'q':
                print("Pressed 'q' — stopping drawing loop.")
                stop_drawing = True
                return False
        except AttributeError:
            pass

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    winsound.Beep(800, 50)  # Starting beep
    time.sleep(2)  # Delay to let user switch to Gartic

    height, width, _ = gartic_img.shape
    last_color_name = None
    box_expand = 3  # Slightly widen horizontal drawing

    y = 0
    while y < height:
        if stop_drawing:
            break

        x = 0
        while x < width:
            if stop_drawing:
                break

            bgr = tuple(gartic_img[y, x])
            color_name = gartic_bgr_colornames.get(bgr)

            # Skip unknown or white (background) pixels
            if color_name is None or color_name == "white":
                x += 1
                continue

            # Change pen color if necessary
            if last_color_name != color_name:
                pos = palette_xys[color_name]
                win32api.SetCursorPos((int(pos[0]), int(pos[1])))
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                time.sleep(0.003)
                last_color_name = color_name

            # Scan horizontal run of same color
            run_start = x
            while x < width and tuple(gartic_img[y, x]) == bgr:
                x += 1
            run_end = x - 1

            # Draw rectangle line over vertical span
            for dy in range(step):
                yy = y + dy
                if yy >= height:
                    break
                box_start = (drawing_area_left + run_start, drawing_area_top + yy)
                box_end = (
                    drawing_area_left + min(run_end + box_expand, width - 1),
                    drawing_area_top + min(yy + box_expand, height - 1)
                )
                mouse_drag(box_start, box_end)

        y += step

    listener.stop()
    winsound.Beep(800, 100)  # Ending beep


def draw_img_with_pen(
    gartic_img: cv.typing.MatLike,
    palette_xys: dict,
    drawing_bbox: dict,
    step: int
):
    """
    Simulates drawing the given image using single-pixel-width pen strokes.

    Args:
        gartic_img (cv.Mat): Image using limited Gartic color palette.
        palette_xys (dict): Color name to screen (x, y) palette positions.
        drawing_bbox (dict): Bounding box of drawing canvas.
        step (int): Resolution (vertical spacing) of drawing scan.
    """
    print(f"Step size: {step}")
    drawing_area_left = drawing_bbox["left"]
    drawing_area_top = drawing_bbox["top"]
    stop_drawing = False

    def on_press(key):
        nonlocal stop_drawing
        try:
            if key.char == 'q':
                print("Pressed 'q' — stopping drawing loop.")
                stop_drawing = True
                return False
        except AttributeError:
            pass

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    winsound.Beep(800, 50)
    time.sleep(2)

    height, width, _ = gartic_img.shape
    last_color_name = None

    for y in range(0, height, step):
        if stop_drawing:
            break

        x = 0
        while x < width:
            if stop_drawing:
                break

            bgr = tuple(gartic_img[y, x])
            color_name = gartic_bgr_colornames.get(bgr)

            if color_name is None:
                x += step
                continue

            # Change pen color
            if last_color_name != color_name:
                win32api.SetCursorPos((int(palette_xys[color_name][0]), int(palette_xys[color_name][1])))
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                last_color_name = color_name
                time.sleep(0.005)

            # Draw single-line stroke across same-color pixels
            run_start = x
            while x < width and tuple(gartic_img[y, x]) == bgr:
                x += step
            run_end = x - step

            start_pos = (drawing_area_left + run_start, drawing_area_top + y)
            end_pos = (drawing_area_left + run_end, drawing_area_top + y)
            mouse_drag(start_pos, end_pos)

    listener.stop()
    winsound.Beep(800, 100)

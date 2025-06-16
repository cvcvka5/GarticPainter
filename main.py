import streamlit as st
from PIL import Image
from utils.image import to_opencv_img, resize_img, denoise_image_preserve_color
from utils.color import to_gartic_colors
from utils.automations import get_border_clicks, get_bbox_from_clicks, screenshot_region_numpy, get_gartic_colors_palette
from utils.automations import test_color_palette, draw_img_with_pen, draw_img_with_box
import numpy as np
import cv2 as cv
import time
import winsound

TEMP_DIR = "temp"

# Read version from file for display
with open("version.txt", "r") as f:
    VERSION = f.read()

# Initialize session state variables if not present
st.session_state.setdefault("drawing_bbox", None)
st.session_state.setdefault("colors_bbox", None)
st.session_state.setdefault("drawing_area_img", None)
st.session_state.setdefault("colors_area_img", None)
st.session_state.setdefault("gartic_palette_xy", None)
st.session_state.setdefault("gartic_img", None)

# Title with version info
st.title(f"GarticPhone Cheat ({VERSION})")

# Function to set the drawing bounding box by capturing 2 mouse clicks
def set_drawing_bbox():
    time.sleep(2)  # Wait before starting
    winsound.Beep(800, 50)  # Signal beep before click capture
    drawing_bbox = get_border_clicks()  # Capture 2 border points
    drawing_bbox = get_bbox_from_clicks(drawing_bbox)  # Convert to bbox
    st.session_state.drawing_bbox = drawing_bbox  # Save bbox
    winsound.Beep(800, 50)  # Signal beep after capture

# Function to set the color palette area by capturing 2 corner points
def set_colors_bbox():
    time.sleep(2)
    winsound.Beep(800, 50)
    colors_bbox = get_border_clicks()
    colors_bbox = get_bbox_from_clicks(colors_bbox)
    st.session_state.colors_bbox = colors_bbox
    st.session_state.gartic_palette_xy = get_gartic_colors_palette(colors_bbox)
    winsound.Beep(800, 50)

# Test color palette by clicking on all detected palette positions
def test_color_palette_onclick():
    winsound.Beep(800, 50)
    time.sleep(2)
    test_color_palette(st.session_state.gartic_palette_xy)
    winsound.Beep(800, 50)

# Button to set drawing bounding box, disabled if already set
st.button("🎯 Set Drawing Area",
          help=("After the beep, click this button and then click on the TWO INNER corners of the drawing canvas on Gartic Phone.\n"
                "Click order: Top-left ➜ Bottom-right."),
          type="primary", on_click=set_drawing_bbox, disabled=st.session_state.drawing_bbox is not None)

# If drawing bbox is set, capture and show screenshot resized to half
if st.session_state.drawing_bbox is not None and st.session_state.drawing_area_img is None:
    drawing_image = screenshot_region_numpy(st.session_state.drawing_bbox["left"], st.session_state.drawing_bbox["top"],
                                     st.session_state.drawing_bbox["width"], st.session_state.drawing_bbox["height"])
    drawing_image = resize_img(drawing_image, drawing_image.shape[1]//2, drawing_image.shape[0]//2)
    st.session_state.drawing_area_img = drawing_image
    
if st.session_state.drawing_area_img is not None:
    st.image(st.session_state.drawing_area_img, channels="BGR", caption="🖼️ Detected Drawing Area")

col1, col2 = st.columns(2)

# Button to set colors bounding box
col1.button("🎨 Set Color Palette Area",
          help=("After the beep, click this button and then click on the TWO INNER corners of the color palette on Gartic Phone.\n"
                "Click order: Top-left ➜ Bottom-right.\n"
                "⚠️ Start from black (top-left), end at the skin tone (bottom-right)."),
          type="primary", on_click=set_colors_bbox, disabled=st.session_state.drawing_bbox is None or st.session_state.colors_bbox is not None)

# If colors bbox is set, capture and show screenshot resized to half
if st.session_state.colors_bbox is not None and st.session_state.colors_area_img is None:
    st.session_state.colors_area_img_shown = True
    colors_image = screenshot_region_numpy(st.session_state.colors_bbox["left"], st.session_state.colors_bbox["top"],
                                     st.session_state.colors_bbox["width"], st.session_state.colors_bbox["height"])
    colors_image = resize_img(colors_image, colors_image.shape[1]//2, colors_image.shape[0]//2)
    st.session_state.colors_area_img = colors_image

if st.session_state.colors_area_img is not None:
    st.image(st.session_state.colors_area_img, channels="BGR", caption="🎨 Detected Color Palette")

# Button to test if colors were detected and clickable
col2.button("🧪 Test Palette Clicks",
          help="Clicks on all detected color palette buttons to ensure the positions are correct. Keep Gartic Phone window active.",
          disabled=st.session_state.gartic_palette_xy is None, type="tertiary", on_click=test_color_palette_onclick)

# Slider for level of detail
details_el = st.slider("🧵 Image Detail Level", min_value=1, max_value=10, step=1, value=9,
                       help="Higher values preserve more detail but are slower to convert to the Gartic palette.")

# File uploader for the reference image
uploaded_img_el = st.file_uploader("📷 Upload Drawing Image", type=["jpg", "jpeg", "png"], accept_multiple_files=False,
                       help="Upload the image you want the bot to draw on the Gartic canvas.",
                       disabled=not st.session_state.drawing_bbox or not st.session_state.colors_bbox)

# Resize + convert uploaded image to Gartic palette
def process_uploaded_image():
    print("processsing")
    step = 11 - details_el.numerator  # Determine color step size based on detail level
    with st.spinner("📏 Resizing image to fit drawing area..."):
        img_data = uploaded_img_el.getbuffer()
        img = to_opencv_img(img_data)
        img = resize_img(img, st.session_state.drawing_bbox["width"], st.session_state.drawing_bbox["height"])
    with st.spinner("🎨 Converting image to Gartic color palette..."):
        gartic_img = to_gartic_colors(img, step=step)
        st.session_state.gartic_img = gartic_img

# Button to process uploaded image
if st.button("⚙️ Process Image"):
    process_uploaded_image()

# Display processed image preview
if st.session_state.gartic_img is not None:
    st.image(st.session_state.gartic_img, caption="✅ Image Converted to Gartic Colors", channels="BGR")

# Drawing mode selection: Pen vs Box
is_box_el = st.checkbox("🧱 Use Box Tool", value=False,
                        help=(
                            "Draw using boxes instead of pen. More precise pixel placements, but a bit slower. (Better for replicating exact image.)"
                            "Drawing using pen instead of boxes. More blurry pattern, a bit faster. (Better for realistic or abstract.)"  
                            ),
                        disabled=st.session_state.gartic_img is None)

# Speed control for drawing
steps_el = st.slider("⏱️ Drawing Steps (Higher = More abstract)", min_value=1, max_value=20, value=2,
                     help="Drawing step size. Keep this at 2 for most images.",
                     disabled=st.session_state.gartic_img is None)

# Start drawing
def draw_function():
    if is_box_el.numerator == 1:
        draw_img_with_box(st.session_state.gartic_img, st.session_state.gartic_palette_xy, st.session_state.drawing_bbox, step=steps_el.numerator)
    elif is_box_el.numerator == 0:
        draw_img_with_pen(st.session_state.gartic_img, st.session_state.gartic_palette_xy, st.session_state.drawing_bbox, step=steps_el.numerator)

# Draw button
btn1col, btn2col = st.columns(2)
btn1col.button("✏️ Start Drawing!",
               help="Begins drawing your processed image on the Gartic Phone canvas.\n"
                    "⚠️ Press 'Q' anytime to stop.\n"
                    "🖊️ Use the SECOND pen radius if using Pen Mode!",
               on_click=draw_function,
               type="primary", disabled=st.session_state.gartic_img is None)

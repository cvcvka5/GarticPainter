import streamlit as st
from PIL import Image
from utils.image import to_opencv_img, resize_img
from utils.color import to_gartic_colors
from utils.automations import get_border_clicks, get_bbox_from_clicks, screenshot_region_numpy, get_gartic_colors_palette, test_color_palette
import numpy as np
import cv2 as cv
import time
import winsound

TEMP_DIR = "temp"

# Read version from file for display
with open("version.txt", "r") as f:
    VERSION = f.read()

# Initialize session state variables if not present
if 'drawing_bbox' not in st.session_state:
    st.session_state.drawing_bbox = None
if 'colors_bbox' not in st.session_state:
    st.session_state.colors_bbox = None
if 'drawing_area_img' not in st.session_state:
    st.session_state.drawing_area_img = None
if 'colors_area_img' not in st.session_state:
    st.session_state.colors_area_img = None
if 'gartic_palette_xy' not in st.session_state:
    st.session_state.gartic_palette_xy = None

# Title with version info
st.title(f"GarticPhone Cheat ({VERSION})")

# Function to set the drawing bounding box by capturing 4 mouse clicks
def set_drawing_bbox():
    time.sleep(2)  # Wait before starting
    winsound.Beep(800, 50)  # Signal beep before click capture
    drawing_bbox = get_border_clicks()  # Capture clicks
    drawing_bbox = get_bbox_from_clicks(drawing_bbox)  # Compute bbox from clicks
    st.session_state.drawing_bbox = drawing_bbox  # Save bbox to session state
    winsound.Beep(800, 50)  # Signal beep after capture

# Function to set the colors bounding box similarly
def set_colors_bbox():
    time.sleep(2)
    winsound.Beep(800, 50)
    colors_bbox = get_border_clicks()
    colors_bbox = get_bbox_from_clicks(colors_bbox)
    st.session_state.colors_bbox = colors_bbox
    st.session_state.gartic_palette_xy = get_gartic_colors_palette(colors_bbox)
    print(st.session_state.gartic_palette_xy)
    winsound.Beep(800, 50)

def test_color_palette_onclick():
    winsound.Beep(800, 50)
    time.sleep(2)
    test_color_palette(st.session_state.gartic_palette_xy)
    winsound.Beep(800, 50)



# Button to set drawing bounding box, disabled if already set
st.button("Set boundary box for drawing.",
          help=("After the beep sound, click this function then go to your Gartic Phone page and click on the inner 4 points of your drawing area "
                "in this order: top-left, top-right, bottom-right, bottom-left"),
          type="primary", on_click=set_drawing_bbox, disabled=st.session_state.drawing_bbox is not None)

# If drawing bbox is set, capture and show screenshot resized to half
if st.session_state.drawing_bbox is not None and st.session_state.drawing_area_img is None:
    drawing_image = screenshot_region_numpy(st.session_state.drawing_bbox["left"], st.session_state.drawing_bbox["top"],
                                     st.session_state.drawing_bbox["width"], st.session_state.drawing_bbox["height"])
    drawing_image = resize_img(drawing_image, drawing_image.shape[1]//2, drawing_image.shape[0]//2)
    st.session_state.drawing_area_img = drawing_image
    
if st.session_state.drawing_area_img is not None:
    st.image(st.session_state.drawing_area_img, channels="BGR")

col1, col2 = st.columns(2)

# Button to set colors bounding box, enabled only if drawing bbox set and colors bbox not set yet
col1.button("Set boundary box for the colors.",
          help=("After the beep sound, click this function then go to your Gartic Phone page and click on the inner 4 points of your colors area"
                "! You must start from the closest location to the top-left color (black), and end on the closest location to the bottom-right color skin."
                "in this order: top-left, top-right, bottom-right, bottom-left"),
          type="primary", on_click=set_colors_bbox, disabled=st.session_state.drawing_bbox is None or st.session_state.colors_bbox is not None)


# If colors bbox is set, capture and show screenshot resized to half
if st.session_state.colors_bbox is not None and st.session_state.colors_area_img is None:
    st.session_state.colors_area_img_shown = True
    colors_image = screenshot_region_numpy(st.session_state.colors_bbox["left"], st.session_state.colors_bbox["top"],
                                     st.session_state.colors_bbox["width"], st.session_state.colors_bbox["height"])
    colors_image = resize_img(colors_image, colors_image.shape[1]//2, colors_image.shape[0]//2)
    st.session_state.colors_area_img = colors_image

if st.session_state.colors_area_img is not None:
    st.image(st.session_state.colors_area_img, channels="BGR")  


col2.button("Test Gartic color palette", help="Test the color palette (the bot will click on each color)",
          disabled=st.session_state.gartic_palette_xy is None, type="tertiary", on_click=test_color_palette_onclick, icon="🧪")


# Slider for detail amount, disabled unless both bounding boxes are set
details_el = st.slider("Detail amount: ", min_value=1, max_value=10, step=1, value=9,
                       on_change=lambda: process_uploaded_image if uploaded_img_el is not None else None,
                       disabled=not st.session_state.drawing_bbox or not st.session_state.colors_bbox)

# File uploader for the reference image, disabled unless both bounding boxes are set
uploaded_img_el = st.file_uploader("Your reference image:", type=["jpg", "jpeg", "png"], accept_multiple_files=False,
                       help="Your image that will be drawn to Gartic Phone.", disabled=not st.session_state.drawing_bbox or not st.session_state.colors_bbox)

# Process the uploaded image: resize and convert to Gartic colors
def process_uploaded_image():
    step = 11 - details_el.numerator  # Compute step from slider
    with st.spinner("Converting to Gartic Color..."):
        img_data = uploaded_img_el.getbuffer()  # Get raw image data
        img = to_opencv_img(img_data)  # Convert to OpenCV image
        img = resize_img(img, st.session_state.drawing_bbox["width"], st.session_state.drawing_bbox["height"])  # Resize to drawing bbox
        gartic_img = to_gartic_colors(img, step=step)  # Convert to Gartic colors
        
    gartic_colored_img = st.image(gartic_img, caption="Image converted to Gartic Colors.", channels="BGR")  # Show result

# Call processing if image uploaded
if uploaded_img_el is not None:
    process_uploaded_image()

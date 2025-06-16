# 🎨GarticPainter

**GarticPainter** is an advanced automated drawing tool designed specifically for the online multiplayer drawing game **Gartic Phone**. It captures a selected screen region, converts images to Gartic’s limited color palette, and uses simulated mouse actions to draw pixel-perfect recreations on the game canvas. The tool supports color matching with CIEDE2000 for accuracy and allows stopping the drawing anytime by pressing 'q'.

---

## Features
- Neat GUI for usage.
- Capture custom screen regions for palette and drawing area.
- Convert arbitrary images to Gartic Phone’s color palette using advanced color matching.
- Automated drawing with mouse drag simulation.
- Graceful stop during drawing with keyboard interrupt.
- Works on Windows with `win32api` and `pyautogui` for mouse control.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/GarticPainter.git
   cd GarticPainter
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

1. Run the main script with: ```streamlit run .\main.py```
2. Select the drawing area by clicking two corners of the canvas.
3. Select the palette area by clicking two corners of the palette.
4. Upload your image.
5. Watch GarticPainter paint it for you.
![Usage demo](media/usage.gif)

---

## Requirements

- Python 3.13.5 or higher
- OpenCV
- NumPy
- pyautogui
- pynput
- mss
- scikit-image
- pywin32 (for Windows mouse control)
- winsound (Windows built-in module)

---

## License

This project is licensed under the MIT License.

---

## Disclaimer

Use responsibly and respect the terms of service of Gartic Phone. This tool is for educational and personal use only.

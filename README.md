# Image to Turtle

Redraw images using Python's built-in [`turtle`](https://docs.python.org/3/library/turtle.html) graphics module.

This project contains two scripts:

| Script | Best for | Output |
|---|---|---|
| `image-to-turtle.py` | Black-and-white images such as logos and icons | Two-tone drawing built from traced contours |
| `color-image-to-turtle.py` | Full-color images such as illustrations and anime art | Posterized, vector-style drawing with a limited color palette |

## How it works

Turtle can't display an image directly, so both scripts convert the image into shapes that Turtle can draw:

**Black-and-white version**

1. Converts the image to grayscale and applies a threshold.
2. Finds every contour, including the nesting between them (shapes inside holes inside shapes).
3. Draws the contours from the outside in, alternating white and black fills by nesting depth. This is what makes holes (like the eyes of a logo) appear correctly.

**Color version**

1. Downscales the image and reduces it to a small palette using k-means color quantization.
2. Cleans up the color map with a median filter to remove noisy pixels.
3. Traces the outline of each color region (holes included) and fills it with Turtle, largest regions first so small details end up on top.

## Requirements

- Python 3.8+
- [OpenCV](https://pypi.org/project/opencv-python/) and [NumPy](https://pypi.org/project/numpy/)
- Tkinter (used by Turtle). It ships with Python on Windows and macOS. On Debian/Ubuntu/Linux Mint:

  ```bash
  sudo apt install python3-tk
  ```

## Installation

```bash
git clone https://github.com/LinarkDMC/image-to-turtle.git
cd image-to-turtle

# Optional but recommended: use a virtual environment
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Usage

Black-and-white images:

```bash
python image_to_turtle.py path/to/logo.png
```

Full-color images:

```bash
python color_image_to_turtle.py path/to/illustration.jpg
```

When the drawing is finished, click the window to close it.

## Configuration

Both scripts have a settings block at the top of the file. Edit the values there to tune the result.

### `image_to_turtle.py`

| Setting | Default | Description |
|---|---|---|
| `DRAWING_SIZE` | `600` | Size of the drawing inside the window, in pixels |
| `THRESHOLD` | `127` | Pixels brighter than this (0-255) count as white |
| `EPSILON` | `1.5` | Contour simplification. Higher means fewer points and a faster, rougher drawing |
| `ANIMATE` | `False` | Watch the drawing being made step by step (much slower) |
| `INVERT` | `False` | Swap black and white if the colors come out reversed |

### `color_image_to_turtle.py`

| Setting | Default | Description |
|---|---|---|
| `NUM_COLORS` | `14` | Palette size. More colors give more detail but take longer |
| `MAX_SIZE` | `450` | The image is downscaled so its longest side is at most this many pixels |
| `DRAWING_SIZE` | `650` | Size of the drawing inside the window, in pixels |
| `EPSILON` | `1.0` | Contour simplification. Higher means fewer points and a faster, rougher drawing |
| `MIN_AREA` | `12` | Regions smaller than this (in pixels) are ignored |
| `SMOOTHING` | `5` | Odd number. Size of the median filter that removes color noise |
| `ANIMATE` | `False` | Watch the drawing being made (very slow with many shapes) |

## Tips

- **Drawing takes too long?** Lower `MAX_SIZE` or `NUM_COLORS`, or raise `EPSILON`.
- **Missing fine details (eyes, highlights)?** Raise `NUM_COLORS` (18-24 works well) and lower `MIN_AREA`.
- **Colors look reversed in the black-and-white version?** Set `INVERT = True`.
- **Transparent PNGs** are blended over a white background automatically.

## Limitations

- The black-and-white script only handles two tones. Use the color script for anything with gradients.
- The color script produces a stylized, posterized version of the image, not an exact copy. Photographs with smooth gradients lose the most detail.
- Turtle isn't built for speed, so images with many regions can take a while to render.

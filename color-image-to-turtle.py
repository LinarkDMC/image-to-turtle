"""
color-image-to-turtle.py
Redraws a full-color image (illustrations, anime art, etc.) using Turtle.

How it works:
  1. Reduces the image to a small palette of K colors (k-means quantization).
  2. Cleans up the color map to remove noisy pixels.
  3. Traces the outline of every color region and fills it with Turtle.

Usage:
    python color_image_to_turtle.py path/to/image.jpg

Requirements:
    pip install opencv-python numpy
"""

import sys
import turtle

import cv2
import numpy as np

# ---------------- Settings ----------------
IMAGE_PATH = sys.argv[1] if len(sys.argv) > 1 else "image.jpg"
NUM_COLORS = 14      # palette size (more colors = more detail, but slower)
MAX_SIZE = 450       # the image is downscaled so its longest side is at most this many pixels
DRAWING_SIZE = 650   # size (in pixels) of the drawing inside the window
EPSILON = 1.0        # contour simplification (higher = fewer points, faster, less precise)
MIN_AREA = 12        # regions smaller than this (in pixels) are ignored
SMOOTHING = 5        # odd number: size of the median filter that removes color noise
ANIMATE = False      # True to watch it being drawn (much slower)
# ------------------------------------------


def load_image(path):
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise SystemExit(f"Could not open the image: {path}")

    # If the image has transparency, blend it over a white background
    if img.ndim == 3 and img.shape[2] == 4:
        alpha = img[:, :, 3:4] / 255.0
        img = (img[:, :, :3] * alpha + 255 * (1 - alpha)).astype(np.uint8)
    elif img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # Downscale large images so the drawing doesn't take forever
    height, width = img.shape[:2]
    factor = MAX_SIZE / max(width, height)
    if factor < 1:
        img = cv2.resize(img, (int(width * factor), int(height * factor)), interpolation=cv2.INTER_AREA)
    return img


def quantize(img, num_colors):
    """Returns (label map, palette in BGR) after k-means color quantization."""
    # Smooth the image a little first so flat areas become cleaner
    img = cv2.bilateralFilter(img, 7, 40, 40)

    data = img.reshape(-1, 3).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    _, labels, centers = cv2.kmeans(data, num_colors, None, criteria, 3, cv2.KMEANS_PP_CENTERS)

    labels = labels.reshape(img.shape[:2]).astype(np.uint8)
    if SMOOTHING > 1:
        labels = cv2.medianBlur(labels, SMOOTHING)  # removes isolated noisy pixels
    return labels, centers.astype(np.uint8)


def bgr_to_hex(color):
    b, g, r = (int(c) for c in color)
    return f"#{r:02x}{g:02x}{b:02x}"


def build_shapes(labels, palette):
    """For each color, builds a list of shapes: (outer contour, [hole contours])."""
    shapes_by_color = []
    for k in range(len(palette)):
        mask = (labels == k).astype(np.uint8) * 255
        area = int(cv2.countNonZero(mask))
        if area == 0:
            continue

        # RETR_CCOMP gives two levels: outer boundaries and the holes inside them
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        if hierarchy is None:
            continue
        hierarchy = hierarchy[0]

        holes_of = {}
        for i, h in enumerate(hierarchy):
            if h[3] != -1:  # this contour is a hole; h[3] is the index of its parent
                holes_of.setdefault(h[3], []).append(i)

        shapes = []
        for i, h in enumerate(hierarchy):
            if h[3] != -1:
                continue
            if cv2.contourArea(contours[i]) < MIN_AREA:
                continue
            outer = cv2.approxPolyDP(contours[i], EPSILON, True)
            holes = []
            for j in holes_of.get(i, []):
                if cv2.contourArea(contours[j]) >= MIN_AREA:
                    holes.append(cv2.approxPolyDP(contours[j], EPSILON, True))
            if len(outer) >= 3:
                shapes.append((outer, holes))

        shapes_by_color.append((area, bgr_to_hex(palette[k]), shapes))

    # Draw the biggest color areas first so smaller details end up on top
    shapes_by_color.sort(key=lambda item: item[0], reverse=True)
    return shapes_by_color


def main():
    img = load_image(IMAGE_PATH)
    height, width = img.shape[:2]
    scale = DRAWING_SIZE / max(width, height)

    def to_turtle(point):
        x, y = point[0]
        return (x - width / 2) * scale, (height / 2 - y) * scale  # the image's Y axis points down

    labels, palette = quantize(img, NUM_COLORS)
    shapes_by_color = build_shapes(labels, palette)

    # Window and turtle setup
    screen = turtle.Screen()
    screen.setup(DRAWING_SIZE + 80, DRAWING_SIZE + 80)
    screen.title("Image drawn with Turtle")

    t = turtle.Turtle()
    t.hideturtle()
    t.penup()
    t.speed(0)
    if not ANIMATE:
        screen.tracer(0)  # draw everything off-screen and show it at the end

    # Background: fill the whole canvas with the most common color to avoid gaps between regions
    background = shapes_by_color[0][1]
    screen.bgcolor(background)

    for _, color, shapes in shapes_by_color:
        t.color(color)
        for outer, holes in shapes:
            outer_points = [to_turtle(p) for p in outer]
            t.goto(outer_points[0])
            t.begin_fill()
            for p in outer_points[1:]:
                t.goto(p)
            t.goto(outer_points[0])

            # Holes are added to the same fill path, connected by a zero-width "bridge"
            for hole in holes:
                hole_points = [to_turtle(p) for p in hole]
                t.goto(hole_points[0])
                for p in hole_points[1:]:
                    t.goto(p)
                t.goto(hole_points[0])
                t.goto(outer_points[0])

            t.end_fill()

    if not ANIMATE:
        screen.update()

    print("Done. Close the window or click on it to exit.")
    screen.exitonclick()


if __name__ == "__main__":
    main()

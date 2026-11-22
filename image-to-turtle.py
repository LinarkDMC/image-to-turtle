"""
image-to-turtle.py
Converts a black-and-white image (such as a logo) into a drawing made with Turtle.

Usage:
    python image_to_turtle.py path/to/image.png

Requirements:
    pip install opencv-python numpy
"""

import sys
import turtle

import cv2
import numpy as np

# ---------------- Settings ----------------
IMAGE_PATH = sys.argv[1] if len(sys.argv) > 1 else "image.png"
DRAWING_SIZE = 600   # size (in pixels) of the drawing inside the window
THRESHOLD = 127      # 0-255: pixels above this value count as "white"
EPSILON = 1.5        # contour simplification (higher = fewer points, faster)
ANIMATE = False      # True to watch it being drawn step by step (much slower)
INVERT = False       # True if the colors come out reversed
# ------------------------------------------


def load_grayscale_image(path):
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise SystemExit(f"Could not open the image: {path}")

    # If the PNG has transparency, blend it over a white background
    if img.ndim == 3 and img.shape[2] == 4:
        alpha = img[:, :, 3:4] / 255.0
        rgb = img[:, :, :3] * alpha + 255 * (1 - alpha)
        img = rgb.astype(np.uint8)

    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


def compute_depths(hierarchy):
    """Depth of each contour: 0 = outer shape, 1 = hole, 2 = island inside a hole, and so on."""
    depths = []
    for i in range(len(hierarchy)):
        depth = 0
        parent = hierarchy[i][3]
        while parent != -1:
            depth += 1
            parent = hierarchy[parent][3]
        depths.append(depth)
    return depths


def main():
    gray = load_grayscale_image(IMAGE_PATH)
    height, width = gray.shape

    _, binary = cv2.threshold(gray, THRESHOLD, 255, cv2.THRESH_BINARY)

    # RETR_TREE keeps the hierarchy (contours nested inside other contours)
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None:
        raise SystemExit("No contours were found in the image.")
    hierarchy = hierarchy[0]
    depths = compute_depths(hierarchy)

    scale = DRAWING_SIZE / max(width, height)

    def to_turtle(point):
        x, y = point
        return (x - width / 2) * scale, (height / 2 - y) * scale  # the image's Y axis points down

    # Window and turtle setup
    screen = turtle.Screen()
    screen.setup(DRAWING_SIZE + 80, DRAWING_SIZE + 80)
    screen.title("Image drawn with Turtle")
    screen.bgcolor("white")

    t = turtle.Turtle()
    t.hideturtle()
    t.penup()
    t.speed(0)
    if not ANIMATE:
        screen.tracer(0)  # draw everything off-screen and show it at the end

    # Draw from the outside in, alternating white/black by depth
    order = sorted(range(len(contours)), key=lambda i: depths[i])
    for i in order:
        approx = cv2.approxPolyDP(contours[i], EPSILON, True)
        points = [to_turtle(p[0]) for p in approx]
        if len(points) < 3:
            continue

        is_white = depths[i] % 2 == 0
        if INVERT:
            is_white = not is_white
        color = "white" if is_white else "black"

        t.color(color)
        t.goto(points[0])
        t.begin_fill()
        for p in points[1:]:
            t.goto(p)
        t.goto(points[0])
        t.end_fill()

    if not ANIMATE:
        screen.update()

    print("Done. Close the window or click on it to exit.")
    screen.exitonclick()


if __name__ == "__main__":
    main()

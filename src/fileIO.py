# fileIO.py
import raylibpy as rl

# Save a raylib Image to disk as PNG
def save_canvas(image, filepath: str):
    rl.export_image(image, filepath)
    print(f"Canvas saved to: {filepath}")

# Load a raylib Image from a given PNG path
def load_canvas(filepath: str) -> rl.Image:
    image = rl.load_image(filepath)
    if image:
        print(f"Canvas loaded from: {filepath}")
    else:
        print(f"Failed to load image from: {filepath}")
    return image
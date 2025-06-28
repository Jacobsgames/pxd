import raylibpy as rl

# Save a raylib Image to disk as PNG
def save_canvas(image, filepath: str):
    rl.export_image(image, filepath)
    print(f"Canvas saved to: {filepath}")

# Load a raylib Image from a hardcoded PNG path
def load_canvas() -> rl.Image:
    path = "../img/pxtest16.png"
    image = rl.load_image(path)
    print(f"Canvas loaded from: {path}")
    return image
from PIL import Image

def load_image(filepath: str) -> Image.Image | None:
    """Load an image from the given filepath and convert it to RGBA format.
    Returns None if loading fails."""
    try:
        return Image.open(filepath).convert('RGBA')
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

def save_image(image: Image.Image, filepath: str):
    """Save the provided image to the given filepath."""
    try:
        image.save(filepath)
        print(f"Image saved to {filepath}")
    except Exception as e:
        print(f"Error saving image: {e}")
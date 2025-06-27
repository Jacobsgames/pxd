import dearpygui.dearpygui as ui
import numpy as np
from PIL import Image
from img_io import load_image, save_image
import os

# === Globals ===
canvas_image = None
CANVAS_ZOOM = 8
TITLEBAR_HEIGHT_APPROX = 28  # Approximate height of the DPG title bar

# Supported file extensions for dialogs
SUPPORTED_EXTENSIONS = [".png", ".jpg"]

# === Theme Setup ===
def setup_themes():
    """Define and bind the application themes."""
    with ui.theme(tag="pxd_dark_theme"):
        with ui.theme_component(ui.mvAll):
            ui.add_theme_color(ui.mvThemeCol_WindowBg, (0, 0, 0, 255))
            ui.add_theme_color(ui.mvThemeCol_FrameBg, (20, 20, 20, 255))
            ui.add_theme_color(ui.mvThemeCol_ChildBg, (10, 10, 10, 255))
            ui.add_theme_color(ui.mvThemeCol_TitleBg, (0, 0, 0, 255))
            ui.add_theme_color(ui.mvThemeCol_TitleBgActive, (0, 0, 0, 255))
            ui.add_theme_color(ui.mvThemeCol_TitleBgCollapsed, (0, 0, 0, 255))
            ui.add_theme_color(ui.mvThemeCol_Text, (255, 255, 255, 255))
            ui.add_theme_color(ui.mvThemeCol_Border, (255, 255, 255, 255))
            ui.add_theme_color(ui.mvThemeCol_BorderShadow, (0, 0, 0, 0))
            ui.add_theme_color(ui.mvThemeCol_Button, (50, 50, 50, 255))
            ui.add_theme_color(ui.mvThemeCol_ButtonHovered, (70, 70, 70, 255))
            ui.add_theme_color(ui.mvThemeCol_ButtonActive, (100, 100, 100, 255))
            ui.add_theme_style(ui.mvStyleVar_FrameBorderSize, 1)
            ui.add_theme_style(ui.mvStyleVar_WindowBorderSize, 1)
            ui.add_theme_style(ui.mvStyleVar_FramePadding, 4, 2)
        with ui.theme_component(ui.mvFileExtension, parent="pxd_dark_theme"):
            ui.add_theme_color(ui.mvThemeCol_Text, (255, 255, 0, 255))

    with ui.theme(tag="canvas_style"):
        with ui.theme_component(ui.mvWindowAppItem):
            # Remove window inner padding (top, left, right, bottom)
            ui.add_theme_style(ui.mvStyleVar_WindowPadding, 0, 0)

    # Bind the main dark theme globally
    ui.bind_theme("pxd_dark_theme")

# === Canvas Creation ===
def create_canvas_texture_and_widget(width, height):
    """Create or recreate the raw texture and image widget inside the canvas window."""
    if ui.does_item_exist("canvas_texture"):
        ui.delete_item("canvas_texture")
    if ui.does_item_exist("canvas_image_widget"):
        ui.delete_item("canvas_image_widget")

    # Create raw texture with transparent black pixels (float RGBA)
    ui.add_raw_texture(
        width=width,
        height=height,
        default_value=np.zeros(width * height * 4, dtype=np.float32),
        format=ui.mvFormat_Float_rgba,
        tag="canvas_texture",
        parent="canvas_texture_registry"
    )

    # Add image widget to display the texture inside the canvas window
    ui.add_image(
        texture_tag="canvas_texture",
        parent="MainCanvas",
        tag="canvas_image_widget",
        width=width,
        height=height
    )

    # Set fixed canvas window size (image height + approx title bar)
    ui.set_item_width("MainCanvas", width)
    ui.set_item_height("MainCanvas", height + 17)  # tweak 17 as needed

# === Callbacks ===
def load_image_callback(sender, app_data):
    """Load image file, resize with zoom, update canvas texture, show canvas window."""
    global canvas_image

    path = app_data.get('file_path_name')
    if path:
        img = load_image(path)
        if img:
            # Resize image with nearest neighbor (pixel art scaling)
            canvas_image = img.resize(
                (img.width * CANVAS_ZOOM, img.height * CANVAS_ZOOM),
                Image.NEAREST
            )

            create_canvas_texture_and_widget(canvas_image.width, canvas_image.height)

            # Convert PIL image to float32 buffer normalized [0,1]
            buffer = np.array(canvas_image.getdata(), dtype=np.float32) / 255.0
            ui.set_value("canvas_texture", buffer)

            ui.set_item_label("MainCanvas", os.path.basename(path))
            ui.show_item("MainCanvas")
            ui.bind_item_theme("MainCanvas", "canvas_style")

def save_image_callback(sender, app_data):
    """Save the currently loaded image to file."""
    path = app_data.get('file_path_name')
    if path and canvas_image:
        save_image(canvas_image, path)

# === Main Application Setup ===

ui.create_context()
ui.create_viewport(title="pxd - Pixel Editor", width=800, height=600)

setup_themes()

# Texture registry to hold raw textures (hidden)
with ui.texture_registry(show=False, tag="canvas_texture_registry"):
    pass

# Menu bar with File, Edit, Help menus and callbacks
with ui.viewport_menu_bar():
    with ui.menu(label="File"):
        ui.add_menu_item(label="New")
        ui.add_menu_item(label="Open...", callback=lambda: ui.show_item("open_file_dialog"))
        ui.add_menu_item(label="Save")
        ui.add_menu_item(label="Save As...", callback=lambda: ui.show_item("save_file_dialog"))
        ui.add_separator()
        ui.add_menu_item(label="Exit", callback=lambda: ui.destroy_context())
    with ui.menu(label="Edit"):
        ui.add_menu_item(label="Undo")
        ui.add_menu_item(label="Redo")
        ui.add_separator()
        ui.add_menu_item(label="Cut")
        ui.add_menu_item(label="Copy")
        ui.add_menu_item(label="Paste")
    with ui.menu(label="Help"):
        ui.add_menu_item(label="About")

# Main canvas window (hidden until image loaded)
with ui.window(tag="MainCanvas", label="Canvas", show=False,
               no_resize=False, no_collapse=False, no_scrollbar=True):
    pass

# Save file dialog
with ui.file_dialog(directory_selector=False, show=False, tag="save_file_dialog",
                    default_filename="my_pixel_art.png", callback=save_image_callback,
                    width=700, height=400):
    for ext in SUPPORTED_EXTENSIONS:
        ui.add_file_extension(ext, color=(255, 255, 0, 255) if ext == ".png" else None)

# Open file dialog
with ui.file_dialog(directory_selector=False, show=False, tag="open_file_dialog",
                    callback=load_image_callback, width=700, height=400):
    for ext in SUPPORTED_EXTENSIONS:
        ui.add_file_extension(ext, color=(255, 255, 0, 255) if ext == ".png" else None)

# Run the app
ui.setup_dearpygui()
ui.show_viewport()
ui.maximize_viewport()
ui.start_dearpygui()
ui.destroy_context()

"""
pxd - Pixel Art Editor

This script implements a minimal pixel art editor UI using DearPyGui.
It supports:
- Loading and displaying pixel art images with nearest neighbor scaling.
- Saving the current canvas image.
- A fixed-size canvas window that matches the displayed image size exactly.
- A dark-themed UI with menus for file operations and editing.

The canvas texture and image widget are recreated each time an image is loaded.
The UI is built around DearPyGui's texture registry, windows, menus, and dialogs.
"""

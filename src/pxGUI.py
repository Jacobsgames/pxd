# “A lightweight Python immediate mode GUI built on raylib.”
import raylibpy as rl
import math

# --- GLOBALS ---
px_font = None
px_theme = None

_default_font = None # Internal: Stores the initial default font
_default_theme = None # Internal: Stores the initial default theme

_initialized = False

# New: Alignment Constants
ALIGN_LEFT = 0
ALIGN_CENTER = 1
ALIGN_RIGHT = 2


# New: Global alignment state (default to left)
_alignment_h = ALIGN_LEFT

# --- THEME DEFS ---
class RectStyle:
    def __init__(self, fill, border, border_width):
        self.fill = fill
        self.border = border
        self.border_width = border_width

class TextStyle:
    def __init__(self, font, size, color, v_offset):
        self.font = font
        self.size = size
        self.color = color
        self.v_offset = v_offset

class LabelStyle:
    def __init__(self, rect: RectStyle, text: TextStyle):
        self.rect = rect
        self.text = text

class Theme:
    def __init__(self, rect: RectStyle, text: TextStyle, label: LabelStyle):
        self.rect = rect
        self.text = text
        self.label = label


# Initialize the GUI subsystem & Raylib window
def pxgui_init():
    global px_font, px_theme, _default_font, _default_theme, _initialized
    if _initialized:
        return  # Only run once

    rl.init_window(800, 600, "pxd")
    rl.set_window_state(rl.FLAG_WINDOW_RESIZABLE)
    rl.maximize_window()
    rl.set_target_fps(60)

    # px_font = rl.get_font_default()

    _default_font = rl.load_font_ex("../arbata compact.ttf", 12, None, 0)
    rl.set_texture_filter(_default_font.texture, rl.TEXTURE_FILTER_POINT) # Crucial for pixel fonts
    
    _default_theme = Theme(
        rect = RectStyle(rl.BLACK, rl.DARKGRAY, 1),                            # Rect
        text = TextStyle(_default_font, 12, rl.RAYWHITE, 0),                      # Text
        label = LabelStyle(                                                 # ↓ Label
            rect=RectStyle(rl.Color(35, 35, 35, 255), rl.DARKGRAY, 1),         # |->  Rect
            text=TextStyle(_default_font, 12, rl.WHITE, 0),                       # |->  Text
        ),
    )
    # Set the initially active font and theme to the defaults
    px_font = _default_font
    px_theme = _default_theme

    _initialized = True

# New: Function to set current horizontal alignment
def set_h_align(alignment_mode: int):
    global _alignment_h
    _alignment_h = alignment_mode 

# --- 'BLIT' PRIMITIVES ---

# Draw styled rectangle; accepts optional RectStyle
def blit_rect(x, y, w, h, style: RectStyle = None):
    style = style or px_theme.rect
    fill = style.fill
    b_clr = style.border
    bw = style.border_width
    rl.draw_rectangle(x, y, w, h, fill)                             # borders
    rl.draw_rectangle(x, y, w, bw, b_clr)                           # Top
    rl.draw_rectangle(x, y + h - bw, w, bw, b_clr)                  # Bottom
    rl.draw_rectangle(x, y + bw, bw, h - 2 * bw, b_clr)             # Left
    rl.draw_rectangle(x + w - bw, y + bw, bw, h - 2 * bw, b_clr)    # Right

# Draw styled text; accepts optional TextStyle
def blit_text(x, y, text, style: TextStyle = None):
    style = style or px_theme.text
    # draw_text_ex(font, text, position, fontSize, spacing, tint)
    rl.draw_text_ex(style.font, text, (x, y + style.v_offset), style.size, 1, style.color)

# Draw styled text with background rect; accepts optional LabelStyle
def blit_label(x: int, y: int, w: int, h: int, text: str, style: LabelStyle = None):
    global _alignment_h # Access the global alignment setting

    style = style or px_theme.label
    text_style = style.text
    blit_rect(x, y, w, h, style.rect)

    # --- Text Measurement
    # Use 1.0 spacing here if that's what blit_text uses consistently
    text_size_vec = rl.measure_text_ex(text_style.font, text, text_style.size, 1.0)
    text_width = text_size_vec.x
    text_height = text_size_vec.y

    # --- Horizontal Centering/Alignment Logic ---
    tx = x # Default to left-aligned start

    if _alignment_h == ALIGN_CENTER:
        tx = x + math.floor((w - text_width) / 2)
    elif _alignment_h == ALIGN_RIGHT:
        tx = x + w - text_width # Position from the right edge of the label rect

    # --- Vertical Centering ---
    ty = y + math.floor((h - text_height) / 2)

    blit_text(int(tx), int(ty), text, text_style)


"""
# Draw styled text with background rect; accepts optional LabelStyle
def blit_label(x: int, y: int, w: int, h: int, text: str, style: LabelStyle = None):
    style = style or _default_theme.label                                                     # Use arg style or default
    text_style = style.text                                                             # Get text style for measurement and drawing
    blit_rect(x, y, w, h, style.rect)                                                   # Draw the label's rect
    # --- Text Measurment
    text_size_vec = rl.measure_text_ex(text_style.font, text, text_style.size, 1)       # Get actual text size for centering
    text_width = text_size_vec.x                                                        # Rendered text width
    text_height = text_size_vec.y                                                       # Rendered text height (crucial for vertical centering)
    # --- Centering
    tx = x + math.floor((w - text_width) / 2)                                           # Get X pos to horizontally center text
    ty = y + math.floor((h - text_height) / 2)                                          # Get Y pos to vertically center text

    blit_text(int(tx), int(ty), text, text_style)                                       # Draw centered text

    # Debug rect around text (uncomment to visualize text bounds)
    # rl.draw_rectangle_lines(int(tx), int(ty), int(text_width), int(text_height), rl.WHITE)
"""


# --- LAYOUT ELEMENTS --- (composed mainly of 'blits)



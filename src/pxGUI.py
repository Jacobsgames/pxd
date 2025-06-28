# “A lightweight Python immediate mode GUI built on raylib.”
import raylibpy as rl
import math

# --- GLOBALS ---
px_font = None
px_theme = None
_initialized = False

# --- THEME DEFS ---
class RectStyle:
    def __init__(self, fill, border, border_width):
        self.fill = fill
        self.border = border
        self.border_width = border_width

class TextStyle:
    def __init__(self, font, size, color):
        self.font = font
        self.size = size
        self.color = color

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
    global px_font, px_theme, _initialized
    if _initialized:
        return  # Only run once

    rl.init_window(800, 600, "pxd")
    rl.set_window_state(rl.FLAG_WINDOW_RESIZABLE)
    rl.maximize_window()
    rl.set_target_fps(60)

    px_font = rl.load_font_ex("../kitchen sink.ttf", 16, None, 0)
    px_theme = Theme(
        rect = RectStyle(rl.BLACK, rl.WHITE, 1),             # Rect
        text = TextStyle(px_font, 16, rl.RAYWHITE),          # Text
        label = LabelStyle(                                  # ↓ Label
            rect=RectStyle(rl.DARKGRAY, rl.LIGHTGRAY, 2),    # |->  Rect
            text=TextStyle(px_font, 16, rl.WHITE),           # |->  Text
        ),
    )

    _initialized = True

 

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
    rl.draw_text_ex(style.font, text, (x, y), style.size, 0, style.color)

# Draw styled text with background rect; accepts optional LabelStyle
def blit_label(x: int, y: int, w: int, h: int, text: str, style: LabelStyle = None):
    style = style or px_theme.label                                                     # Use arg style or default
    text_style = style.text                                                             # Get text style for measurement and drawing
    blit_rect(x, y, w, h, style.rect)                                                   # Draw the label's rect
    # --- Text Measurment
    text_size_vec = rl.measure_text_ex(text_style.font, text, text_style.size, 0)       # Get actual text size for centering
    text_width = text_size_vec.x                                                        # Rendered text width
    text_height = text_size_vec.y                                                       # Rendered text height (crucial for vertical centering)
    # --- Centering
    tx = x + math.floor((w - text_width) / 2)                                           # Get X pos to horizontally center text
    ty = y + math.floor((h - text_height) / 2)                                          # Get Y pos to vertically center text

    blit_text(int(tx), int(ty), text, text_style)                                       # Draw centered text

    # Debug rect around text (uncomment to visualize text bounds)
    # rl.draw_rectangle_lines(int(tx), int(ty), int(text_width), int(text_height), rl.WHITE)



# --- LAYOUT ELEMENTS --- (composed mainly of 'blits)

# Very minimal button for testing
def button(x, y, w, h, text):
    mouse = rl.get_mouse_position()
    hit = (x <= mouse.x <= x + w) and (y <= mouse.y <= y + h)
    clicked = hit and rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON)
    # reuse label style for hover, rect style otherwise
    style = px_theme.label.rect if hit else px_theme.rect
    blit_rect(x, y, w, h, style)
    # text
    txt_style = px_theme.label.text if hit else px_theme.text
    tw = rl.measure_text(text, txt_style.size)
    tx = x + (w - tw) // 2
    ty = y + (h - txt_style.size) // 2
    blit_text(tx, ty, text, txt_style)
    return clicked

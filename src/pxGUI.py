# “A lightweight Python immediate mode GUI built on raylib.”
import raylibpy as rl

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

# Default global theme
default_rect = RectStyle(rl.BLACK, rl.WHITE, 1)
default_text = TextStyle(rl.get_font_default(), 16, rl.RAYWHITE)
default_label = LabelStyle(
    rect=RectStyle(rl.DARKGRAY, rl.LIGHTGRAY, 2),   # can be same or custom
    text=TextStyle(rl.get_font_default(), 16, rl.WHITE)
)

theme_pxgui = Theme(
    rect=default_rect,
    text=default_text,
    label=default_label
)

# Expose the global theme instance for easy import
px_theme = theme_pxgui


# --- PRIMITIVES ---

# Draw styled rectangle; accepts optional RectStyle
def draw_rect(x, y, w, h, style: RectStyle = None):
    style = style or px_theme.rect
    fill = style.fill
    b_clr = style.border
    bw = style.border_width
    rl.draw_rectangle(x, y, w, h, fill)
    rl.draw_rectangle(x, y, w, bw, b_clr)               # Top
    rl.draw_rectangle(x, y + h - bw, w, bw, b_clr)      # Bottom
    rl.draw_rectangle(x, y + bw, bw, h - 2 * bw, b_clr) # Left
    rl.draw_rectangle(x + w - bw, y + bw, bw, h - 2 * bw, b_clr) # Right

# Draw styled text; accepts optional TextStyle
def draw_text(x, y, text, style: TextStyle = None):
    style = style or px_theme.text
    rl.draw_text(style.font, text, x, y, style.size, style.color)

# Composite label from rect and text; accepts optional LabelStyle
def draw_label(x, y, w, h, text, style: LabelStyle = None):
    style = style or px_theme.label

    # Draw background rectangle with border
    draw_rect(x, y, w, h, style.rect)

    # Center text
    font_size = style.text.size
    text_width = rl.measure_text(text, font_size)
    text_x = x + (w - text_width) // 2
    text_y = y + (h - font_size) // 2  # Approximate vertical centering

    draw_text(text_x, text_y, text, style.text)











def button(x, y, w, h, text):
    mouse_pos = rl.get_mouse_position()
    mouse_inbounds = (x <= mouse_pos.x <= x+w) and (y <= mouse_pos.y <= y+h)
    clicked = mouse_inbounds and rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON)
    color = rl.RED if mouse_inbounds else rl.DARKGRAY
    rl.draw_rectangle(x, y, w, h, color)
    rl.draw_text(text, x + 10, y + 10, 20, rl.RAYWHITE)
    return clicked
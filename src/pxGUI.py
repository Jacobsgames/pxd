#“A lightweight Python immediate mode GUI built on raylib.”
import raylibpy as rl

# Base styled rectangle primative - Draw rect with (n)px border contained within the rect
def draw_rect(x, y, w, h, bw, fill_clr, b_clr):
    # Draw filled background
    rl.draw_rectangle(x, y, w, h, fill_clr)

    # Manually draw borders (top, bottom, left, right)
    rl.draw_rectangle(x, y, w, bw, b_clr)               # Top
    rl.draw_rectangle(x, y + h - bw, w, bw, b_clr)      # Bottom
    rl.draw_rectangle(x, y + bw, bw, h - 2 * bw, b_clr) # Left
    rl.draw_rectangle(x + w - bw, y + bw, bw, h - 2 * bw, b_clr) # Right
""" 
This manual border drawing fixes the problem of `draw_rectangle_lines_ex`
rendering borders half inside and half outside the rectangle edges,
which causes visual overflow and misalignment. By drawing four filled
rectangles for each border edge, the border stays fully inside the
original rectangle bounds, ensuring precise and consistent visuals. 
"""



def button(x, y, w, h, text):
    mouse_pos = rl.get_mouse_position()
    mouse_inbounds = (x <= mouse_pos.x <= x+w) and (y <= mouse_pos.y <= y+h)
    clicked = mouse_inbounds and rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON)
    color = rl.RED if mouse_inbounds else rl.DARKGRAY
    rl.draw_rectangle(x, y, w, h, color)
    rl.draw_text(text, x + 10, y + 10, 20, rl.RAYWHITE)
    return clicked
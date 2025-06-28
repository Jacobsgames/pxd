#“A lightweight Python immediate mode GUI built on raylib.”
import raylibpy as rl

# Base styled rectangle primative
def draw_rect(x, y, w, h, border_width, fill_color, border_color):
    # Draw the filled rectangle
    rl.draw_rectangle(x, y, w, h, fill_color)

    # Draw the border (outline) around it
    rl.draw_rectangle_lines_ex(rl.Rectangle(x, y, w, h), border_width, border_color)


def button(x, y, w, h, text):
    mouse_pos = rl.get_mouse_position()
    mouse_inbounds = (x <= mouse_pos.x <= x+w) and (y <= mouse_pos.y <= y+h)
    clicked = mouse_inbounds and rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON)
    color = rl.RED if mouse_inbounds else rl.DARKGRAY
    rl.draw_rectangle(x, y, w, h, color)
    rl.draw_text(text, x + 10, y + 10, 20, rl.RAYWHITE)
    return clicked
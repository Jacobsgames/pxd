import raylibpy as rl

rl.init_window(640, 480, b"Font Crispness Test")
rl.set_target_fps(60)

font = rl.get_font_default()
rl.set_texture_filter(font.texture, rl.TEXTURE_FILTER_POINT)

while not rl.window_should_close():
    rl.begin_drawing()
    rl.clear_background(rl.DARKGRAY)

    x = 100
    y = 100
    text = "Edit"
    size = 10
    spacing = 0

    rl.draw_rectangle_lines(x, y, rl.measure_text(text, size), size, rl.LIGHTGRAY)
    rl.draw_text_ex(font, (x, y), text, size, spacing, rl.WHITE)

    rl.end_drawing()

rl.close_window()

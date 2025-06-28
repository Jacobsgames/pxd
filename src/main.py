import raylibpy as rl
import fileIO  # Handles image saving/loading using raylib

# --- Canvas Config ---
canvas_width = 32           # Canvas pixel width
canvas_height = 32          # Canvas pixel height
canvas_scale = 16           # Scale each canvas pixel by this amount on screen

# --- Canvas State ---
canvas_image = None         # raylib image storing pixel data (CPU-side)
canvas_texture = None       # GPU texture used for drawing the image
canvas_pos_x = 128          # Canvas top-left X position on screen
canvas_pos_y = 128

# --- Interpolation State ---
prev_cell_pos = None        # Previous canvas cell (x, y) for brush interpolation

# --- FPS Counter ---
def fps_count():
    fps_text = f"FPS: {rl.get_fps()}"
    text_width = rl.measure_text(fps_text, 20)
    x_pos = rl.get_screen_width() - text_width - 10
    rl.draw_text(fps_text, x_pos, 10, 20, rl.GREEN)

# --- Initialize a blank white canvas ---
def init_canvas(width, height):
    global canvas_image, canvas_texture
    canvas_image = rl.gen_image_color(width, height, rl.RAYWHITE)
    canvas_texture = rl.load_texture_from_image(canvas_image)

# --- Convert mouse screen pixel to canvas cell coordinates ---
def screen_to_cell(pixel_x, pixel_y):
    # Adjust for canvas position and scale to get canvas grid coords
    local_x = pixel_x - canvas_pos_x
    local_y = pixel_y - canvas_pos_y
    cell_x = int(local_x // canvas_scale)
    cell_y = int(local_y // canvas_scale)
    return cell_x, cell_y

# --- Draw a black pixel at canvas cell coords ---
def draw_cell(cell_x, cell_y):
    global canvas_image, canvas_texture
    if 0 <= cell_x < canvas_width and 0 <= cell_y < canvas_height:
        rl.image_draw_pixel(canvas_image, cell_x, cell_y, rl.BLACK)  # Update CPU image
        rl.unload_texture(canvas_texture)                            # Free old texture
        canvas_texture = rl.load_texture_from_image(canvas_image)    # Reload GPU texture

# --- Interpolate line between two canvas cells ---
def trace_input_path(x0, y0, x1, y1):
    points = []
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy))
    if steps == 0:
        return [(x0, y0)]
    for i in range(steps + 1):
        x = int(x0 + dx * i / steps)
        y = int(y0 + dy * i / steps)
        points.append((x, y))
    return points

# --- Draw the canvas to screen ---
def draw_canvas(pos_x=0, pos_y=0):
    rl.draw_texture_ex(canvas_texture, rl.Vector2(pos_x, pos_y), 0, canvas_scale, rl.WHITE)

# --- Cleanup resources ---
def unload_canvas():
    rl.unload_texture(canvas_texture)


# =============================================================================
#                               Main Program
# =============================================================================

rl.init_window(800, 600, "pxd")
rl.set_window_state(rl.FLAG_WINDOW_RESIZABLE)
rl.maximize_window()
rl.set_target_fps(240)

init_canvas(canvas_width, canvas_height)

while not rl.window_should_close():
    # --- Handle drawing with interpolation ---
    if rl.is_mouse_button_down(rl.MOUSE_LEFT_BUTTON):
        mouse = rl.get_mouse_position()
        pixel_x, pixel_y = mouse.x, mouse.y   # Mouse screen pixel coords

        # Convert screen pixels to canvas cells
        curr_cell_x, curr_cell_y = screen_to_cell(pixel_x, pixel_y)

        if prev_cell_pos is not None:
            prev_cell_x, prev_cell_y = prev_cell_pos
            # Interpolate and draw all cells between previous and current position
            for cell_x, cell_y in trace_input_path(prev_cell_x, prev_cell_y, curr_cell_x, curr_cell_y):
                draw_cell(cell_x, cell_y)
        else:
            draw_cell(curr_cell_x, curr_cell_y)  # Draw current cell if no previous pos

        prev_cell_pos = (curr_cell_x, curr_cell_y)  # Store current for next frame
    else:
        prev_cell_pos = None  # Reset when mouse button is released

    # --- Save canvas to file ---
    if rl.is_key_pressed(rl.KEY_S):
        fileIO.save_canvas(canvas_image, "canvas.png")

    # --- Load canvas from file ---
    if rl.is_key_pressed(rl.KEY_W):
        loaded_image = fileIO.load_canvas()
        if loaded_image:
            rl.unload_texture(canvas_texture)
            canvas_image = loaded_image
            canvas_texture = rl.load_texture_from_image(canvas_image)
            print("Canvas loaded from disk.")

    # --- Draw Frame ---
    rl.begin_drawing()
    rl.clear_background(rl.BLACK)
    draw_canvas(canvas_pos_x, canvas_pos_y)
    fps_count()
    rl.end_drawing()

# --- Shutdown ---
unload_canvas()
rl.close_window()

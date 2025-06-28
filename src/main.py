import raylibpy as rl
import fileIO  # Handles image saving/loading using raylib
import ctypes
import easygui

# --- Canvas Config ---
canvas_width = 32           # Canvas pixel width
canvas_height = 32          # Canvas pixel height
cell_size = 16              # Initial canvas scale (zoom level)

# Zoom limits (to prevent too large or too small scaling)
MIN_SCALE = 4
MAX_SCALE = 64

# --- Canvas State ---
canvas_image = None         # CPU-side image storing pixel data
canvas_texture = None       # GPU texture for drawing canvas_image
canvas_pos_x = 128          # Canvas top-left X on screen (used for panning)
canvas_pos_y = 128          # Canvas top-left Y on screen (used for panning)

# --- Interpolation State ---
prev_cell_pos = None        # Previous canvas cell coordinate for smooth drawing

# --- Panning State ---
panning = False             # True when middle mouse dragging for panning
last_mouse_pos = None       # Last mouse position to calculate movement delta


# --- Color Helper: creates rl.Color from rgba values ---
def rgba(r, g, b, a) -> rl.Color:
    return rl.Color(r, g, b, a)


# --- Draw FPS counter in top-right corner ---
def fps_count():
    fps_text = f"FPS: {rl.get_fps()}"
    text_width = rl.measure_text(fps_text, 20)
    x_pos = rl.get_screen_width() - text_width - 10  # 10px padding from right edge
    rl.draw_text(fps_text, x_pos, 10, 20, rgba(58, 227, 43, 255))  # Bright green text


# --- Initialize blank canvas image and GPU texture ---
def init_canvas(width, height):
    global canvas_image, canvas_texture
    canvas_image = rl.gen_image_color(width, height, rl.RAYWHITE)  # White canvas
    canvas_texture = rl.load_texture_from_image(canvas_image)


# --- Convert mouse pixel coords on screen to canvas grid cell coords ---
def screen_to_cell(pixel_x, pixel_y):
    local_x = pixel_x - canvas_pos_x  # Translate relative to canvas top-left
    local_y = pixel_y - canvas_pos_y
    cell_x = int(local_x // cell_size)  # Integer division to get cell index
    cell_y = int(local_y // cell_size)
    return cell_x, cell_y


# --- Draw a black pixel at given canvas cell ---
def draw_cell(cell_x, cell_y):
    global canvas_image, canvas_texture
    # Only draw if cell is inside canvas bounds
    if 0 <= cell_x < canvas_width and 0 <= cell_y < canvas_height:
        rl.image_draw_pixel(canvas_image, cell_x, cell_y, rl.BLACK)  # Update CPU-side image
        rl.unload_texture(canvas_texture)                            # Free old texture from GPU
        canvas_texture = rl.load_texture_from_image(canvas_image)    # Reload updated texture


# --- Return list of interpolated points between two cells for smooth brush strokes ---
def trace_input_path(x0, y0, x1, y1):
    points = []
    dx, dy = x1 - x0, y1 - y0
    steps = max(abs(dx), abs(dy))  # Number of steps is largest delta dimension

    # If no movement, return single point
    if steps == 0:
        return [(x0, y0)]

    # Linearly interpolate between start and end points
    for i in range(steps + 1):
        x = int(x0 + dx * i / steps)
        y = int(y0 + dy * i / steps)
        points.append((x, y))

    return points


# --- Draw the canvas texture at given position and scale ---
def draw_canvas(pos_x=0, pos_y=0):
    # Draw texture scaled by cell_size (zoom) at position
    rl.draw_texture_ex(canvas_texture, rl.Vector2(pos_x, pos_y), 0, cell_size, rl.WHITE)


# --- Free GPU texture resource ---
def unload_canvas():
    rl.unload_texture(canvas_texture)


# --- Load image file into canvas, updating canvas size and texture ---
def load_file():
    global canvas_width, canvas_height, canvas_image, canvas_texture

    file_path = easygui.fileopenbox(filetypes=["*.png"])
    if file_path:
        loaded_image = fileIO.load_canvas(file_path)
        if loaded_image:
            rl.unload_texture(canvas_texture)
            canvas_image = loaded_image
            canvas_texture = rl.load_texture_from_image(canvas_image)

            # Update canvas size to loaded image dimensions
            canvas_width = canvas_image.width
            canvas_height = canvas_image.height

            print(f"Loaded canvas from: {file_path} (size: {canvas_width}x{canvas_height})")
        else:
            print(f"Failed to load image: {file_path}")


# --- Set Windows title bar theme to dark or light ---
def set_window_theme(theme: str):
    hwnd = ctypes.windll.user32.FindWindowW(None, "pxd")  # Use your window title here
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    value = ctypes.c_int(1 if theme.upper() == "DARK" else 0)
    dwm = ctypes.windll.dwmapi
    dwm.DwmSetWindowAttribute(
        hwnd,
        DWMWA_USE_IMMERSIVE_DARK_MODE,
        ctypes.byref(value),
        ctypes.sizeof(value)
    )


# --- Zoom canvas in or out, clamping scale within limits ---
def zoom_canvas(increase: bool):
    global cell_size
    if increase:
        cell_size = min(cell_size * 2, MAX_SCALE)  # Double zoom but max limit
    else:
        cell_size = max(cell_size // 2, MIN_SCALE)  # Half zoom but min limit


# --- Handle canvas panning state and update position ---
def canvas_panning(is_panning):
    global panning, last_mouse_pos, canvas_pos_x, canvas_pos_y

    mouse_pos = rl.get_mouse_position()

    if is_panning:
        if not panning:
            # Start panning: record initial mouse position
            panning = True
            last_mouse_pos = mouse_pos
        else:
            # Calculate how far the mouse moved since last frame
            dx = mouse_pos.x - last_mouse_pos.x
            dy = mouse_pos.y - last_mouse_pos.y

            # Move canvas position by this delta to simulate panning
            canvas_pos_x += dx
            canvas_pos_y += dy

            # Update last mouse position for next frame delta calculation
            last_mouse_pos = mouse_pos
    else:
        # Stop panning when mouse button released
        panning = False


# --- Main Program Setup ---
rl.init_window(800, 600, "pxd")
set_window_theme("DARK")
rl.set_window_state(rl.FLAG_WINDOW_RESIZABLE)
rl.maximize_window()
rl.set_target_fps(60)

init_canvas(canvas_width, canvas_height)


# --- MAIN LOOP ---
while not rl.window_should_close():
    mouse_pos = rl.get_mouse_position()

    # --- Handle panning with middle mouse button ---
    if rl.is_mouse_button_down(rl.MOUSE_MIDDLE_BUTTON):
        canvas_panning(True)
    else:
        canvas_panning(False)

    # --- Handle drawing with left mouse button ---
    if rl.is_mouse_button_down(rl.MOUSE_LEFT_BUTTON):
        pixel_x, pixel_y = mouse_pos.x, mouse_pos.y
        curr_cell_x, curr_cell_y = screen_to_cell(pixel_x, pixel_y)

        if prev_cell_pos is not None:
            prev_cell_x, prev_cell_y = prev_cell_pos
            # Draw line interpolated between previous and current cell for smooth strokes
            for cell_x, cell_y in trace_input_path(prev_cell_x, prev_cell_y, curr_cell_x, curr_cell_y):
                draw_cell(cell_x, cell_y)
        else:
            draw_cell(curr_cell_x, curr_cell_y)  # Draw first point

        prev_cell_pos = (curr_cell_x, curr_cell_y)  # Save current cell for next frame
    else:
        prev_cell_pos = None  # Reset when mouse released

    # --- Save canvas on 'S' key press ---
    if rl.is_key_pressed(rl.KEY_S):
        fileIO.save_canvas(canvas_image, "canvas.png")

    # --- Load canvas on 'L' key press ---
    if rl.is_key_pressed(rl.KEY_L):
        load_file()

    # --- Zoom in/out with mouse wheel ---
    wheel_move = rl.get_mouse_wheel_move()
    if wheel_move > 0:
        zoom_canvas(True)
    elif wheel_move < 0:
        zoom_canvas(False)






# --- LOOP END (Draw frame)  ---
    rl.begin_drawing()
    rl.clear_background(rgba(0, 0, 0, 255))  # Black background
    draw_canvas(canvas_pos_x, canvas_pos_y)  # Draw zoomed and panned canvas
    fps_count()
    rl.end_drawing()

unload_canvas()
rl.close_window()

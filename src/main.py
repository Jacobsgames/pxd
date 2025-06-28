import raylibpy as rl   # Core renderer
import fileIO           # Handles image saving/loading using raylib
import pxgui as ui      # Handles GUI using custom raylib powered framework

import ctypes           # Used to access windows to set the OS windows theme
import easygui          # Handles filedialog & other OS popups

# --- Canvas Config ---
canvas_width = 32           # Canvas pixel width
canvas_height = 32          # Canvas pixel height
cell_size = 16              # Initial canvas scale (zoom level)

# Zoom limits
MIN_SCALE = 4
MAX_SCALE = 32

# --- Canvas State ---
canvas_image = None        # CPU‐side image storing pixel data
canvas_texture = None      # GPU texture for drawing canvas_image
canvas_pos_x = 128         # Canvas top‐left X on screen
canvas_pos_y = 64          # Canvas top‐left Y on screen

# --- Interpolation State ---
prev_cell_pos = None       # Previous canvas cell for interpolation

# --- Panning State ---
panning = False            # True when middle mouse dragging
last_mouse_pos = None      # Last mouse pos for panning delta

# --- Color Helper ---
def rgba(r, g, b, a) -> rl.Color:
    return rl.Color(r, g, b, a)

def fps_count():
    fps_text = f"FPS: {rl.get_fps()}"
    tw = rl.measure_text(fps_text, 20)
    x = rl.get_screen_width() - tw - 5
    rl.draw_text(fps_text, x, 2, 20, rgba(200, 200, 200, 255))

# --- Initialize blank canvas image and texture ---
def init_canvas(w, h):
    global canvas_image, canvas_texture
    canvas_image = rl.gen_image_color(w, h, rl.RAYWHITE)
    canvas_texture = rl.load_texture_from_image(canvas_image)

# --- Screen→grid conversion ---
def screen_to_cell(mx, my):
    lx = mx - canvas_pos_x
    ly = my - canvas_pos_y
    return int(lx // cell_size), int(ly // cell_size)

# --- Paint one cell & refresh texture ---
def draw_cell(cx, cy):
    global canvas_image, canvas_texture
    if 0 <= cx < canvas_width and 0 <= cy < canvas_height:
        rl.image_draw_pixel(canvas_image, cx, cy, rl.BLACK)
        rl.unload_texture(canvas_texture)
        canvas_texture = rl.load_texture_from_image(canvas_image)

# --- Bresenham‐style interpolation between two cells ---
def trace_input_path(x0, y0, x1, y1):
    pts = []
    dx, dy = x1 - x0, y1 - y0
    steps = max(abs(dx), abs(dy))
    if steps == 0:
        return [(x0, y0)]
    for i in range(steps + 1):
        x = int(x0 + dx * i / steps)
        y = int(y0 + dy * i / steps)
        pts.append((x, y))
    return pts

# --- Draw the canvas texture ---
def draw_canvas(x=0, y=0):
    rl.draw_texture_ex(canvas_texture, rl.Vector2(x, y), 0, cell_size, rl.WHITE)

def unload_canvas():
    rl.unload_texture(canvas_texture)

# --- Load via fileIO, update canvas size & texture ---
def load_file():
    global canvas_width, canvas_height, canvas_image, canvas_texture
    path = easygui.fileopenbox(filetypes=["*.png"])
    if path:
        img = fileIO.load_canvas(path)
        if img:
            rl.unload_texture(canvas_texture)
            canvas_image = img
            canvas_texture = rl.load_texture_from_image(canvas_image)
            canvas_width, canvas_height = canvas_image.width, canvas_image.height
            print(f"Loaded canvas from: {path} ({canvas_width}×{canvas_height})")
        else:
            print(f"Failed to load image: {path}")

# --- Windows dark titlebar helper ---
def set_window_theme(theme: str):
    hwnd = ctypes.windll.user32.FindWindowW(None, "pxd")
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    val = ctypes.c_int(1 if theme.upper() == "DARK" else 0)
    ctypes.windll.dwmapi.DwmSetWindowAttribute(
        hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
        ctypes.byref(val), ctypes.sizeof(val)
    )

# --- Zoom canvas in/out ---
def zoom_canvas(inc: bool):
    global cell_size
    if inc:
        cell_size = min(cell_size * 2, MAX_SCALE)
    else:
        cell_size = max(cell_size // 2, MIN_SCALE)

# --- Panning helper ---
def canvas_panning(active: bool):
    global panning, last_mouse_pos, canvas_pos_x, canvas_pos_y
    mp = rl.get_mouse_position()
    if active:
        if not panning:
            panning = True
            last_mouse_pos = mp
        else:
            dx = mp.x - last_mouse_pos.x
            dy = mp.y - last_mouse_pos.y
            canvas_pos_x += dx
            canvas_pos_y += dy
            last_mouse_pos = mp
    else:
        panning = False



# init our GUI library (loads theme & font into pxgui.px_theme)
ui.pxgui_init()

init_canvas(canvas_width, canvas_height)

# --- Main Loop ---
while not rl.window_should_close():
    mp = rl.get_mouse_position()

    # panning
    canvas_panning(rl.is_mouse_button_down(rl.MOUSE_MIDDLE_BUTTON))

    # drawing
    if rl.is_mouse_button_down(rl.MOUSE_LEFT_BUTTON):
        cx, cy = screen_to_cell(mp.x, mp.y)
        if prev_cell_pos is not None:
            px, py = prev_cell_pos
            for x, y in trace_input_path(px, py, cx, cy):
                draw_cell(x, y)
        else:
            draw_cell(cx, cy)
        prev_cell_pos = (cx, cy)
    else:
        prev_cell_pos = None

    # save/load
    if rl.is_key_pressed(rl.KEY_S):
        fileIO.save_canvas(canvas_image, "canvas.png")
    if rl.is_key_pressed(rl.KEY_L):
        load_file()

    # zoom
    wm = rl.get_mouse_wheel_move()
    if wm > 0:   zoom_canvas(True)
    elif wm < 0: zoom_canvas(False)

    # render
    rl.begin_drawing()
    rl.clear_background(rgba(20, 20, 20, 255))
    draw_canvas(canvas_pos_x, canvas_pos_y)
    ui.blit_rect(-1, -2, 1932, 24)            # placeholder top bar
    ui.blit_text(4, 2, "pxd")                 # placeholder title
    ui.blit_rect(-1, 64, 128, 512)            # placeholder side
    ui.blit_label(512, 24, 64, 24, "Edit")            # placeholder label



    
    fps_count()
    rl.end_drawing()

unload_canvas()
rl.close_window()

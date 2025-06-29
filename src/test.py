import raylibpy as rl
import math
import os # For robust font path handling

# --- Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WINDOW_TITLE = "Monogram Font Pixel Test"
TARGET_FPS = 60

# Define the path to your monogram.ttf file
# Adjust this path if your font file is in a different location relative to this script.
# Example: If monogram.ttf is in the same directory as this script, use "monogram.ttf"
# If it's in a 'fonts' folder next to the script, use "fonts/monogram.ttf"
# A robust way is to use os.path.join and os.path.dirname
current_script_dir = os.path.dirname(__file__)
FONT_PATH = os.path.join(current_script_dir, "../AdapaMono.ttf") # Assumes it's one level up

# Define the list of font sizes to test
# Common pixel font sizes: 6, 8, 10, 12, 16, 20, 24, 32
# Start with sizes known to be common pixel art font bases.
TEST_FONT_SIZES = [6, 8, 10, 13, 26, 52, 104, 20, 24, 32]
# Test a wider range if needed, or specific multiples of 6 or 12.

# --- Global Font Storage ---
# This list will hold (rl.Font object, original_load_size) tuples
loaded_test_fonts = []

# --- Main Program ---
def run_font_test():
    # Initialize Raylib window
    rl.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE)
    rl.set_window_state(rl.FLAG_WINDOW_RESIZABLE)
    rl.set_target_fps(TARGET_FPS)

    # Load each test font instance
    for size in TEST_FONT_SIZES:
        try:
            # Load the font at the current test size
            font_instance = rl.load_font_ex(FONT_PATH, size, None, 0)
            # Crucial: Immediately set texture filtering to POINT for pixel fonts
            rl.set_texture_filter(font_instance.texture, rl.TEXTURE_FILTER_POINT)
            loaded_test_fonts.append((font_instance, size))
            print(f"Successfully loaded monogram.ttf at size: {size}px")
        except Exception as e:
            print(f"ERROR: Could not load monogram.ttf at size {size}px. Ensure path is correct and font exists. Error: {e}")

    # --- Main Loop ---
    while not rl.window_should_close():
        # Begin drawing phase
        rl.begin_drawing()
        rl.clear_background(rl.BLACK) # Clear screen to black for good contrast

        current_draw_y = 10 # Starting Y position for the first font line

        # Iterate through all loaded font instances and draw test text
        for font_instance, load_size in loaded_test_fonts:
            display_text = f"Monogram @ Load {load_size}px: ABCDEFGHIJ abcdefghij 0123456789!@#$%^&*()_+"

            # Measure the text using the loaded font and its load_size
            # This is critical for accurate centering/positioning
            text_measured_size = rl.measure_text_ex(font_instance, display_text, float(load_size), 0.0) # Spacing 0.0 for raw test

            # Draw the text at integer coordinates to avoid sub-pixel artifacts
            # We use the load_size for drawing to see its native appearance
            rl.draw_text_ex(
                font_instance,
                display_text,
                rl.Vector2(10, float(current_draw_y)), # Start at X=10, current Y
                float(load_size), # Draw at the same size it was loaded
                0.0,              # Initial spacing for test. Adjust later in pxgui.
                rl.WHITE          # White color for visibility
            )

            # Draw a red rectangle around the measured bounds of the text
            # This helps visualize the actual space the text occupies
            rl.draw_rectangle_lines(
                10, # Same X as text
                current_draw_y,
                int(text_measured_size.x),
                int(text_measured_size.y),
                rl.RED
            )
            # Display the size of the drawn text for easy identification
            rl.draw_text(f"{load_size}px", SCREEN_WIDTH - 60, current_draw_y, 10, rl.GRAY)


            # Advance Y for the next line of text
            # Use the measured height for proper spacing between lines + some padding
            current_draw_y += int(text_measured_size.y) + 5 # 5 pixels additional padding

            # If we're getting close to the bottom, break or adjust
            if current_draw_y > SCREEN_HEIGHT - 30:
                # Optionally, restart at a new column or just stop to avoid overflow
                # For this test, simply break if we run out of screen space
                break


        # Display FPS in the corner
        fps_text = f"FPS: {rl.get_fps()}"
        rl.draw_text(fps_text, SCREEN_WIDTH - rl.measure_text(fps_text, 20) - 5, 2, 20, rl.RAYWHITE)


        # End drawing phase
        rl.end_drawing()

    # --- Cleanup ---
    # Unload all loaded test fonts
    for font_instance, _ in loaded_test_fonts:
        if rl.is_font_ready(font_instance):
            rl.unload_font(font_instance)
    rl.close_window() # Close the Raylib window

# Run the test when the script is executed
if __name__ == "__main__":
    run_font_test()

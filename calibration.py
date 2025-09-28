import time
import serial
import threading
import keyboard  # install with `pip install keyboard`

from calibration import send_gcode, map_cell, PORT, BAUDRATE, PRESS_Z, DELAY, calibrate
from solver import load_trie, find_words
from ocr import extract_board_letters

# ------------- CONFIG -------------
TRIE_PATH = "./trie.pkl"
OCR_IMAGE_PATH = "image1.jpg"  # Replace with actual screenshot logic later
CENTER_TAP_X = 20.8            # Placeholder: center of the screen
CENTER_TAP_Y = 20.8
TIME_LIMIT = 60                # Seconds

# --------- Screenshot Stub ---------
def capture_screen():
    print("📷 (Simulated) Screenshot captured.")
    # Replace with screenshot logic (e.g., via ADB or a webcam snapshot)
    return OCR_IMAGE_PATH

# ------------- Play a word -------------
def play_word(ser, path):
    if not path:
        return
    x, y = map_cell(*path[0])
    send_gcode(ser, f"G1 X{x:.2f} Y{y:.2f} F3000")
    send_gcode(ser, f"G1 Z{-PRESS_Z} F1000")

    for row, col in path[1:]:
        x, y = map_cell(row, col)
        send_gcode(ser, f"G1 X{x:.2f} Y{y:.2f} F3000")

    send_gcode(ser, "G1 Z0 F1000")  # Lift

# ------------- Main game loop -------------
def run_game(ser, trie):
    print("🕹️ Starting game...")

    # Tap center to begin game
    send_gcode(ser, f"G1 X{CENTER_TAP_X:.2f} Y{CENTER_TAP_Y:.2f} F3000")
    send_gcode(ser, f"G1 Z{-PRESS_Z} F1000")  # Press
    send_gcode(ser, "G1 Z0 F1000")            # Lift

    # Capture screen
    image_path = capture_screen()

    # OCR to get board
    board = extract_board_letters(image_path)
    print("📖 OCR Board:")
    for row in board:
        print(" ".join(row))

    # Solve board
    start = time.perf_counter()
    results = find_words(board, trie)
    end = time.perf_counter()
    print(f"✅ Found {len(results)} words in {end - start:.2f} seconds")

    # Play words until timer runs out
    game_start = time.time()
    for entry in results:
        if time.time() - game_start > TIME_LIMIT:
            print("⏰ Time's up!")
            break
        word = entry["word"]
        path = entry["path"]
        print(f"👉 Playing: {word}")
        play_word(ser, path)

    print("🔁 Returning to idle state.\n")

# ------------- Main program loop -------------
def main():
    # Load trie once
    trie = load_trie(TRIE_PATH)

    # Serial connection
    print("Connecting to printer...")
    with serial.Serial(PORT, BAUDRATE, timeout=2) as ser:
        time.sleep(2)
        ser.reset_input_buffer()

        # Calibrate on startup
        calibrate(ser)

        print("✅ Calibration complete.")
        print("Press [SPACE] to start a game. Press [Ctrl+C] to quit.")

        # Wait for spacebar
        try:
            while True:
                if keyboard.is_pressed("space"):
                    run_game(ser, trie)
                    # Wait for spacebar to be released to avoid multiple triggers
                    while keyboard.is_pressed("space"):
                        time.sleep(0.1)
                else:
                    time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n👋 Exiting...")

if __name__ == "__main__":
    main()

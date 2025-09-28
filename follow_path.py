import serial
import time
from typing import Tuple, List

# --------------------------
# CONFIGURATION
# --------------------------
PORT = "COM8"               # Change this to your actual port
BAUDRATE = 115200
CELL_SIZE = 13.6 # 12.15           # mm
PRESS_Z = 0                 # How far down to press relative to REST_Z
REST_Z = 3                  # Resting Z height above phone, treated as Z=0 after G92
DELAY = 0.3                 # seconds between acti  ons 

# --------------------------
# G-code helpers
# --------------------------
def send_gcode(ser, command: str, wait: float = DELAY):
    print(f"> {command}")
    ser.write((command + "\n").encode())
    time.sleep(wait)
    while ser.in_waiting:
        line = ser.readline().decode().strip()
        print(f"< {line}")

def play_path(ser, path: List[Tuple[int, int]]):
    """
    Takes a list of (row, col) coordinates from the solver (top-left origin),
    converts them to printer coordinates (bottom-left origin),
    moves to the first point, presses down,
    then traces the entire path,
    and lifts up at the end.
    """
    if not path:
        print(">> Empty path, nothing to play.")
        return

    send_gcode(ser, f"G1 Z{REST_Z} F1000")

    max_row = 3  # For a 4x4 grid, rows 0 to 3
    print(f">> Playing path with {len(path)} points...")

    # Move to the first point at rest height
    first_row, first_col = path[0]
    x0 = first_col * CELL_SIZE
    y0 = (max_row - first_row) * CELL_SIZE
    send_gcode(ser, f"G1 X{x0:.2f} Y{y0:.2f} F3000")

    # Press down once
    send_gcode(ser, f"G1 Z{PRESS_Z} F1000")

    # Trace the rest of the points while pressed down
    for row, col in path[1:]:
        x = col * CELL_SIZE
        y = (max_row - row) * CELL_SIZE
        send_gcode(ser, f"G1 X{x:.2f} Y{y:.2f} F3000")

    # Lift up at the end
    send_gcode(ser, f"G1 Z{REST_Z} F1000")

    print("✅ Path playback complete.")

# --------------------------
# Main logic
# --------------------------
def main():
    with serial.Serial(PORT, BAUDRATE, timeout=2) as ser:
        time.sleep(2)  # Wait for printer to initialize

        solver_results = [{'word': 'reinstator', 'path': [(0, 1), (1, 0), (2, 1), (3, 2), (2, 3), (1, 2), (1, 1), (2, 0), (3, 0), (3, 1)]}, {'word': 'castrator', 'path': [(2, 2), (3, 3), (2, 3), (1, 2), (0, 1), (1, 1), (2, 0), (3, 0), (3, 1)]}, {'word': 'veratrins', 'path': [(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (3, 1), (2, 1), (3, 2), (2, 3)]}, {'word': 'castrate', 'path': [(2, 2), (3, 3), (2, 3), (1, 2), (0, 1), (1, 1), (2, 0), (1, 0)]}, {'word': 'castrati', 'path': [(2, 2), (3, 3), (2, 3), (1, 2), (0, 1), (1, 1), (2, 0), (2, 1)]}, {'word': 'castrato', 'path': [(2, 2), (3, 3), (2, 3), (1, 2), (0, 1), (1, 1), (2, 0), (3, 0)]}, {'word': 'nitrator', 'path': [(3, 2), (2, 1), (1, 2), (0, 1), (1, 1), (2, 0), (3, 0), (3, 1)]}, {'word': 'sanitate', 'path': [(2, 3), (3, 3), (3, 2), (2, 1), (1, 2), (1, 1), (2, 0), (1, 0)]}, {'word': 'scawtite', 'path': [(2, 3), (2, 2), (1, 1), (0, 2), (1, 2), (2, 1), (2, 0), (1, 0)]}, {'word': 'veratrin', 'path': [(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (3, 1), (2, 1), (3, 2)]}]

        for result in solver_results:
            word = result["word"]
            path = result["path"]
            print(f"Playing word: {word}, path: {path}")
            play_path(ser, path)
            time.sleep(0.5)  # small delay between words to avoid overlap
        
        exit(0)

if __name__ == "__main__":
    main()

    #with serial.Serial(PORT, BAUDRATE, timeout=2) as ser:
        #time.sleep(2)  # Wait for printer to initialize
        #send_gcode(ser, f"G1 Z{0} F1000")

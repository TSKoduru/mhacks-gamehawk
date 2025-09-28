import websocket
import serial
import time
from typing import Tuple, List

# --------------------------
# CONFIGURATION
# --------------------------

PORT = "/dev/ttyUSB0"               # Change this to your actual port
BAUDRATE = 115200
CELL_SIZE = 13.6  #12.15           # mm
PRESS_Z = 0                 # How far down to press relative to REST_Z
REST_Z = 3                  # Resting Z height above phone, treated as Z=0 after G92
DELAY = 0.3   
START_LOCATION = (2, 2) # Approximate location of green start button

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

def on_message(ws, message):
    print(f"Received from server: {message}")
    if message == "start":
        # TODO: press start button
        ws.send("ack")
    else:
        # TODO this is json of words list
        pass

def on_close(ws, close_status, close_msg):
    print("Connection closed")

if __name__ == "__main__":
    ws_url = "ws://172.20.10.5:8766"
    ws = websocket.WebSocketApp(
        ws_url,
        on_message=on_message,
        on_close=on_close
    )
    ws.run_forever()
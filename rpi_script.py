import websocket
import serial
import time
from typing import Tuple, List
import json 

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
    try:
        if message == "start":
            print(">> Pressing start button")
            play_path(ser, [START_LOCATION])  # Just go to the start button location
            ws.send("ack")

        else:
            data = json.loads(message)
            results = data.get("words", [])
            print(f">> Received {len(results)} words to play")

            for word_data in results:
                coords = word_data.get("coordinates", [])
                if coords:
                    print(f">> Playing word: {word_data.get('word')}")
                    play_path(ser, coords)
                else:
                    print(">> Skipping word with no coordinates.")

                time.sleep(0.5)  # Short delay between words
            ws.send("ack")
    
    except Exception as e:
        print(f"⚠️ Error in on_message: {e}")

def on_close(ws, close_status, close_msg):
    print("Connection closed")

if __name__ == "__main__":
    print("Connecting to printer...")
    ser = serial.Serial(PORT, BAUDRATE, timeout=2)
    time.sleep(2)
    ser.reset_input_buffer()

    # Home and unlock motors
    send_gcode(ser, "G28")
    send_gcode(ser, "M18 X Y Z")
    send_gcode(ser, "M84")
    input(f">> Motors unlocked. Manually move the printhead to the center of the top-left cell at resting height {REST_Z}mm, then press Enter to set home...")

    send_gcode(ser, "G92 X0 Y0 Z0")
    send_gcode(ser, "G90")

    print("✅ Printer ready. Connecting to WebSocket...")

    ws_url = "ws://172.20.10.5:8766"
    ws = websocket.WebSocketApp(
        ws_url,
        on_message=on_message,
        on_close=on_close
    )
    ws.run_forever()

import websocket
import serial
import time
from typing import Tuple, List
import json
import signal
import sys

# --------------------------
# CONFIGURATION
# --------------------------

PORT = "/dev/ttyUSB0"
BAUDRATE = 115200
CELL_SIZE = 13.6  # mm
PRESS_Z = 0
REST_Z = 3
DELAY = 0.3
START_LOCATION = (2, 2)

# --------------------------
# WebSocket debug trace
# --------------------------
websocket.enableTrace(True)

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
    if not path:
        print(">> Empty path, nothing to play.")
        return

    send_gcode(ser, f"G1 Z{REST_Z} F1000")
    max_row = 3  # For 4x4 grid

    print(f">> Playing path with {len(path)} points...")

    first_row, first_col = path[0]
    x0 = first_col * CELL_SIZE
    y0 = (max_row - first_row) * CELL_SIZE
    send_gcode(ser, f"G1 X{x0:.2f} Y{y0:.2f} F3000")

    send_gcode(ser, f"G1 Z{PRESS_Z} F1000")

    for row, col in path[1:]:
        x = col * CELL_SIZE
        y = (max_row - row) * CELL_SIZE
        send_gcode(ser, f"G1 X{x:.2f} Y{y:.2f} F3000")

    send_gcode(ser, f"G1 Z{REST_Z} F1000")
    print("✅ Path playback complete.")

# --------------------------
# Graceful shutdown handler
# --------------------------
def exit_gracefully(sig, frame):
    print("\n🛑 Exiting gracefully...")
    try:
        if ws:
            ws.close()
        if ser:
            ser.close()
    except:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, exit_gracefully)

# --------------------------
# WebSocket callbacks
# --------------------------
def on_message(ws, message):
    print(f"Received from server: {message}")
    try:
        if message == "start":
            print(">> Pressing start button")
            play_path(ser, [START_LOCATION])
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
                    time.sleep(0.5)
                else:
                    print(">> Skipping word with no coordinates.")
            ws.send("ack")

    except Exception as e:
        print(f"⚠️ Error in on_message: {e}")

def on_close(ws, close_status, close_msg):
    print(f"❌ WebSocket closed. Status: {close_status}, Message: {close_msg}")
    exit_gracefully(None, None)

def on_error(ws, error):
    print(f"⚠️ WebSocket error: {error}")
    exit_gracefully(None, None)

# --------------------------
# Main
# --------------------------
if __name__ == "__main__":
    print("Connecting to printer...")
    ser = serial.Serial(PORT, BAUDRATE, timeout=2)
    time.sleep(2)
    ser.reset_input_buffer()

    send_gcode(ser, "G28")
    send_gcode(ser, "M18 X Y Z")
    send_gcode(ser, "M84")

    input(f">> Motors unlocked. Manually move the printhead to the center of the top-left cell at resting height {REST_Z}mm, then press Enter to set home...")

    send_gcode(ser, "G92 X0 Y0 Z0")
    send_gcode(ser, "G90")
    send_gcode(ser, f"G1 Z{REST_Z} F1000")

    print("✅ Printer ready. Connecting to WebSocket...")

    ws_url = "ws://172.20.10.5:8766"
    ws = websocket.WebSocketApp(
        ws_url,
        on_message=on_message,
        on_close=on_close,
        on_error=on_error
    )
    ws.run_forever()

import json
import signal
import time
from typing import Tuple, List
import sys
from solver import load_trie, find_words
trie = load_trie("./trie.pkl")
import websocket
import serial
import numpy as np
from memryx import AsyncAccl

PORT = "/dev/ttyUSB0"
BAUDRATE = 115200
CELL_SIZE = 13.6  # mm
PRESS_Z = 0
REST_Z = 3
DELAY = 0.25
START_LOCATION = (2.5, 1.5)

DFP_PATH = "models/yolo_ocr_pipeline.dfp"  # compiled pipeline
accl = AsyncAccl(DFP_PATH)

websocket.enableTrace(True)
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

    send_gcode(ser, f"G1 Z{REST_Z} F2000")
    max_row = 3 

    print(f">> Playing path with {len(path)} points...")

    first_row, first_col = path[0]
    x0 = first_col * CELL_SIZE
    y0 = (max_row - first_row) * CELL_SIZE
    send_gcode(ser, f"G1 X{x0:.2f} Y{y0:.2f} F8000")

    send_gcode(ser, f"G1 Z{PRESS_Z} F2000")
    time.sleep(0.5)

    for row, col in path[1:]:
        x = col * CELL_SIZE
        y = (max_row - row) * CELL_SIZE
        send_gcode(ser, f"G1 X{x:.2f} Y{y:.2f} F8000")

    send_gcode(ser, f"G1 Z{REST_Z} F2000")
    print("✅ Path playback complete.")

def exit_gracefully(sig, frame):
    print("\n🛑 Exiting gracefully...")
    try:
        if ws:
            ws.close()
        if ser:
            ser.close()
        if accl:
            accl.shutdown()
    except:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, exit_gracefully)

def extract_board_letters(inp, grid_size=4):
    inp_proc = np.transpose(inp.astype(np.float32)/255.0, (2,0,1))[None, ...]  # NCHW
    results = []
    def output_processor(*logits):
        class_ids = logits[0].reshape((grid_size, grid_size))
        letters = [[chr(ord("A")+cid) for cid in row] for row in class_ids]
        results.append(letters)
    accl.connect_input(lambda: (inp_proc,))
    accl.connect_output(output_processor)
    accl.wait()
    return results[0]

def on_message(ws, message):
    print(f"Received from server: {message}")
    try:
        if json.loads(message) == "start":
            print(">> Pressing start button")
            play_path(ser, [START_LOCATION])
            ws.send("ack")
        else:
            inp = np.array(json.loads(message), dtype=np.uint8)
            letters = extract_board_letters(inp)
            print(">> Board letters:")
            for row in letters:
                print("   " + " ".join(row))

            results = find_words(letters, trie)
            print(f">> Found {len(results)} words:")
            board_message = {"board": letters, "words": results}
            ws.send(json.dumps(board_message))

            for word_data in results:
                coords = word_data.get("coordinates", [])
                if coords:
                    print(f">> Playing word: {word_data.get('word')}")
                    play_path(ser, coords)
                    time.sleep(0.5)
                else:
                    print(">> Skipping word with no coordinates.")
            send_gcode(ser, f"G1 X{START_LOCATION[0]} F2000")
            send_gcode(ser, f"G1 Y{START_LOCATION[1]} F2000")
            send_gcode(ser, f"G1 Z{REST_Z} F2000")
            ws.send("ack")

    except Exception as e:
        print(f"⚠️ Error in on_message: {e}")

def on_close(ws, close_status, close_msg):
    print(f"❌ WebSocket closed. Status: {close_status}, Message: {close_msg}")
    exit_gracefully(None, None)

def on_error(ws, error):
    print(f"⚠️ WebSocket error: {error}")
    exit_gracefully(None, None)

if __name__ == "__main__":
    print("Connecting to printer...")
    ser = serial.Serial(PORT, BAUDRATE, timeout=2)
    time.sleep(2)
    ser.reset_input_buffer()

    print("✅ Printer ready. Connecting to WebSocket...")

    ws_url = "ws://172.20.10.8:8766"
    ws = websocket.WebSocketApp(
        ws_url,
        on_message=on_message,
        on_close=on_close,
        on_error=on_error
    )
    ws.run_forever()

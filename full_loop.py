import pygetwindow as gw
import mss
import cv2
import numpy as np
import time
import easyocr

# import solver logic
from solver import load_trie, find_words
ready= False


def find_lonelyscreen_window():
    windows = gw.getWindowsWithTitle('LonelyScreen')
    if not windows:
        print("LonelyScreen window not found.")
        return None
    return windows[0]

def activate_and_maximize_window(window):
    if window.isMinimized:
        window.restore()
    window.activate()
    time.sleep(0.5)
    # Maximize window
    window.maximize()
    time.sleep(1)  # Wait for maximize animation

def capture_fullscreen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]  # Primary monitor (full screen)
        img = sct.grab(monitor)
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
        # crop to 1054, 1504 (x), 655, 1108 (y)
        img_bgr = img_bgr[150:150+1108, 105:105+655]
        return img_bgr

reader = easyocr.Reader(['en'], gpu=False)

def clean_letter(text):
    if not text:
        return "I"
    text = text.upper()[0]  # take first char
    corrections = {
        "0": "O",
        "1": "I",
        "5": "S",
        "8": "B"
    }
    return corrections.get(text, text if text.isalpha() else "?")

def extract_board_letters(img, grid_size=4):
    """
    Takes a screenshot of the Word Hunt board, runs OCR, 
    and returns a grid of recognized letters.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    h, w = thresh.shape
    board_size = min(h, w)
    start_x = (w - board_size) // 2
    start_y = (h - board_size) // 2
    board = thresh[start_y:start_y+board_size, start_x:start_x+board_size]

    cell_h, cell_w = board.shape[0] // grid_size, board.shape[1] // grid_size

    letters = []
    for r in range(grid_size):
        row = []
        for c in range(grid_size):
            cell = board[r*cell_h:(r+1)*cell_h, c*cell_w:(c+1)*cell_w]
            cell = cv2.bitwise_not(cell)
            cell = cv2.resize(cell, (200, 200), interpolation=cv2.INTER_LINEAR)
            border = 20
            cell = cell[border:-border, border:-border]
            cv2.imshow("cell", cell)
            cv2.waitKey(0)
            
            results = reader.readtext(cell)
            char = clean_letter(results[0][1] if results else "")
            row.append(char)
        letters.append(row)

    return letters

from websocket_server import WebsocketServer
import threading
import json

server = WebsocketServer(host="0.0.0.0", port=8765)
server2 = WebsocketServer(host="0.0.0.0", port=8764)
clients = []
clients2 = []

def new_client(client, server):
    print(f"New client connected: {client['id']}")
    clients.append(client)

def new_client2(client, server):
    print(f"New client connected: {client['id']}")
    clients2.append(client)

def client_left(client, server):
    print(f"Client disconnected: {client['id']}")
    clients.remove(client)

def client_left2(client, server):
    print(f"Client disconnected: {client['id']}")
    clients2.remove(client)

def send_message(message):
    for client in clients:
        server.send_message(client, json.dumps(message))

def send_message2(message):
    for client in clients2:
        server.send_message(client, json.dumps(message))

def message_received(client, server, message):
    print(f"Received message from client")
    global ready 
    ready = True

server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)

server2.set_fn_new_client(new_client2)
server2.set_fn_new_client(new_client2)

server2.set_fn_message_received(message_received)

threading.Thread(target=server.run_forever, daemon=True).start()

def main():
    global ready
    trie = load_trie("./trie.pkl")
    print("Press space bar to start game...")
    while True:
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

    # send socket message to rpi 
    message = "start"
    send_message2(message)

    # receive ack from rpi 
    while(not ready):
        pass

    window = find_lonelyscreen_window()
    if window is None:
        return

    activate_and_maximize_window(window)
    img = capture_fullscreen()

    grid = extract_board_letters(img)

    # ---------------------------
    # find words and coordinates and estimate times
    # ---------------------------
    grid = [[ch.lower() for ch in row] for row in grid] # algo needs lowercase
    results = find_words(grid, trie)

    # send words, coordinates to rpi via socket
    message = {
        "words": results
    }
    send_message2(message)

    # send grid, words, coordinates, and times to frontend via socket
    message = {
        "board": grid,
        "words": results
    }
    send_message(message)


if __name__ == "__main__":
    while True:
        main()

from websocket_server import WebsocketServer
import json
import time
from solver import load_trie, find_words
import threading

# -----------------------------
# CONFIGURATION
# -----------------------------
TRIE_PATH = "./trie.pkl"

# -----------------------------
# WebSocket handlers
# -----------------------------
server = WebsocketServer(host="0.0.0.0", port=8766)
clients = []

def new_client(client, server):
    print(f"New client connected: {client['id']}")
    clients.append(client)
    print("✅ Connected to RPi.")

    # Get board input
    board_str = input("🔤 Enter 16-letter board string (left-to-right, top-to-bottom): ").strip().lower()

    # Convert to 4x4 grid
    grid = [[ch for ch in board_str[i*4:(i+1)*4]] for i in range(4)]
    print("🧩 Grid:")
    for row in grid:
        print(" ".join(row))

    # Run solver
    trie = load_trie(TRIE_PATH)
    results = find_words(grid, trie)

    print(f"🧠 Found {len(results)} words. Sending to RPi...")

    # Send to RPi
    message = {
        "words": results
    }
    send_message(message)

def client_left(client, server):
    print(f"Client disconnected: {client['id']}")
    clients.remove(client)

def send_message(message):
    for client in clients:
        server.send_message(client, json.dumps(message))

def message_received(client, server, message):
    print(f"Received message from client")
    global ready 
    ready = True

server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)

threading.Thread(target=server.run_forever, daemon=True).start()

while True:
    pass
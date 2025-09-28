from websocket_server import WebsocketServer
import threading
import json

server = WebsocketServer(host="0.0.0.0", port=8765)
clients = []

def new_client(client, server):
    print(f"New client connected: {client['id']}")
    clients.append(client)

def client_left(client, server):
    print(f"Client disconnected: {client['id']}")
    clients.remove(client)

def send_message(message):
    for client in clients:
        server.send_message(client, json.dumps(message))

server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)

threading.Thread(target=server.run_forever, daemon=True).start()

message = {
    "board": [
        ['C', 'A', 'T', 'S'],
        ['O', 'R', 'E', 'N'],
        ['W', 'D', 'O', 'G'],
        ['M', 'E', 'A', 'L']
    ],
    "words": [
        {
            "word": 'CAT',
            "coordinates": [[0, 0], [0, 1], [0, 2]],
            "duration": 3,
            "status": 'pending'
        },
        {
            "word": 'DOG', 
            "coordinates": [[2, 2], [2, 3], [2, 1]],
            "duration": 4,
            "status": 'pending'
        },
        {
            "word": 'COW',
            "coordinates": [[0, 0], [1, 0], [2, 0]],
            "duration": 3,
            "status": 'pending'
        },
        {
            "word": 'READ',
            "coordinates": [[1, 1], [1, 2], [2, 2], [2, 1]],
            "duration": 5,
            "status": 'pending'
        },
        {
            "word": 'MEAL',
            "coordinates": [[3, 0], [3, 1], [3, 2], [3, 3]],
            "duration": 4,
            "status": 'pending'
        },
        {
            "word": 'STAR',
            "coordinates": [[0, 3], [0, 2], [0, 1], [1, 1]],
            "duration": 5,
            "status": 'pending'
        }
    ]
}

while True:
    text = input("Enter a message to send: ")
    send_message(message)

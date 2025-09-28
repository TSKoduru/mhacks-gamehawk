from websocket_server import WebsocketServer
import threading

server = WebsocketServer(host="0.0.0.0", port=8765)
clients = []

def new_client(client, server):
    print(f"New client connected: {client['id']}")
    clients.append(client)

def client_left(client, server):
    print(f"Client disconnected: {client['id']}")
    clients.remove(client)

server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)

threading.Thread(target=server.run_forever, daemon=True).start()

while True:
    text = input("Enter a message to send: ")
    send_message(text)

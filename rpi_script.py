import websocket

def on_message(ws, message):
    print(f"Received from server: {message}")
    if message == "start":
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
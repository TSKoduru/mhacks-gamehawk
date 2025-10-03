import pygetwindow as gw
import mss
import cv2
import numpy as np
import time
import keyboard 
import win32gui
import win32con
import win32com.client
import memryx
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
    hwnd = window._hWnd  # get native window handle

    # Restore if minimized
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.2)

    # Force foreground
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')  # Send ALT key to allow SetForegroundWindow
    win32gui.SetForegroundWindow(hwnd)

    # Maximize
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
    time.sleep(0.5)

def capture_fullscreen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]  # Primary monitor (full screen)
        img = sct.grab(monitor)
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
        # crop to 1054, 1504 (x), 655, 1108 (y)
        img_bgr = img_bgr[896:150+1108, 1062:150+1264]
        return img_bgr

def send_img_to_pi(img):
    """
    Input: BGR board screenshot
    Output:rpi handles it
    """

    # preprocessing so we can run the yolo model on rpi after sending thorugh scoket
    inp = cv2.resize(img, (640, 640))          
    inp = cv2.cvtColor(inp, cv2.COLOR_BGR2RGB) 
    inp = inp.astype(np.float32) / 255.0  
    inp = np.transpose(inp, (2,0,1))
    inp = np.expand_dims(inp, 0) 


    # no output, send raw image data to pi and compute shit on that end
    send_message2(inp)

from websocket_server import WebsocketServer
import threading
import json

server = WebsocketServer(host="0.0.0.0", port=8765)
server2 = WebsocketServer(host="0.0.0.0", port=8766)
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
    disconnected = []
    for client in clients:
        try:
            server.send_message(client, json.dumps(message))
        except Exception as e:
            print(f"Error sending message to client {client['id']}: {e}")
            disconnected.append(client)
    
    for client in disconnected:
        try:
            clients.remove(client)
        except ValueError:
            pass

def send_message2(message):
    disconnected = []
    for client in clients2:
        try:
            server.send_message(client, json.dumps(message))
        except Exception as e:
            print(f"Error sending message to client {client['id']}: {e}")
            disconnected.append(client)
    
    # Remove disconnected clients
    for client in disconnected:
        try:
            clients2.remove(client)
        except ValueError:
            pass

def message_received(client, server, message):
    print(f"Received message from client")
    global ready 
    ready = True
    if message != "ack":
        send_message(message) # send to webserver

server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)

server2.set_fn_new_client(new_client2)
server2.set_fn_new_client(new_client2)

server2.set_fn_message_received(message_received)

threading.Thread(target=server.run_forever, daemon=True).start()
threading.Thread(target=server2.run_forever, daemon=True).start()


def main():
    global ready
    print("in main")
    while not clients2:
        pass
    print("Press ~ to start game...")
    
    # Wait for spacebar press before continuing
    keyboard.wait("~")

    # send socket message to rpi 
    message = "start"
    send_message2(message)

    # receive ack from rpi 
    while(not ready):
        pass

    # allow time to hit the start
    time.sleep(1)
    
    window = find_lonelyscreen_window()
    if window is None:
        return

    activate_and_maximize_window(window)
    img = capture_fullscreen()
    send_img_to_pi(img)

    # wait for rpi to send back board and words
    ready = False
    while(not ready):
        pass

if __name__ == "__main__":
    while True:
        main()

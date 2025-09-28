import pygetwindow as gw
import time
import mss
import cv2
import numpy as np

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
        # img_bgr = img_bgr[150:150+1108, 105:105+655]
        return img_bgr
    
window = find_lonelyscreen_window()

activate_and_maximize_window(window)
img = capture_fullscreen()
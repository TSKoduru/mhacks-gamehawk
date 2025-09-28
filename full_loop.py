import pygetwindow as gw
import mss
import cv2
import numpy as np
import time
import easyocr

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
    
    Args:
        image_path (str): Path to the screenshot image.
        grid_size (int): Number of cells per row/col (default=4 for Word Hunt).
        
    Returns:
        list[list[str]]: grid_size x grid_size grid of letters.
    """

    # Preprocess: convert to grayscale and threshold
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Assume the board is roughly square in the center — crop dynamically if needed
    h, w = thresh.shape
    board_size = min(h, w)
    start_x = (w - board_size) // 2
    start_y = (h - board_size) // 2
    board = thresh[start_y:start_y+board_size, start_x:start_x+board_size]

    # Divide into grid
    cell_h, cell_w = board.shape[0] // grid_size, board.shape[1] // grid_size

    letters = []
    for r in range(grid_size):
        row = []
        for c in range(grid_size):
            cell = board[r*cell_h:(r+1)*cell_h, c*cell_w:(c+1)*cell_w]

            # Optional: pad & clean cell for better OCR
            # show cell
            cell = cv2.bitwise_not(cell)
            cell = cv2.resize(cell, (200, 200), interpolation=cv2.INTER_LINEAR)
            # crop border
            border = 20
            cell = cell[border:-border, border:-border]
            cv2.imshow("cell", cell)
            cv2.waitKey(0)
            
            results = reader.readtext(cell)
            char = clean_letter(results[0][1] if results else "")
            row.append(char)
        letters.append(row)

    return letters

def main():
    # wait for space bar press
    print("Press space bar to start game...")
    while True:
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

    # send socket message to rpi 
    # TODO

    # receive ack from rpi 
    # TODO

    # take screenshot
    window = find_lonelyscreen_window()
    if window is None:
        return

    activate_and_maximize_window(window)
    img = capture_fullscreen()

    # detect 
    grid = extract_board_letters(img)

    # find words and coordinates and estimate times
    # TODO

    # send grid, words, coordinates to rpi via socket
    # TODO

    # send grid, words, coordinates, and times to frontend via socket
    # TODO



if __name__ == "__main__":
    while True:
        main()

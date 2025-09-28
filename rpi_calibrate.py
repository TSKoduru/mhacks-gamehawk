import serial
import time

PORT = "/dev/ttyUSB0"
BAUDRATE = 115200
REST_Z = 2
DELAY = 0.25

def send_gcode(ser, command: str, wait: float = DELAY):
    print(f"> {command}")
    ser.write((command + "\n").encode())
    time.sleep(wait)
    while ser.in_waiting:
        line = ser.readline().decode().strip()
        print(f"< {line}")

if __name__ == "__main__":
    print("Connecting to printer for calibration...")
    ser = serial.Serial(PORT, BAUDRATE, timeout=2)
    time.sleep(2)
    ser.reset_input_buffer()

    send_gcode(ser, "G28")            # Home all axes
    send_gcode(ser, "M18 X Y Z")     # Disable motors
    send_gcode(ser, "M84")           
    send_gcode(ser, f"G1 Z{5*REST_Z} F1000")
    
    input(f">> Motors unlocked. Manually move the printhead to the center of the top-left cell at resting height {REST_Z}mm, then press Enter to set home...")

    send_gcode(ser, "G92 X0 Y0 Z0")  # Set current position as zero
    send_gcode(ser, "G90")            # Use absolute positioning
    send_gcode(ser, f"G1 Z{REST_Z} F1000")  # Move to resting height

    print("✅ Calibration complete. You can now run the main script without calibration.")
    ser.close()

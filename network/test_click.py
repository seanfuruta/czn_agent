import socket

PICO_IP = "192.168.50.168"
PORT = 4242

# Pixel 7 Resolution
SCREEN_W = 1080
SCREEN_H = 2400

def get_hid_coords(pixel_x, pixel_y):
    # Convert pixels to the 0-32767 scale defined in boot.py
    hid_x = int((pixel_x / SCREEN_W) * 32767)
    hid_y = int((pixel_y / SCREEN_H) * 32767)
    return hid_x, hid_y

def send_click(x, y):
    hx, hy = get_hid_coords(x, y)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((PICO_IP, PORT))
        # Send the command to the code.py listener
        s.sendall(f"CLICK:{hx}:{hy}".encode())
        print(f"Sent Click to Pixel: ({x}, {y}) -> HID: ({hx}, {hy})")

if __name__ == "__main__":
    # Test: Click the middle of the screen
    send_click(540, 1200)
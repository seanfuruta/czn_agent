import socket
import time

# --- CONFIGURATION ---
# Replace with the IP address printed in your Pico's serial console
PICO_IP = "192.168.50.168" 
PORT = 4242

# Pixel 7 Screen Resolution
SCREEN_WIDTH = 2400
SCREEN_HEIGHT = 1080

# Setup Socket with a 2-second timeout for the handshake
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2.0)

def send_action(message):
    """Sends a command and waits for the Pico's ACK confirmation."""
    try:
        sock.sendto(message.encode('utf-8'), (PICO_IP, PORT))
        data, _ = sock.recvfrom(1024)
        print(f"Pico Confirmed: {data.decode('utf-8')}")
        return True
    except socket.timeout:
        print("!! TIMEOUT: Pico did not respond. Check Wi-Fi/IP.")
        return False

def click(pixel_x, pixel_y):
    hid_x = int((pixel_x / SCREEN_WIDTH) * 32767)
    hid_y = int((pixel_y / SCREEN_HEIGHT) * 32767)
    return send_action(f"CLICK:{hid_x}:{hid_y}")

def swipe(x1, y1, x2, y2):
    hx1 = int((x1 / SCREEN_WIDTH) * 32767)
    hy1 = int((y1 / SCREEN_HEIGHT) * 32767)
    hx2 = int((x2 / SCREEN_WIDTH) * 32767)
    hy2 = int((y2 / SCREEN_HEIGHT) * 32767)
    return send_action(f"SWIPE:{hx1}:{hy1}:{hx2}:{hy2}")

if __name__ == "__main__":
    print(f"Connecting to Pico at {PICO_IP}...")
    print("Prepare your Pixel 7. Starting test in 3 seconds...")
    time.sleep(3)

    # Test 1: Center Tap
    print("\n[1/3] Testing Center Tap...")
    if click(1200, 540):
        time.sleep(1)

        # Test 2: Swipe Right
        print("[2/3] Testing Swipe Right...")
        if swipe(600, 540, 1800, 540):
            time.sleep(1)

            # Test 3: Swipe Left
            print("[3/3] Testing Swipe Left...")
            swipe(1800, 540, 600, 540)

    print("\nAll tests complete.")
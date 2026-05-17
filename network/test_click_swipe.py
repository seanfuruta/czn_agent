import socket
import time

# --- CONFIGURATION ---
PICO_IP = "192.168.50.168"
PORT = 4242

# High-Res Absolute scale used by adafruit_hid in our boot.py
HID_MAX = 32767

# Pixel 7 Screen Resolution for mapping
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 2400

def to_hid_units(pixel_val, screen_max, is_y=False):
    """
    Converts pixel coordinates to the 0-32767 HID range.
    """
    scaled = (pixel_val / screen_max) * HID_MAX
    
    # Pixel 7 Y-axis logic: 
    # If clicks are inverted, change this to return int(scaled)
    # if is_y:
    #     return int(HID_MAX - scaled)
    return int(scaled)

def send_command(command):
    """Sends the command string to the Pico agent."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((PICO_IP, PORT))
            print(f"Sending: {command}")
            sock.sendall(command.encode('utf-8'))
            
            response = sock.recv(1024).decode('utf-8')
            print(f"Agent Response: {response}")
            return response
    except Exception as e:
        print(f"Network Error: {e}")
        return None

def run_test():
    # 1. CENTER CLICK TEST
    # Target: 540, 1200
    cx =100 #to_hid_units(0, SCREEN_WIDTH)
    cy = 100#to_hid_units(0, SCREEN_HEIGHT, is_y=True)
    
    print(f"--- TESTING CENTER CLICK ({cx}, {cy}) ---")
    send_command(f"CLICK:{cx}:{cy}")
    
    # time.sleep(2)

    # 2. SWIPE TEST (Pull down notification shade)
    # Target: Top middle to bottom middle
    # print("--- TESTING SWIPE (NOTIFICATION SHADE) ---")
    # sx = to_hid_units(540, SCREEN_WIDTH)
    # sy_start = to_hid_units(20, SCREEN_HEIGHT, is_y=True)
    # sy_end = to_hid_units(1800, SCREEN_HEIGHT, is_y=True)
    
    # send_command(f"SWIPE:{sx}:{sy_start}:{sx}:{sy_end}")

if __name__ == "__main__":
    print(f"Connecting to Chaos Zero Agent at {PICO_IP}...")
    run_test()
    print("\nTest complete.")
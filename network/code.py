import wifi
import socketpool
import os
import usb_hid
import time
import digitalio
import board
import microcontroller
from adafruit_hid.mouse import Mouse

# --- 1. HARDWARE & STATUS ---
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# --- 2. AGGRESSIVE WIFI RESET ---
# Addresses the power delivery issues common with Pixel OTG connections
print("Hard resetting Wi-Fi radio...")
wifi.radio.enabled = False
time.sleep(1.5) 
wifi.radio.enabled = True
time.sleep(1.5) 

SSID = os.getenv('WIFI_SSID')
PASS = os.getenv('WIFI_PASSWORD')

for attempt in range(3):
    try:
        print(f"Connection Attempt {attempt + 1}...")
        wifi.radio.connect(SSID, PASS)
        print(f"Connected! IP: {wifi.radio.ipv4_address}")
        break 
    except Exception as e:
        print(f"Connection failed: {e}")
        if attempt == 2:
            print("Final failure. Hard rebooting...")
            time.sleep(5)
            microcontroller.reset()
        time.sleep(2)

# --- 3. HID SETUP VIA LIBRARY ---
# The library automatically finds the Mouse device you enabled in boot.py


# We pass the report_id explicitly so the library formats 6-byte packets
try:
    # We find our specific device from the usb_hid pool
    target_device = None
    for dev in usb_hid.devices:
        if dev.usage == 0x02 and dev.usage_page == 0x01:
            target_device = dev
            break
            
    if target_device:
        # CRITICAL: We tell the library to use Report ID 1
        mouse = Mouse(target_device, report_id=1) 
        print("SUCCESS: Mouse initialized with Report ID 1")
    else:
        print("ERROR: Device not found")
except Exception as e:
    print(f"Library Init Error: {e}")

def send_click(x_hid, y_hid):
    if mouse:
        # The library now handles the ID '1' prefix automatically
        mouse.move(x=int(x_hid), y=int(y_hid), absolute=True)
        time.sleep(0.1)
        mouse.click(Mouse.LEFT_BUTTON)
        print(f"Library ID-1 Click: {x_hid}, {y_hid}")
# def send_swipe(x1, y1, x2, y2, steps=100):
#     """
#     Simulates a human-like drag which is safer for anti-cheat systems.
#     """
#     if mouse:
#         try:
#             # Move to start and press
#             mouse.move(x=int(x1), y=int(y1), absolute=True)
#             time.sleep(0.05)
#             mouse.press(Mouse.LEFT_BUTTON)
            
#             # Incremental movement
#             for i in range(1, steps + 1):
#                 cx = int(x1 + (x2 - x1) * i / steps)
#                 cy = int(y1 + (y2 - y1) * i / steps)
#                 mouse.move(x=cx, y=cy, absolute=True)
#                 time.sleep(0.01)
                
#             mouse.release(Mouse.LEFT_BUTTON)
#             print("Swipe executed.")
#         except Exception as e:
#             print(f"SWIPE ERROR: {e}")

# --- 5. MAIN SERVER LOOP ---
pool = socketpool.SocketPool(wifi.radio)
server_sock = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
server_sock.bind(('0.0.0.0', 4242))
server_sock.listen(1)

print("TCP BACKDOOR READY.")

while True:
    try:
        server_sock.settimeout(1.0)
        conn, addr = server_sock.accept()
        with conn:
            print(f"PC Connected: {addr}")
            while True:
                buf = bytearray(1024)
                size = conn.recv_into(buf)
                if size == 0: break
                
                msg = buf[:size].decode('utf-8')
                
                if msg.startswith("CLICK:"):
                    _, x, y = msg.split(":")
                    send_click(int(x), int(y))
                    conn.send(b"ACK: CLICK_DONE")
                elif msg.startswith("SWIPE:"):
                    p = msg.split(":")
                    send_swipe(int(p[1]), int(p[2]), int(p[3]), int(p[4]))
                    conn.send(b"ACK: SWIPE_DONE")
                elif msg.startswith("UPDATE:"):
                    # Basic placeholder for your file update logic
                    conn.send(b"ACK: READY_FOR_UPDATE")
                    break
                    
    except Exception:
        pass
    
    # Heartbeat LED
    led.value = True
    time.sleep(0.1)
    led.value = False
    time.sleep(0.4)
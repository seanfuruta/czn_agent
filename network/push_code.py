import socket
import os
import time

PICO_IP = "192.168.50.168"
PORT = 4242
# PC Path (where the file is on your computer)
LOCAL_FILE_PATH = "chaos-zero-agent/network/code.py" 
# Pico Path (where it should live on the microcontroller)
REMOTE_FILENAME = "code.py" 

def push_update():
    if not os.path.exists(LOCAL_FILE_PATH):
        print(f"ERROR: {LOCAL_FILE_PATH} not found.")
        return

    filesize = os.path.getsize(LOCAL_FILE_PATH)
    with open(LOCAL_FILE_PATH, "rb") as f:
        content = f.read()

    print(f"Connecting to Pico at {PICO_IP}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((PICO_IP, PORT))
        
        # Send header with ONLY the filename 'code.py', not the full PC path
        header = f"UPDATE:{REMOTE_FILENAME}:{filesize}"
        print(f"Sending header: {header}")
        sock.sendall(header.encode('utf-8'))
        
        time.sleep(0.7) 
        sock.sendall(content)
        print("Push complete!")
    except Exception as e:
        print(f"Transfer failed: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    push_update()
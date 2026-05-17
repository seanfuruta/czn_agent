import socket

PICO_IP = "192.168.50.168"
PORT = 4242

def send_to_agent(command):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((PICO_IP, PORT))
            sock.sendall(command.encode('utf-8'))
            response = sock.recv(1024).decode('utf-8')
            print(f"Pico Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

# TEST 1: The "Absolute Top" to "Absolute Bottom"
# We will send raw HID units to bypass any math errors for now.
print("Testing Raw HID Swipe...")
# Start: Middle Width (16383), Top (0)
# End: Middle Width (16383), Bottom (32767)
# IF THIS PULLS UP THE TRAY, THEN 32767 IS THE TOP.
raw_cmd = "SWIPE:16383:0:16383:30000"
send_to_agent(raw_cmd)
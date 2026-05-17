import socket
import time

PICO_IP = "192.168.50.168"
PORT = 4242

def ota_clean_test():
    # Attempt to clear any current 'ghost' touch first
    print("Sending Nuke-Release...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((PICO_IP, PORT))
        s.sendall(b"RELEASE:0:0") # You must add the RELEASE case to code.py!
    
    time.sleep(2.0)
    
    # Send ONE click to the center of the screen
    print("Sending Center-Click...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((PICO_IP, PORT))
        # RAW HID Units for the center of the screen
        s.sendall(b"CLICK:16383:16383") 

if __name__ == "__main__":
    ota_clean_test()
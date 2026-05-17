import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# FORCE Python to use your Ethernet adapter (Replace with your PC's IPv4 address)
sock.bind(('10.143.168.169.', 0)) 

# Fire the packet at the Pico (Replace with the Pico's IP address)
sock.sendto(b"CLICK:1200:540", ("10.143.168.1", 4242))
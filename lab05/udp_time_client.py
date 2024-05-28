import time
import socket
import sys

def get_time():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    client_socket.bind(("", 12000))
    data, server = client_socket.recvfrom(1024)
    print(str(data, sys.stdout.encoding))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for i in range(int(sys.argv[1])):
            get_time()
    else:
        while True:
            get_time()


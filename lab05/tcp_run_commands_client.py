import socket
import threading
import sys

HOST = "127.0.0.1"
PORT = 54321

def send_request():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    message = input(">> ")

    while message.lower().strip() != "quit":
        client_socket.send(message.encode())
        data = client_socket.recv(1024).decode()
        if data.split(' ', 1)[0].lower().strip() == "quit":
            print("Server response:\n" + data.split(' ', 1)[1])
            print("Connection closed.")
            break
        print("Server response:\n" + data)
        message = input(">> ")
        
    client_socket.close()


if __name__ == "__main__":
    print("Client is running.")
    PORT = int(sys.argv[1])
    send_request()
        

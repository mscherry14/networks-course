import sys, socket, subprocess, shlex

HOST = "0:0:0:0:0:0:0:1"
PORT = 48484

with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT, 0, 0))
    server_socket.listen()

    print("Server is running.")

    conn, address = server_socket.accept()
    print(str(address[0])+":"+ str(address[1]) + " is connected")
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        print("Connected user's input: " + str(data))
        try:
            conn.sendall(data.upper().encode())
        except BaseException as err:
            conn.sendall("Quit. Server unexpected error. Connection will be terminated".encode())
            conn.sendall("quit".encode())
            conn.close()
            raise
    
    conn.close()

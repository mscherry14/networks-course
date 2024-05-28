import sys, socket, subprocess, shlex

HOST = "127.0.0.1"
PORT = 48484

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
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
            command = str(data)
            op = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            if op:
                output = str(op.stdout.read(), sys.stdout.encoding)
                print("Output:", output)
                error = str(op.stderr.read(), sys.stdout.encoding)
                print("Error:", error)
                streamdata = op.communicate()[0]
                code = str(op.returncode)
                print("Return Code:",code)
                message = "Output: " + output + "\n Error: " + error + "\n Code: " + code
                conn.sendall(message.encode())
            else:
                print("Subprocess error")
                conn.sendall("Subprocess error".encode())
        except BaseException as err:
            conn.sendall("Quit. Server unexpected error. Connection will be terminated".encode())
            conn.sendall("quit".encode())
            conn.close()
            raise
    
    conn.close()

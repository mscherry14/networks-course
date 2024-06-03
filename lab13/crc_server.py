import socket
import sys
import random
 
HOST = '127.0.0.1'
PORT = 48484
KEY = "1001"
 
def xor(a, b):
    result = []
    for i in range(1, len(b)):
        if a[i] == b[i]:
            result.append('0')
        else:
            result.append('1')
 
    return ''.join(result)
 
 
def crc(dividend, divisor):
    pick = len(divisor)
    tmp = dividend[0 : pick]
    while pick < len(dividend):
        if tmp[0] == '1':
            tmp = xor(divisor, tmp) + dividend[pick]
        else:
            tmp = xor('0'*pick, tmp) + dividend[pick]
 
        pick += 1
 
    if tmp[0] == '1':
        tmp = xor(divisor, tmp)
    else:
        tmp = xor('0'*pick, tmp)
 
    checkword = tmp
    return checkword
 

def receive(key, data):
    checkword = crc(data, key)
    print(checkword)
    if checkword == '0' * (len(data) - 1):
        return 'Success', checkword
    else:
        return 'Error', checkword

def server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()

    print("Server is running.")

    conn, address = server_socket.accept()
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        print("Connected user's input: " + str(data))
        res = receive(KEY, data)
        msg = "Received: " + data + ' --- ' + res[0] + ' --- ' + "Reminder: " + res[1]
        conn.sendall(msg.encode())
        
    conn.close()


def get_args(start):
    host, port = HOST, PORT
    i = start
    while i < len(sys.argv):
        match sys.argv[i]:
            case "-p":
                if i + 1 >= len(sys.argv):
                    raise Exception("{} option require an argument".format(sys.argv[i]))
                else:
                    try:
                        port = int(sys.argv[i + 1])
                        i = i + 1
                    except Exception:
                        raise Exception("wrong argument for {} option".format(sys.argv[i]))
            case "--port":
                if i + 1 >= len(sys.argv):
                    raise Exception("{} option require an argument".format(sys.argv[i]))
                else:
                    try:
                        port = int(sys.argv[i + 1])
                        i = i + 1
                    except Exception:
                        raise Exception("wrong argument for {} option".format(sys.argv[i]))
            
            case "-h":
                if i + 1 >= len(sys.argv):
                    raise Exception("{} option require an argument".format(sys.argv[i]))
                else:
                    try:
                        host = sys.argv[i + 1]
                        i = i + 1
                    except Exception:
                        raise Exception("wrong argument for {} option".format(sys.argv[i]))
            case "--host":
                if i + 1 >= len(sys.argv):
                    raise Exception("{} option require an argument".format(sys.argv[i]))
                else:
                    try:
                        host = sys.argv[i + 1]
                        i = i + 1
                    except Exception:
                        raise Exception("wrong argument for {} option".format(sys.argv[i]))
            case _:
                raise Exception("unknow option")
        i = i + 1
    return host, port

def main():
    try:
        host, port = get_args(1)
    except Exception as e:
        print("Error:", e.args[0])
        return
    server(host, port)

if __name__ == "__main__":
    main()

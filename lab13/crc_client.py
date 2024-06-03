import socket
import sys
import random
 
HOST = '127.0.0.1'
PORT = 48484
ERRORS = False
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
 

def encodeData(data, key):
    appended_data = data + '0' * (len(key) - 1)
    remainder = crc(appended_data, key)
    codeword = data + remainder
    return codeword
     
     
def send_packets(host, port, errors=False):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
 
    input_string = input("Enter data you want to send->")

    data =(''.join(format(ord(x), 'b') for x in input_string))
    print("Entered data in binary format :",data)
    
    tmp = data
    i = 1
    while len(tmp) > 0:
        packet = tmp[ : min(5, len(tmp))]
        
        ans = encodeData(packet, KEY)
        print("Packet {}\nEncoded data to be sent to server in binary format :".format(i), ans)
        
        if errors:
            if random.random() < 0.3:
                ind = random.randint(0, len(ans) - 1)
                if ans[ind] == '1':
                    ans = ans[: ind] + '0' + ans[ind + 1:]
                else:
                    ans = ans[: ind] + '1' + ans[ind + 1:]
        s.sendto(ans.encode(), (host, port))
 
        print("Received feedback from server :", s.recv(1024).decode())
        print("----------")
        
        tmp = tmp[min(5, len(tmp)):]
        i = i + 1
 
    s.close()

def get_args(start):
    host, port, errors = HOST, PORT, ERRORS
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
            case "--error":
                errors = True
                i = i + 1
                
            case "-e":
                errors = True
                i = i + 1
            case _:
                raise Exception("unknow option")
        i = i + 1
    return host, port, errors

def main():
    try:
        host, port, errors = get_args(1)
    except Exception as e:
        print("Error:", e.args[0])
        return
    send_packets(host, port, errors)

if __name__ == "__main__":
    main()

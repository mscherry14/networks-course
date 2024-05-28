import sys
import random
import socket
import struct
from checksum import check_checksum

DEFAULT_PORT = 48484
DEFAULT_PACKET_SIZE = 1024
RECEIVED_FILE_PATH = 'received.bin'

class Server:
    def __init__(self, port, packet_size):
        self.port = port
        self.packet_size = packet_size
        self.data = {}

    def start(self):
        print("Server started: port {}, packet_size {}".format(self.port, self.packet_size))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', self.port))

        while True:
            buf, addr = self.socket.recvfrom(self.packet_size)
            np = struct.unpack('i', buf[:4])[0]
            if np == 0:
                total = struct.unpack('i', buf[4:8])[0]
                num = struct.unpack('i', buf[8:12])[0]
                self.data[addr] = num, bytearray(total)
                check = 0
            else:
                check = struct.unpack('H', buf[4:6])[0]
            nt = struct.unpack('b', buf[12:13])[0]
            print('Packet # %d was received, try is %d, check is %d' % (np, nt, check))

            if random.randint(0, 100) < 30:
                print('Imitate lost for packet %d try %d' % (np, nt))
                continue

            if np == 0:
                is_check = True
            else:
                is_check = check_checksum(buf[13:], check)
            resp = bytearray(12)
            resp[:8] = buf[:8]
            if is_check:
                resp[8:] = b'ASK '
            else:
                resp[8:] = b'RETR'
            self.socket.sendto(resp, addr)

            if np > 0:
                total = len(self.data[addr][1])
                sz = self.packet_size - 13
                i1 = (np - 1) * sz
                i2 = min(total, np * sz)
                self.data[addr][1][i1:i2] = buf[13:13 + i2 - i1]
                if np == self.data[addr][0]:
                    self.save_file(RECEIVED_FILE_PATH, addr)
                    del self.data[addr]
                    break
        self.socket.close()


    def save_file(self, fn, addr):
        f = open(fn, 'wb')
        f.write(self.data[addr][1])
        f.close()

def get_args(start):
    port, packet_size = DEFAULT_PORT, DEFAULT_PACKET_SIZE
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
            
            case "-s":
                if i + 1 >= len(sys.argv):
                    raise Exception("{} option require an argument".format(sys.argv[i]))
                else:
                    try:
                        packet_size = int(sys.argv[i + 1])
                        i = i + 1
                    except Exception:
                        raise Exception("wrong argument for {} option".format(sys.argv[i]))
            case "--packet_size":
                if i + 1 >= len(sys.argv):
                    raise Exception("{} option require an argument".format(sys.argv[i]))
                else:
                    try:
                        packet_size = int(sys.argv[i + 1])
                        i = i + 1
                    except Exception:
                        raise Exception("wrong argument for {} option".format(sys.argv[i]))
            
            case "--p_size":
                if i + 1 >= len(sys.argv):
                    raise Exception("{} option require an argument".format(sys.argv[i]))
                else:
                    try:
                        packet_size = int(sys.argv[i + 1])
                        i = i + 1
                    except Exception:
                        raise Exception("wrong argument for {} option".format(sys.argv[i]))
            case _:
                raise Exception("unknow option")
        i = i + 1
    return port, packet_size


def main():
    try:
        port, packet_size = get_args(1)
    except Exception as e:
        print("Error:", e.args[0])
        return
    server = Server(port, packet_size)
    server.start()


if __name__ == '__main__':
    main()

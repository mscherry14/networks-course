import random
import struct
import socket
import sys
from checksum import get_checksum

DEFAULT_PORT = 48484
DEFAULT_TIMEOUT = 0.2
DEFAULT_PACKET_SIZE = 1024
RECEIVED_FILE_PATH = 'received.bin'
SEND_FILE_PATH = 'send.bin'


class Client:
    def __init__(self, port, packet_size, timeout):
        self.server = '127.0.0.1'
        self.port = port
        self.timeout = timeout
        self.packet_size = packet_size


    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except:
            return False
        self.socket.settimeout(self.timeout)
        return True

    def close(self):
        self.socket.close()

    def send_packet(self, i: int, packet: bytes) -> bool:
        addr = self.server, self.port
        for n_try in range(10):
            packet[12:13] = struct.pack('b', n_try)

            ## imitate lost packets
            if random.randint(0, 100) > 29:
                self.socket.sendto(packet, addr)

            try:
                data, _ = self.socket.recvfrom(self.packet_size)
                if data[8:11] == b'ASK':
                    return True
            except socket.timeout:
                print('-- Timeout for packet %d: try %d' % (i, n_try))
                pass

        return False


    def send_data(self, buf: bytes):
        if self.connect():
            total = len(buf)
            packet = bytearray(self.packet_size)
            sz = self.packet_size - 13
            n = total // sz
            if total % sz:
                n += 1
            print('Number of packets: %d' % n)

            packet[:4] = struct.pack('i', 0)
            packet[4:8] = struct.pack('i', total)
            packet[8:12] = struct.pack('i', n)
            if not self.send_packet(0, packet):
                return False

            for i in range(n):
                i1, i2 = i * sz, min((i + 1) * sz, total)
                check = get_checksum(buf[i1:i2])
                packet[:4] = struct.pack('i', i + 1)
                packet[4:6] = struct.pack('H', check)
                packet[13:] = buf[i1:i2]
                if self.send_packet(i + 1, packet):
                    print('Send packet %d checksum %d' % ((i + 1), check))
                    pass
                else:
                    print('Error sending packet # %d.' % (i + 1))
                    return False
            return True
        return False

def read_file(fn: str) -> bytes:
    f = open(fn, 'br')
    res = f.read()
    f.close()
    return res


def check_files(f1, f2):
    return read_file(f1) == read_file(f2)

def get_args(start):
    port, packet_size, timeout = DEFAULT_PORT, DEFAULT_PACKET_SIZE, DEFAULT_TIMEOUT
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
            case "-t":
                if i + 1 >= len(sys.argv):
                    raise Exception("{} option require an argument".format(sys.argv[i]))
                else:
                    try:
                        timeout = float(sys.argv[i + 1])
                        i = i + 1
                    except Exception:
                        raise Exception("wrong argument for {} option".format(sys.argv[i]))
            case "--timeout":
                if i + 1 >= len(sys.argv):
                    raise Exception("{} option require an argument".format(sys.argv[i]))
                else:
                    try:
                        timeout = float(sys.argv[i + 1])
                        i = i + 1
                    except Exception:
                        raise Exception("wrong argument for {} option".format(sys.argv[i]))
            case _:
                raise Exception("unknow option")
        i = i + 1
    return port, packet_size, timeout


def main():
    try:
        port, packet_size, timeout = get_args(1)
    except Exception as e:
        print("Error:", e.args[0])
        return
    client = Client(port, packet_size, timeout)
    print("Client started: port {}, packet_size {}, timeout {}".format(port, packet_size, timeout))
    if client.send_data(read_file(SEND_FILE_PATH)):
        print('Data was sent successfully.')
        client.close()
        
        if check_files(SEND_FILE_PATH, RECEIVED_FILE_PATH):
            print('Sent and received files are the same.')
        else:
            print('Sent and received files are different.')

if __name__ == '__main__':
    main()

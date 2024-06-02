import time
import socket
import struct
import select
import random
import math
import sys
import os

ICMP_ECHO_REPLY = 0
ICMP_ECHO_REQUEST = 8
ICMP_TIME_EXCEEDED = 11

FIRST_TTL = 1
MAX_HOPS = 64
NQUERIES = 3
ICMP_CODE = socket.getprotobyname('icmp')

def checksum(source_string):
    sum = 0
    count_to = (len(source_string) / 2) * 2
    count = 0
    while count < count_to:
        this_val = source_string[count + 1]*256+source_string[count]
        sum = sum + this_val
        sum = sum & 0xffffffff
        count = count + 2
    if count_to < len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
        sum = sum & 0xffffffff
    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def create_packet(seq_number, data_size = 64):
    data_zero = data_size * '0'
    data = struct.pack("d", time.time())
    my_id = os.getpid() & 0xFFFF
    header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, 0, my_id, 1)
    my_checksum = checksum(header + data + data_zero.encode())
    header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0,
                         socket.htons(my_checksum), my_id, seq_number)
    return header + data+ data_zero.encode()


def one_trace(dest_addr, ttl, seq_number, timeout, time_left):
    with socket.socket(socket.AF_INET, socket.SOCK_RAW, ICMP_CODE) as raw_socket:
        raw_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, struct.pack('I', ttl))
        raw_socket.settimeout(timeout)
        
        host = socket.gethostbyname(dest_addr)
        packet = create_packet(seq_number)
        raw_socket.sendto(packet, (dest_addr, 0))
        time_sent = time.time()

        started_select = time.time()
        what_ready = select.select([raw_socket], [], [], timeout)
        time_in_select = time.time() - started_select
        if what_ready[0] == []:  # Timeout
            print(" *", end='', flush=True)
            return time_left - (time.time() - started_select), "", ""

        time_left = time_left - time_in_select
        if time_left <= 0:  # Timeout
            print(" *", end='', flush=True)
            return time_left, "", ""

        time_received = time.time()
        rec_packet, addr = raw_socket.recvfrom(1024)
        icmp_header = rec_packet[20:28]
        icmp_type, code, checksum, packetID, sequence = struct.unpack(
            "!BBHHH", icmp_header)
        addr_name = get_addr_name(addr[0])

        if icmp_type == ICMP_TIME_EXCEEDED:
            return time_left, " %s (%s) " % (addr_name, addr[0]), " %.2f ms" % ((time_received - time_sent) * 1000)
        elif icmp_type == ICMP_ECHO_REPLY:
            byte = struct.calcsize("d")
            time_sent = struct.unpack("d", rec_packet[28:28 + byte])[0]
            return -1, " %s (%s) " % (addr_name, addr[0]), " %s (%s)  %.2f ms" % (addr_name, addr[0], (time_received - time_sent) * 1000)
        else:
            return time_left, " %s (%s) " % (addr_name, addr[0]), " %.2f ms" % ((time_received - time_sent) * 1000)



def traceroute(host, first_ttl, max_ttl, nqueries, timeout=1):
    time_left = timeout * max_ttl * nqueries
    dest = socket.gethostbyname(host)
    print("Traceroute to " + host + " (%s), %d hops max:"
          % (dest, max_ttl))

    for ttl in range(first_ttl, max_ttl + 1):
        print(" %d " % (ttl), end = '')
        for num in range(0, nqueries):
            res = one_trace(dest, ttl, 3 * ttl - 2 + num, timeout, time_left)
            time_left = res[0]
            if num == 0:
                prev = res[1]
                print(res[1], end='')
            else:
                if res[1] != prev:
                    prev = res[1]
                    print(res[1], end='')
            print(res[2], end = '', flush=True)
            if time_left <= 0:
                break
        print()
        if time_left <= 0:
            break

    if ttl == max_ttl:
        print("Timeout: Exceeded %d hops" % max_ttl)

    return

def get_addr_name(addr):
    try:
        return socket.gethostbyaddr(addr)[0]
    except socket.herror:
        return addr


def get_args(start):
    first_ttl, max_ttl, nqueries = FIRST_TTL, MAX_HOPS, NQUERIES
    i = start
    while i < len(sys.argv):
        match sys.argv[i]:
            case "-q":
                if i + 1 >= len(sys.argv):
                    raise Exception("{} option require an argument".format(sys.argv[i]))
                else:
                    try:
                        nqueries = int(sys.argv[i + 1])
                        i = i + 1
                    except Exception:
                        raise Exception("wrong argument for {} option".format(sys.argv[i]))
            case "-f":
                if i + 1 >= len(sys.argv):
                    raise Exception("{} option require an argument".format(sys.argv[i]))
                else:
                    try:
                        first_ttl = int(sys.argv[i + 1])
                        i = i + 1
                    except Exception:
                        raise Exception("wrong argument for {} option".format(sys.argv[i]))
            
            case "-M":
                if i + 1 >= len(sys.argv):
                    raise Exception("{} option require an argument".format(sys.argv[i]))
                else:
                    try:
                        first_ttl = int(sys.argv[i + 1])
                        i = i + 1
                    except Exception:
                        raise Exception("wrong argument for {} option".format(sys.argv[i]))
            case "-m":
                if i + 1 >= len(sys.argv):
                    raise Exception("{} option require an argument".format(sys.argv[i]))
                else:
                    try:
                        max_ttl = int(sys.argv[i + 1])
                        i = i + 1
                    except Exception:
                        raise Exception("wrong argument for {} option".format(sys.argv[i]))
            case _:
                raise Exception("unknow option")
        i = i + 1
    return first_ttl, max_ttl, nqueries

def main():
    host = sys.argv[1]
    try:
        first_ttl, max_ttl, nqueries = get_args(2)
    except Exception as e:
        print("Error:", e.args[0])
        return
    traceroute(host, first_ttl, max_ttl, nqueries, timeout=2)

if __name__ == '__main__':
    main()

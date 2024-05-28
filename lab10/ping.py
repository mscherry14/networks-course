import time
import socket
import struct
import select
import random
import math
import sys

ICMP_ECHO_REQUEST = 8
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


def create_packet(id):
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, id, 1)
    data = 192 * 'Q'
    my_checksum = checksum(header + data.encode())
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0,
                         socket.htons(my_checksum), id, 1)
    return header + data.encode()


def one_ping(dest_addr, timeout=1):
    with socket.socket(socket.AF_INET, socket.SOCK_RAW, ICMP_CODE) as my_socket:
        host = socket.gethostbyname(dest_addr)
        packet_id = int((id(timeout) * random.random()) % 65535)
        packet = create_packet(packet_id)
        while packet:
            sent = my_socket.sendto(packet, (dest_addr, 1))
            packet = packet[sent:]
        delay = receive_ping(my_socket, packet_id, time.time(), timeout)
    return delay


def receive_ping(my_socket, packet_id, time_sent, timeout):
    time_left = timeout
    while True:
        started_select = time.time()
        ready = select.select([my_socket], [], [], time_left)
        how_long_in_select = time.time() - started_select
        if ready[0] == []: # Timeout
            return
        time_received = time.time()
        rec_packet, addr = my_socket.recvfrom(1024)
        icmp_header = rec_packet[20:28]
        type, code, checksum, p_id, sequence = struct.unpack(
            'bbHHh', icmp_header)
        if p_id == packet_id:
            return time_received - time_sent
        time_left -= time_received - time_sent
        if time_left <= 0:
            return


def verbose_ping(dest_addr, timeout=1, count=None):
    delays = []
    sent = received = 0
    print('PING {}'.format(dest_addr))
    if count is None:
        try:
            while True:
                delay = one_ping(dest_addr, timeout)
                if delay == None:
                    sent += 1
                    print('Request timeout for icmp_seq {}'.format(sent))
                else:
                    sent += 1
                    received += 1
                    delay = round(delay * 1000.0, 3)
                    print('Reply from {}: icmp_seq={} time={}ms'.format(dest_addr, sent - 1, delay))
                    delays.append(delay)
                time.sleep(1)
        except KeyboardInterrupt:
            print("", end="")
    elif count > 0:
        try:
            for i in range(count):
                delay = one_ping(dest_addr, timeout)
                if delay == None:
                    sent += 1
                    print('Request timeout for icmp_seq {}'.format(sent))
                else:
                    sent += 1
                    received += 1
                    delay = round(delay * 1000.0, 3)
                    print('Reply from {}: icmp_seq={} time={}ms'.format(dest_addr, sent - 1, delay))
                    delays.append(delay)
                time.sleep(1)
        except KeyboardInterrupt:
            print("", end="")
    else:
        print("ping.py: invalid count of packets to transmit: {}".format(count))
        return
    info = '''--- {dest_addr} ping statistics ---
{sent} packets transmitted, {received} packets received, {loss}% packet loss ({lost} of {sent})
'''.format(
        dest_addr=dest_addr,
        sent=sent,
        received=received,
        lost=sent - received,
        loss=(sent - received) / sent * 100)
    if len(delays) > 0:
        avg = round(sum(delays) / len(delays), 3)
        stddev = round(math.sqrt(sum([(x - avg) ** 2 for x in delays]) / len(delays)), 3)
        info = info + "round-trip min/avg/max/stddev = {minimum}/{avg}/{maximum}/{stddev} ms".format(
        minimum=min(delays),
        maximum=max(delays),
        avg=avg,
        stddev=stddev
    )
    print()
    print(info)

def parse_count(i):
    if i < len(sys.argv):
        if sys.argv[i] == "-c" or sys.argv[i] == "--count":
            if i + 1 >= len(sys.argv):
                print("ping.py: {} option requires an argument".format(sys.argv[i]))
                return -1
            else:
                try:
                    return int(sys.argv[i + 1])
                except Exception:
                    print("ping.py: invalid argument of {} option -- an integer greater than zero is required".format(sys.argv[i]))
    else:
        return None
        
def main():
    if len(sys.argv) < 2:
        print("ping.py: you need to specify the host. try ping.py hostname")
        return
    host = sys.argv[1]
    count = parse_count(2)
    if count == -1:
        return
    verbose_ping(host, count=count)
    
    
if __name__ == "__main__":
    main()

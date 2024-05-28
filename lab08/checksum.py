import struct


def get_checksum(buf: bytes) -> int:
    n = len(buf)
    check = 0
    for i in range(n // 2):
        i1, i2 = 2 * i, min(2 * i + 2, n)
        check += struct.unpack('H', buf[i1:i2])[0]
    return check & 0xFFFF


def check_checksum(buf: bytes, check: int) -> bool:
    return get_checksum(buf) == check


def test():
    s = ['fjlwdfjreofejr', 'dwdqwe3e']
    buf = list(map(str.encode, s))
    check = []
    for i in range(2):
        check.append(get_checksum(buf[i]))
    assert(check_checksum(buf[0], check[0]))
    assert(check_checksum(buf[1], check[1]))
    assert(check[0] != check[1])
    assert(not check_checksum(buf[0], check[1]))
    assert(not check_checksum(buf[1], check[0]))

    print('All tests passed.')


if __name__ == '__main__':
    test()

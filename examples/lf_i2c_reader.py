from smbus2 import SMBus, i2c_msg
from struct import unpack


def read_sensor(bus, address):
    msg = i2c_msg.read(address, 6)
    bus.i2c_rdwr(msg)

    # Convert the read bytes into a tuple of integers. unpack() takes a bytes
    # object and treats the contents as C struct with the format specified in
    # the 2nd argument. "<3H" means to treat the bytes as 3 unsigned short
    # integers (which are 2 bytes long) stored little endian (that is, the
    # least significant byte is first.)
    return unpack(msg.buf, "<3H")


if __name__ == "__main__":
    with SMBus(10) as bus:
        print(read_sensor(bus, 0x58))

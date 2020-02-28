class LuxSensor:
    def __init__(self, bus):
        bus.write_byte_data(0x39, (0x00 | 0x80), 0x03)
        bus.write_byte_data(0x39, (0x01 | 0x80), 0x02) 

    def read(self):
        data = self.bus.read_i2c_block_data(0x39, 0x0C | 0x80, 2)
        data1 = self.bus.read_i2c_block_data(0x39, 0x0E | 0x80, 2)
        ch0 = data[1] * 256 + data[0]
        ch1 = data1[1] * 256 + data1[0]
        return ch0 - ch1

    def calibrate(self, sensitivity):
        visible = []
        for i in range(sensitivity):
            visible.append(read_lux())
        visible = sum(visible)/sensitivity  
        return visible

if __name__ == "__main__":
    target = calibrate(1000)
    offset = 200
    motors = MotorsGroup()
    motors.set(SPEED, SPEED)
    while True:
        lux = read_lux()
        if lux > target + offset or lux < target - offset:
            motors.set(0,0)
            break




    


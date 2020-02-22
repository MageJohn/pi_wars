from smbus2 import SMBus
from lf_i2c_reader import read_sensor

def calibration(sensitivity, bus):
    # in the tuple returned by read_sensor, the first two values correspond
    # to the right hand sensor values. This returns a centre value
    bus = SMBus(bus)
    initial = read_sensor(bus,0x58)[1:3]
    highest = max(initial)
    lowest = min(initial)
    average = 0
    for i in range(sensitivity):
        temp = read_sensor(bus,0x58)[1:3]
        if max(temp) > highest:
            highest = max(temp)
        if min(temp) < lowest:
            lowest = min(temp)
        average += sum(temp)/2
    average /= sensitivity
    deviance = highest - lowest
    low_bound = average - deviance
    up_bound = average + deviance
    bus.close()
    return low_bound,average,up_bound


        
    
if __name__ == "__main__":
    print(calibration(100,7))

from time import sleep

import os

os.system("sudo pigpiod")
import pigpio

pi = pigpio.pi()


class Lidar:
    def __init__(self, pin):
        self.pin = pin
        pi.set_mode(pin, pigpio.INPUT)
        pi.bb_serial_read_open(pin, 115200)

    def get_data(self):
        (count, recv) = pi.bb_serial_read(self.pin)
        if count > 8:
            for i in range(0, count - 9):
                if recv[i] == 89 and recv[i + 1] == 89:  # 0x59 is 89
                    checksum = 0
                    for j in range(0, 8):
                        checksum = checksum + recv[i + j]
                    checksum = checksum % 256
                    if checksum == recv[i + 8]:
                        distance = recv[i + 2] + recv[i + 3] * 256
                        strength = recv[i + 4] + recv[i + 5] * 256
                        if distance <= 1200 and strength < 2000:
                            return distance, strength
                        # else:
                        # raise ValueError('distance error: %d' % distance)
                        # i = i + 9
        return None, None

    def close(self):
        pi.bb_serial_read_close(self.pin)


def lidar_control(que):
    lidars = {"front": Lidar(0), "left": Lidar(0), "bottom": Lidar(0), "right": Lidar(0)}
    while True:
        values = {}
        for key in lidars:
            values[key] = lidars[key].get_data()
        que.put(values)


if __name__ == '__main__':
    lidars = [Lidar(0), Lidar(0), Lidar(0), Lidar(0)]
    try:
        while True:
            for i in range(len(lidars)):
                sleep(0.05)
                distance, strength = lidars[i].get_data()
                print("Lidar" + str(i) + ":", distance, strength, end='\t')
            print("")

    except KeyboardInterrupt:
        print("KeyboardInterrupt yakalandı")

    for lidar in lidars:
        lidar.close()
    pi.stop()

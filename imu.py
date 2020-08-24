import math
import operator
import time
from threading import Thread

import adafruit_lsm9ds1
import board
import busio


def tuple_summer(x, y):
    return tuple(map(operator.add, x, y))


def tuple_divider(t, divisor):
    return map(lambda x: x / divisor, t)


def tuple_multiplier(t, multiplier):
    return map(lambda x: x * multiplier, t)


class Imu:
    def __init__(self, i2c=busio.I2C(board.SCL, board.SDA)):
        self._sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)

        # self._speed = None
        self._degree = None
        self._direction = None

        self._running = False
        self._thread = None

    def start(self):
        if self._running:
            print('IMU is already running')
            return None
        # TODO calibre et
        self._degree = self.get_instant_degree()
        self._direction = (0, 0, 0)
        self._running = True
        self._thread = Thread(target=self._update_values)
        self._thread.start()
        return self

    def stop(self):
        self._running = False
        self._thread.join()

    def _update_values(self):
        last_second_control = time.time()
        last_second_control_count = 0
        loop_time = time.time()
        sum_degree = (0, 0, 0)
        while self._running:
            self._direction = tuple_summer(self._direction,
                                           tuple_multiplier(self._sensor.gyro, time.time() - loop_time))
            loop_time = time.time()

            if time.time() - last_second_control > 1:
                self._degree = tuple_divider(sum_degree, last_second_control_count)
                sum_degree = (0, 0, 0)
                last_second_control_count = 0
                last_second_control = time.time()
            else:
                sum_degree = tuple_summer(sum_degree, self.get_instant_degree())
                last_second_control_count += 1

    def get_instant_acceleration(self):
        return self._sensor.acceleration

    def get_instant_magnetic(self):
        return self._sensor.magnetic

    def get_instant_gyro(self):
        return self._sensor.gyro

    def get_temperature(self):
        return self._sensor.temperature

    def get_instant_degree(self):
        acc_x, acc_y, acc_z = self._sensor.acceleration
        acc_magnitude = math.sqrt(acc_x ** 2 + acc_y ** 2 + acc_z ** 2)

        if acc_magnitude is not 0:
            unit_acc_x = acc_x / acc_magnitude
            unit_acc_y = acc_y / acc_magnitude
            unit_acc_z = acc_z / acc_magnitude
            degree_x = math.atan2((-unit_acc_x), math.sqrt(unit_acc_y ** 2 + unit_acc_z ** 2)) * 180 / math.pi
            degree_y = math.atan2((-unit_acc_y), math.sqrt(unit_acc_x ** 2 + unit_acc_z ** 2)) * 180 / math.pi
            degree_z = math.atan2((-unit_acc_y), math.sqrt(unit_acc_x ** 2 + unit_acc_z ** 2)) * 180 / math.pi
        else:
            degree_x, degree_y, degree_z = 0, 0, 0
        return degree_x, degree_y, degree_z

    def get_degree(self):
        return self._degree

    def get_direction(self, absolute=True):
        if absolute:
            return map(lambda x: x % 360, self._direction)
        return self._direction


if __name__ == '__main__':
    imu = Imu()
    for i in range(10):
        print("Degree:", imu.get_degree())
        print("Direction:", imu.get_direction())
        time.sleep(0.1)

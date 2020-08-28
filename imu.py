import math
import operator
import time
from datetime import datetime
from threading import Thread

import adafruit_lsm9ds1
import board
import busio


def list_summer(x, y):
    return [i + j for i, j in zip(x, y)]


def list_subtructor(x, y):
    return [i - j for i, j in zip(x, y)]


def list_divider(l, divisor):
    return [i / divisor for i in l]


def list_multiplier(l, multiplier):
    return [i * multiplier for i in l]


def list_rounder(l, r=2):
    return [round(i, r) for i in l]


def tuple_summer(x, y):
    return tuple(map(operator.add, x, y))


def tuple_divider(t, divisor):
    return tuple(map(lambda x: x / divisor, t))


def tuple_multiplier(t, multiplier):
    return tuple(map(lambda x: x * multiplier, t))


def tuple_subtructor(x, y):
    # return x-y
    return tuple(map(operator.sub, x, y))


def round_tuple(t, r=2):
    return tuple(map(lambda x: round(x, r), t))


class Imu:
    def __init__(self, i2c=busio.I2C(board.SCL, board.SDA)):
        # i2c = busio.I2C(board.SCL, board.SDA)
        self._sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)

        # self._speed = None
        self._degree = None
        self._init_degree = None
        self._direction = None
        self._init_gyro = None

        self._running = False
        self._thread = None

    def calibrate(self, seconds=1):
        seconds_control = time.time()
        seconds_control_count = 0
        sum_degree = [0, 0, 0]
        sum_gyro = [0, 0, 0]
        while time.time() - seconds_control < seconds:
            sum_degree = list_summer(sum_degree, self.get_instant_degree())
            sum_gyro = list_summer(sum_gyro, self.get_instant_gyro())
            seconds_control_count += 1
            print("Sum degree:", sum_degree)
            print("Instant degree:", self.get_instant_degree())
            print(self.get_instant_gyro())

        self._init_degree = list_divider(sum_degree, seconds_control_count)
        self._init_gyro = list_divider(sum_gyro, seconds_control_count)
        print("--------------------------------------------------------")
        print("init degree:", self._init_degree)
        print("init gyro", self._init_gyro)
        print("--------------------------------------------------------")

    def start(self):
        if self._running:
            print('IMU is already running')
            return None
        self._degree = self.get_instant_degree()
        self._direction = [0, 0, 0]
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
        sum_degree = [0, 0, 0]
        while self._running:
            self._direction = list_summer(
                self._direction, list_multiplier(self.get_instant_gyro(), time.time() - loop_time)
            )
            loop_time = time.time()

            if time.time() - last_second_control > 0.1:
                self._degree = list_divider(sum_degree, last_second_control_count)
                sum_degree = [0, 0, 0]
                last_second_control_count = 0
                last_second_control = time.time()
            else:
                sum_degree = list_summer(sum_degree, self.get_instant_degree())
                last_second_control_count += 1

    def get_instant_acceleration(self):
        return self._sensor.acceleration

    def get_instant_magnetic(self):
        # mag_x = magReadX * cos(pitch) + magReadY * sin(roll) * sin(pitch) + magReadZ * cos(roll) * sin(pitch)
        # mag_y = magReadY * cos(roll) - magReadZ * sin(roll)
        # yaw = 180 * atan2(-mag_y, mag_x) / M_PI;
        return self._sensor.magnetic

    def get_instant_gyro(self):
        if self._init_gyro:
            return list_subtructor(self._sensor.gyro, self._init_gyro)
        return self._sensor.gyro

    def get_temperature(self):
        return self._sensor.temperature

    def get_instant_degree(self):
        acc_x, acc_y, acc_z = self._sensor.acceleration
        acc_magnitude = math.sqrt(acc_x ** 2 + acc_y ** 2 + acc_z ** 2)
        degree = [0, 0, 0]
        if acc_magnitude is not 0:
            unit_acc_x = acc_x / acc_magnitude
            unit_acc_y = acc_y / acc_magnitude
            unit_acc_z = acc_z / acc_magnitude
            degree[0] = math.atan2(unit_acc_x, math.sqrt(unit_acc_y ** 2 + unit_acc_z ** 2)) * 180 / math.pi  # PITCH
            degree[1] = math.atan2(unit_acc_y, math.sqrt(unit_acc_x ** 2 + unit_acc_z ** 2)) * 180 / math.pi  # ROLL
            degree[2] = math.atan2(unit_acc_z, math.sqrt(unit_acc_x ** 2 + unit_acc_y ** 2)) * 180 / math.pi

        if self._init_degree:
            return list_subtructor(degree, self._init_degree)
        return degree

    def get_degree(self):
        return list_rounder(self._degree)

    def get_direction(self, absolute=True):
        # if absolute:
        #    return round_tuple(tuple_subtructor(map(lambda x: x % 360, self._direction), self._init_direction))
        # return round_tuple(tuple_subtructor(self._direction, self._init_direction))
        if absolute:
            return list_rounder([i % 360 for i in self._direction])
        return round_tuple(self._direction)

    # def get_yaw_mag(self):
    #     mag_read_x, mag_read_y, mag_read_z = self.get_instant_magnetic()
    #     pitch, roll, _ = self.get_instant_degree()
    #     mag_x = mag_read_x * math.cos(pitch) + mag_read_y * math.sin(roll) * math.sin(pitch) + mag_read_z * math.cos(
    #         roll) * math.sin(pitch)
    #     mag_y = mag_read_y * math.cos(roll) - mag_read_z * math.sin(roll)
    #     yaw = 180 * math.atan2(-mag_y, mag_x) / math.pi
    #     return yaw


if __name__ == '__main__':
    print("Create imu...")
    imu = Imu()
    print("Calibration...")
    imu.calibrate(5)
    print("Start...")
    imu.start()
    t = datetime.now()
    try:
        print("qqq")
        while True:
            print("Degree:", imu.get_degree())
            print("Direction:", imu.get_direction(absolute=False))
            # print("Mag:", *imu._sensor.magnetic)
            # print("Yaw:", imu.get_yaw_mag())
            print("Time:", datetime.now() - t)
            print()
            time.sleep(0.1)
    except KeyboardInterrupt:
        imu.stop()
    finally:
        imu.stop()

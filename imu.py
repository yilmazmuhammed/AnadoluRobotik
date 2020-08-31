import math
import time
from datetime import datetime
from threading import Thread

import adafruit_lsm9ds1
import board
import busio


class XYZ:
    def __init__(self, x=0, y=0, z=0):
        self.x, self.y, self.z = x, y, z

    def __add__(self, other):
        return XYZ(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return XYZ(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, multiplier):
        return XYZ(self.x * multiplier, self.y * multiplier, self.z * multiplier)

    def __truediv__(self, divider):
        return XYZ(self.x / divider, self.y / divider, self.z / divider)

    def __mod__(self, other):
        return XYZ(self.x % other, self.y % other, self.z % other)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    def __imul__(self, multiplier):
        self.x *= multiplier
        self.y *= multiplier
        self.z *= multiplier
        return self

    def __idiv__(self, divider):
        self.x *= divider
        self.y *= divider
        self.z *= divider
        return self

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y and self.z == other.z:
            return True
        return False

    def __neg__(self):
        return XYZ(-self.x, -self.y, -self.z)

    def __str__(self):
        return str((self.x, self.y, self.z))

    def __repr__(self):
        return self.x, self.y, self.z

    def get(self):
        return round(self.x, 2), round(self.y, 2), round(self.z, 2)


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
        sum_degree = XYZ()
        sum_gyro = XYZ()
        while time.time() - seconds_control < seconds:
            sum_degree += self.get_instant_degree()
            sum_gyro += self.get_instant_gyro()
            seconds_control_count += 1

        self._init_degree = sum_degree / seconds_control_count
        self._init_gyro = sum_gyro / seconds_control_count
        print("--------------------------------------------------------")
        print("init degree:", self._init_degree)
        print("init gyro", self._init_gyro)
        print("--------------------------------------------------------")

    def start(self):
        if self._running:
            print('IMU is already running')
            return None
        self._degree = self.get_instant_degree()
        self._direction = XYZ()
        self._running = True
        self._thread = Thread(target=self._update_values)
        self._thread.start()
        return self

    def stop(self):
        if self._running:
            print("IMU is stopping...")
            self._running = False
            self._thread.join()
            print("IMU has been stopped.")
        else:
            print("IMU is already stopped.")

    def _update_values(self):
        last_second_control = time.time()
        last_second_control_count = 0
        loop_time = time.time()
        sum_degree = XYZ()
        while self._running:
            # Calculate direction from gyro
            self._direction += self.get_instant_gyro() * (time.time() - loop_time)
            loop_time = time.time()

            # Calculate degree from acceleration
            sum_degree += self.get_instant_degree()
            last_second_control_count += 1
            if time.time() - last_second_control > 0.1:
                self._degree = sum_degree / last_second_control_count
                sum_degree = XYZ()
                last_second_control_count = 0
                last_second_control = time.time()

    def get_instant_acceleration(self):
        return XYZ(*self._sensor.acceleration)

    def get_instant_magnetic(self):
        # mag_x = magReadX * cos(pitch) + magReadY * sin(roll) * sin(pitch) + magReadZ * cos(roll) * sin(pitch)
        # mag_y = magReadY * cos(roll) - magReadZ * sin(roll)
        # yaw = 180 * atan2(-mag_y, mag_x) / M_PI;
        return XYZ(*self._sensor.magnetic)

    def get_instant_gyro(self):
        if self._init_gyro:
            return XYZ(*self._sensor.gyro) - self._init_gyro
        return XYZ(*self._sensor.gyro)

    def get_temperature(self):
        return XYZ(*self._sensor.temperature)

    def get_instant_degree(self):
        acc_x, acc_y, acc_z = self._sensor.acceleration
        acc_magnitude = math.sqrt(acc_x ** 2 + acc_y ** 2 + acc_z ** 2)
        degree = XYZ()
        if acc_magnitude is not 0:
            unit_acc_x = acc_x / acc_magnitude
            unit_acc_y = acc_y / acc_magnitude
            unit_acc_z = acc_z / acc_magnitude
            degree.x = math.atan2(unit_acc_x, math.sqrt(unit_acc_y ** 2 + unit_acc_z ** 2)) * 180 / math.pi  # PITCH
            degree.y = math.atan2(unit_acc_y, math.sqrt(unit_acc_x ** 2 + unit_acc_z ** 2)) * 180 / math.pi  # ROLL
            degree.z = math.atan2(unit_acc_z, math.sqrt(unit_acc_x ** 2 + unit_acc_y ** 2)) * 180 / math.pi

        if self._init_degree:
            return degree - self._init_degree
        return degree

    def get_degree(self):
        return self._degree

    def get_direction(self, absolute=True):
        # if absolute:
        #    return round_tuple(tuple_subtructor(map(lambda x: x % 360, self._direction), self._init_direction))
        # return round_tuple(tuple_subtructor(self._direction, self._init_direction))
        if absolute:
            return self._direction % 360
        return self._direction


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
            print("Time:", datetime.now() - t)
            print()
            time.sleep(0.1)
    except KeyboardInterrupt:
        imu.stop()
    finally:
        imu.stop()

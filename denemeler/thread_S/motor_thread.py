import json
import math
from threading import Thread, Lock
from time import sleep


class NotInCorrectRange(Exception):
    pass


class Control:
    def __init__(self, pin):
        self.pin = pin
        self.throttle = None
        self.min_freq = None
        self.max_freq = None

    def set_pulse_width_range(self, min_freq, max_freq):
        self.min_freq = min_freq
        self.max_freq = max_freq


class ContinuousRotationServo:
    max_freq = 1900
    min_freq = 1100
    middle_point = (max_freq + min_freq) / 2
    power_multiplier = ((max_freq - min_freq) / 2) / 100

    def __init__(self, pin):
        self.control = None
        self.pin = abs(int(pin))
        self.pervane = -1 if pin[0] == "-" else 1
        self.motor_initialize()

        self.running = True
        self.power = 0
        self.lock = Lock()
        self.thread = Thread(target=self.motor_thread)
        self.thread.start()

    def motor_thread(self):
        slp = 0.01
        prev_power = 0
        control = self.control
        while self.running:
            self.lock.acquire()
            current_power = self.power
            print("Pin:", self.pin, "current_power:", current_power, "prev_power:", prev_power)
            if prev_power == current_power:
                continue
            else:
                if current_power - prev_power > 5:
                    for i in range(prev_power + 1, current_power + 1, 5):
                        control.throttle = i / 100
                        sleep(slp)
                elif prev_power - current_power > 5:
                    for i in range(prev_power - 1, current_power - 1, -5):
                        control.throttle = i / 100
                        sleep(slp)
                control.throttle = self.force_to_throttle(current_power * self.pervane)
                prev_power = current_power
        self.power = 0

    @staticmethod
    def force_to_throttle(power):
        with open('../../t200.json', 'r') as j:
            sozluk = json.load(j)

        if sozluk.get(str(power)):
            return (sozluk.get(str(power)) - 1500) / 400 + 0

        p_key = None
        l_key = None
        # sozluk.keys() küçükten büyüğe sıralı olmalı
        for key in sozluk.keys():
            key = int(key)
            if power > key:
                p_key = key
            else:
                l_key = key
                break

        p_value = sozluk.get(str(p_key))
        l_value = sozluk.get(str(l_key))
        o_value = (l_value - p_value) / (int(l_key) - int(p_key)) * (power - p_key) + p_value
        return (o_value - 1500) / 400 + 0

    def motor_initialize(self):
        self.control = Control(self.pin)
        self.control.set_pulse_width_range(1135, 1935)

    def _change_power(self, power):
        """
        :param power: this parameter takes a value between -100 and 100. Negative values​make it work backward,
                      positive values​make it work forward.
        :return:
        """
        if power != self.power:
            self.power = power
            if self.lock.locked():
                self.lock.release()

    def run_clockwise(self, power):
        """
        Suyu geriye ittirir. Motor ileriye doğru hareket etmek ister.
        :param power:
        :return:
        """
        if not 0 <= power <= 100:
            raise NotInCorrectRange("Power must be between 0 and 100.")
        return self._change_power(power)

    def run_counterclockwise(self, power):
        """
        Suyu ileriye ittirir. Motor geriye doğru hareket etmek ister.
        :param power:
        :return:
        """
        if not 0 <= power <= 100:
            raise NotInCorrectRange("Power must be between 0 and 100.")
        return self._change_power(-power)

    def run_bidirectional(self, power):
        if power >= 0:
            self.run_clockwise(power)
        else:
            self.run_counterclockwise(-power)

    def stop(self):
        print(self.pin, "motor stop...")
        if self.running:
            print(self.pin, "motor kapatılıyor...")
            self.running = False
            self.power = 0
            if self.lock.locked():
                self.lock.release()
            self.thread.join()
            print(self.pin, "motor kapatıldı...")


class RovMovement:
    def __init__(self, xy_lf_pin, xy_rf_pin, xy_lb_pin, xy_rb_pin, z_lf_pin, z_rf_pin, z_lb_pin, z_rb_pin, arm_pin,
                 initialize_motors=True):
        self.xy_lf = ContinuousRotationServo(xy_lf_pin)
        self.xy_rf = ContinuousRotationServo(xy_rf_pin)
        self.xy_lb = ContinuousRotationServo(xy_lb_pin)
        self.xy_rb = ContinuousRotationServo(xy_rb_pin)
        self.z_lf = ContinuousRotationServo(z_lf_pin)
        self.z_rf = ContinuousRotationServo(z_rf_pin)
        self.z_lb = ContinuousRotationServo(z_lb_pin)
        self.z_rb = ContinuousRotationServo(z_rb_pin)
        # self.arm = StandardServo(arm_pin)
        self.z_motors_list = [self.z_lf, self.z_rf, self.z_lb, self.z_rb]
        self.xy_motors_list = [self.xy_lf, self.xy_rf, self.xy_lb, self.xy_rb]
        self.all_motors_list = self.z_motors_list + self.xy_motors_list
        self.arm_status = False
        self.open_arm()
        if initialize_motors:
            self._initialize_motors()
        sleep(2)

    def _initialize_motors(self):
        print("All motors initializing...")
        mp = 30
        for i in list(range(0, mp)) + list(range(mp, -mp, -1)) + list(range(-mp, 1)):
            print("Power:", i)
            for motor in self.all_motors_list:
                motor.run_bidirectional(i)
            sleep(0.01)
        print("All motors initialized...")

    def go_up(self, power):
        power_per_motor = int(power / 4)
        for motor in self.z_motors_list:
            motor.run_clockwise(power_per_motor)

    def go_down(self, power):
        power_per_motor = int(power / 4)
        for motor in self.z_motors_list:
            motor.run_counterclockwise(power_per_motor)

    def turn_left(self, power):
        power = power / 4
        power_per_motor = int(power / 4)
        self.xy_rf.run_clockwise(power_per_motor)
        self.xy_lf.run_counterclockwise(power_per_motor)
        self.xy_lb.run_clockwise(power_per_motor)
        self.xy_rb.run_counterclockwise(power_per_motor)

    def turn_right(self, power):
        power = power / 4
        power_per_motor = int(power / 4)
        self.xy_rf.run_counterclockwise(power_per_motor)
        self.xy_lf.run_clockwise(power_per_motor)
        self.xy_lb.run_counterclockwise(power_per_motor)
        self.xy_rb.run_clockwise(power_per_motor)

    def go_xy(self, power, degree):
        """
        :param power: Power sent to the vehicle's movement
        :param degree: degree of movement (0between 0-360 degree)
                       0 -> ileri
                       90 -> sağa
                       180 -> geri
                       270 -> sola
        :return:
        """
        power_per_motor = int(power / 2)

        radian_rf = (45 - degree) / 180 * math.pi
        radian_lf = (135 - degree) / 180 * math.pi
        radian_lb = (225 - degree) / 180 * math.pi
        radian_rb = (315 - degree) / 180 * math.pi

        pow_rf = int(math.sin(radian_rf) * power_per_motor)
        pow_lf = int(math.sin(radian_lf) * power_per_motor)
        pow_lb = int(math.sin(radian_lb) * power_per_motor)
        pow_rb = int(math.sin(radian_rb) * power_per_motor)

        self.xy_rf.run_bidirectional(pow_rf)
        self.xy_lf.run_bidirectional(pow_lf)
        self.xy_lb.run_bidirectional(pow_lb)
        self.xy_rb.run_bidirectional(pow_rb)

    def go_xy_and_turn(self, power, degree, turn_power):
        """
        :param power: Power sent to the vehicle's movement
        :param degree: degree of movement (0between 0-360 degree)
                       0 -> ileri
                       90 -> sağa
                       180 -> geri
                       270 -> sola
        :param turn_power: Turn power
                           Positive value -> Turn right
                           Negative value -> Turn left
        :return:
        """
        turn_power = turn_power / 4
        turn_power_per_motor = int(turn_power / 4)
        go_power_per_motor = int(power / 2)

        radian_rf = (45 - degree) / 180 * math.pi
        radian_lf = (135 - degree) / 180 * math.pi
        radian_lb = (225 - degree) / 180 * math.pi
        radian_rb = (315 - degree) / 180 * math.pi

        pow_rf = int(math.sin(radian_rf) * go_power_per_motor - turn_power_per_motor)
        pow_lf = int(math.sin(radian_lf) * go_power_per_motor + turn_power_per_motor)
        pow_lb = int(math.sin(radian_lb) * go_power_per_motor - turn_power_per_motor)
        pow_rb = int(math.sin(radian_rb) * go_power_per_motor + turn_power_per_motor)

        self.xy_rf.run_bidirectional(pow_rf)
        self.xy_lf.run_bidirectional(pow_lf)
        self.xy_lb.run_bidirectional(pow_lb)
        self.xy_rb.run_bidirectional(pow_rb)

    def open_arm(self):
        # self.arm.change_angle(180)
        self.arm_status = True

    def close_arm(self):
        # self.arm.change_angle(0)
        self.arm_status = False

    def toggle_arm(self, arm_status=None):
        if self.arm_status and (arm_status is None or arm_status == False):
            self.close_arm()
        elif not self.arm_status and (arm_status is None or arm_status == True):
            self.open_arm()

    def run_all_motors_cw(self, power):
        for motor in self.all_motors_list:
            motor.run_clockwise(power)

    def run_all_motors_ccw(self, power):
        for motor in self.all_motors_list:
            motor.run_counterclockwise(power)

    def stop(self):
        for motor in self.all_motors_list:
            motor.stop()
        # self.arm.stop()

    def close(self):
        self.stop()


if __name__ == '__main__':
    rov_movement = RovMovement(xy_lf_pin="-2", xy_rf_pin="0", xy_lb_pin="-1", xy_rb_pin="6",
                               z_lf_pin="-5", z_rf_pin="3", z_lb_pin="-7", z_rb_pin="4", arm_pin=8,
                               initialize_motors=True
                               )
    rov_movement.stop()

import json
import math
from threading import Thread, Lock
from time import sleep
from adafruit_servokit import ServoKit

from imu import Imu

kit = ServoKit(channels=16)


class NotInCorrectRange(Exception):
    pass


class NotCorrectType(Exception):
    pass


class ContinuousRotationServo:
    def __init__(self, pin, min_freq=1135, max_freq=1935, ssc_control=True, p2t=None):
        self.control = None
        self.pin = abs(int(pin))
        self.propeller_direction = -1 if pin[0] == "-" else 1
        self.min_freq = min_freq
        self.max_freq = max_freq
        self.ssc_control = ssc_control
        self.p2t = p2t

        self.motor_initialize()

        self.running = True
        self.power = 0
        self.lock = Lock()
        self.thread = Thread(target=self.motor_thread)
        self.thread.start()

    def motor_thread(self):
        # Sudden speed change control
        ssc_sleep = 0.01
        ssc_step = 5
        prev_power = 0
        while self.running:
            self.lock.acquire()
            current_power = self.power
            if prev_power == current_power:
                continue
            else:
                if self.ssc_control:
                    dif = current_power - prev_power
                    if abs(dif) > ssc_step:
                        sign = int(dif / abs(dif))
                        for cp in range(prev_power + sign * ssc_step, current_power + sign, sign * ssc_step):
                            self._control_change_throttle(cp)
                            sleep(ssc_sleep)
                    # if current_power - prev_power > ssc_step:
                    #     for i in range(prev_power + 1, current_power + 1, ssc_step):
                    #         self._control_change_throttle(i)
                    #         # self.control.throttle = i / 100
                    #         sleep(ssc_sleep)
                    # elif prev_power - current_power > ssc_step:
                    #     for i in range(prev_power - 1, current_power - 1, -ssc_step):
                    #         self._control_change_throttle(i)
                    #         # self.control.throttle = i / 100
                    #         sleep(ssc_sleep)
                self._control_change_throttle(current_power)
                # self.control.throttle = self.power_to_throttle(current_power * self.propeller_direction)
                prev_power = current_power
        self._control_change_throttle(0)

    def _control_change_throttle(self, power):
        if self.p2t:
            self.control.throttle = self.power_to_throttle(power * self.propeller_direction)
        else:
            self.control.throttle = power / 100

    def power_to_throttle(self, power):
        if not -100 <= power <= 100:
            raise NotInCorrectRange("Power must be between -100 and 100.")

        return self.p2t[str(power)]

    def motor_initialize(self):
        self.control = kit.continuous_servo[self.pin]
        self.control.set_pulse_width_range(self.min_freq, self.max_freq)

    def _change_power(self, power, range_control=True, type_control=True):
        """
        :param power: this parameter takes a value between -100 and 100. Negative values​make it work backward,
                      positive values​make it work forward.
        :return:
        """
        if range_control and not -100 <= power <= 100:
            raise NotInCorrectRange("Power must be between -100 and 100 in run_bidirectional function. Power:", power)
        if type_control and not isinstance(power, int):
            raise NotCorrectType("Power must be integer. Power:", power)

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
            raise NotInCorrectRange("Power must be between 0 and 100. Power:", power)
        return self._change_power(power)

    def run_counterclockwise(self, power):
        """
        Suyu ileriye ittirir. Motor geriye doğru hareket etmek ister.
        :param power:
        :return:
        """
        if not 0 <= power <= 100:
            raise NotInCorrectRange("Power must be between 0 and 100. Power:", power)
        return self._change_power(-power)

    def run_bidirectional(self, power):
        if not -100 <= power <= 100:
            raise NotInCorrectRange("Power must be between -100 and 100 in run_bidirectional function. Power:", power)

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


class StandardServo:
    max_degree = 180
    min_freq = 1100
    max_freq = 1900

    def __init__(self, pin):
        self.control = None
        self.pin = pin
        self._motor_initialize()

        self.running = False
        self.angle = None
        self.write_lock = Lock()
        self.write_thread = None
        self.start()

    def _motor_initialize(self):
        self.control = kit.servo[self.pin]
        # self.control.actuation_range = self.max_degree
        # self.control.set_pulse_width_range(self.min_freq, self.max_freq)
        # self.change_angle(0)

    def start(self):
        if self.running:
            print('Motor is already running')
            return None
        else:
            self.running = True
            self.angle = 0
            self.write_thread = Thread(target=self._motor_thread)
            self.write_thread.start()
            return self

    def _motor_thread(self):
        while self.running:
            self.write_lock.acquire()
            self.control.angle = self.angle

    def change_angle(self, angle):
        if angle != self.angle:
            self.angle = angle
            if self.write_lock.locked():
                self.write_lock.release()

    def stop(self):
        print(self.pin, "motor is shutting down...")
        if self.running:
            self.running = False
            if self.write_lock.locked():
                self.write_lock.release()
            self.write_thread.join()
            print(self.pin, "motor is shut down...")
        else:
            print(self.pin, "motor is already shut down...")


def sign_n(num):
    if num == 0:
        return 1
    return num / abs(num)


class RovMovement:
    def __init__(self, xy_lf_pin, xy_rf_pin, xy_lb_pin, xy_rb_pin, z_lf_pin, z_rf_pin, z_lb_pin, z_rb_pin, arm_pin,
                 initialize_motors=True, ssc_control=True):
        with open('p2t.json', 'r') as json_file:
            p2t = json.load(json_file)
        self.xy_lf = ContinuousRotationServo(xy_lf_pin, ssc_control=ssc_control, p2t=p2t)
        self.xy_rf = ContinuousRotationServo(xy_rf_pin, ssc_control=ssc_control, p2t=p2t)
        self.xy_lb = ContinuousRotationServo(xy_lb_pin, ssc_control=ssc_control, p2t=p2t)
        self.xy_rb = ContinuousRotationServo(xy_rb_pin, ssc_control=ssc_control, p2t=p2t)
        self.z_lf = ContinuousRotationServo(z_lf_pin, ssc_control=ssc_control, p2t=p2t)
        self.z_rf = ContinuousRotationServo(z_rf_pin, ssc_control=ssc_control, p2t=p2t)
        self.z_lb = ContinuousRotationServo(z_lb_pin, ssc_control=ssc_control, p2t=p2t)
        self.z_rb = ContinuousRotationServo(z_rb_pin, ssc_control=ssc_control, p2t=p2t)
        self.arm = StandardServo(arm_pin)
        self.imu = Imu()
        self.z_motors_list = [self.z_lf, self.z_rf, self.z_lb, self.z_rb]
        self.xy_motors_list = [self.xy_lf, self.xy_rf, self.xy_lb, self.xy_rb]
        self.all_motors_list = self.z_motors_list + self.xy_motors_list
        self.arm_status = False
        self.open_arm()

        self.imu.start()
        if initialize_motors:
            self.initialize_motors()
            self._initialize_imu()
        sleep(2)

    def initialize_motors(self, mp=30):
        print("All motors initializing...")
        for cp in list(range(0, mp)) + list(range(mp, -mp, -1)) + list(range(-mp, 1)):
            print("Power:", cp)
            for motor in self.all_motors_list:
                motor.run_bidirectional(cp)
            sleep(0.01)
        print("All motors initialized...")

    def _initialize_imu(self, seconds=5):
        print("IMU is being calibrated...")
        self.imu.calibrate(seconds)
        print("IMU is calibrated...")

    def _get_z_balance_p(self, kp=1.0, type_=int):
        try:
            x, y, _ = self.imu.get_degree().get()
            comp_sign = +1 if (x < 0 and y < 0) or (x > 0 and y > 0) else -1
            lf_p = sign_n(-y - x) * math.sqrt(abs(-y * -y + comp_sign * -x * -x))  # -y - x
            rf_p = sign_n(-y + x) * math.sqrt(abs(-y * -y - comp_sign * +x * +x))  # -y + x
            lb_p = sign_n(+y - x) * math.sqrt(abs(+y * +y - comp_sign * -x * -x))  # +y - x
            rb_p = sign_n(+y + x) * math.sqrt(abs(+y * +y + comp_sign * +x * +x))  # +y + x
            return type_(lf_p * kp), type_(rf_p * kp), type_(lb_p * kp), type_(rb_p * kp)
        except Exception as e:
            print("Exception in _get_balance_p:", e)
            return 0, 0, 0, 0

    def go_z_bidirectional(self, power, with_balance=True):
        power_per_motor = int(power / 4)

        lf_p, rf_p, lb_p, rb_p = self._get_z_balance_p(kp=1 / 9) if with_balance else 0, 0, 0, 0
        self.z_lf.run_bidirectional(power_per_motor + int(lf_p))
        self.z_rf.run_bidirectional(power_per_motor + int(rf_p))
        self.z_lb.run_bidirectional(power_per_motor + int(lb_p))
        self.z_rb.run_bidirectional(power_per_motor + int(rb_p))

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
        self.arm.change_angle(100)
        self.arm_status = True

    def close_arm(self):
        self.arm.change_angle(30)
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
        print("RovMovement is terminating...")
        for motor in self.all_motors_list:
            motor.stop()
        self.arm.stop()
        self.imu.stop()
        print("RovMovement has been terminated.")

    def close(self):
        self.stop()


if __name__ == '__main__':
    try:
        for i in range(0, 8):
            print("pin:", i)
            m = ContinuousRotationServo(str(i))
            for j in range(30):
                print("power:", j)
                m.run_bidirectional(j)
                sleep(0.1)
            for j in range(30, -30, -1):
                print("power:", j)
                m.run_bidirectional(j)
                sleep(0.1)
            for j in range(-30, 1):
                print("power:", j)
                m.run_bidirectional(j)
                sleep(0.1)
            m.stop()
            sleep(2)
    except KeyboardInterrupt:
        print("KeyboardInterrupt yakalandı")

    # rov_movement = RovMovement(xy_lf_pin=0, xy_rf_pin=1, xy_lb_pin=2, xy_rb_pin=3,
    #                            z_lf_pin=4, z_rf_pin=5, z_lb_pin=6, z_rb_pin=7, arm_pin=8)
    # try:
    #     import getch
    #
    #     power = 0
    #     char = "w"
    #     while True:
    #         previous = char
    #         char = getch.getch()
    #         if previous != char:
    #             rov_movement.stop()
    #
    #         if char == "a":
    #             print("Hareket: sola git", "\tGüç:", power)
    #             rov_movement.go_xy(power, 270)
    #         elif char == "s":
    #             print("Hareket: geri git", "\tGüç:", power)
    #             rov_movement.go_xy(power, 180)
    #         elif char == "d":
    #             print("Hareket: sağa git", "\tGüç:", power)
    #             rov_movement.go_xy(power, 90)
    #         elif char == "w":
    #             print("Hareket: ileri git", "\tGüç:", power)
    #             rov_movement.go_xy(power, 0)
    #         elif char == "y":
    #             print("Hareket: yüksel", "\tGüç:", power)
    #             rov_movement.go_up(power)
    #         elif char == "u":
    #             print("Hareket: alçal", "\tGüç:", power)
    #             rov_movement.go_down(power)
    #         elif char == "q":
    #             print("Hareket: sola dön", "\tGüç:", power)
    #             rov_movement.turn_left(power)
    #         elif char == "e":
    #             print("Hareket: sağa dön", "\tGüç:", power)
    #             rov_movement.turn_right(power)
    #         elif char == "j":
    #             print("Hareket: güçü arttır", "\tGüç:", power)
    #             if power <= 90:
    #                 power += 10
    #         elif char == "k":
    #             print("Hareket: güçü azalt", "\tGüç:", power)
    #             if power >= 10:
    #                 power -= 10
    #         else:
    #             rov_movement.stop()
    #             print("Tanımsız karaktere basıldı")
    # except KeyboardInterrupt:
    #     print("KeyboardInterrupt yakalandı")
    # finally:
    #     rov_movement.close()

    # try:
    #     secenek = input("1: Saat yönünün tersine son hızdan, saat yönünde son hıza\n"
    #                     "2: Elle güç gir\n"
    #                     "3: Arttır/Azalt\n"
    #                     "\nİstediğiniz seçeneği seçiniz: ")
    #     if secenek == '1':
    #         for pow in range(100, -1, -1):
    #             print("pow:", pow)
    #             rov_movement.run_all_motors_ccw(pow)
    #             sleep(0.5)
    #         for pow in range(101):
    #             print("pow:", pow)
    #             rov_movement.run_all_motors_cw(pow)
    #             sleep(0.5)
    #     elif secenek == '2':
    #         print("Motor yönünü değiştirmek için '+' veya '-' giriniz\n"
    #               "Kapatmak için 'c' giriniz\n"
    #               "Motorun çalışmasını istediğiniz gücü 0-100 aralığında giriniz\n")
    #         yon = "+"
    #         pow = 0
    #         while True:
    #             if yon == "+":
    #                 print("pow:", pow)
    #                 rov_movement.run_all_motors_cw(pow)
    #             elif yon == "-":
    #                 print("pow:", pow)
    #                 rov_movement.run_all_motors_ccw(pow)
    #             deger = input()
    #             if deger == "+":
    #                 yon = "+"
    #             elif deger == "-":
    #                 yon = "-"
    #             elif deger.isnumeric():
    #                 pow = int(deger)
    #             elif deger == "c":
    #                 break
    #             else:
    #                 print("Your input is '" + deger + "'. Please enter valid input.")
    #                 print("Motor yönünü değiştirmek için '+' veya '-' giriniz\n"
    #                       "Kapatmak için 'c' giriniz\n"
    #                       "Motorun çalışmasını istediğiniz gücü 0-100 aralığında giriniz\n")
    #     elif secenek == '3':
    #         print("Motor hızını değiştirmek için 'a' veya 'd' giriniz\n"
    #               "Kapatmak için 'c' giriniz\n")
    #         pow = 0
    #         while True:
    #             if pow >= 0:
    #                 print("pow:", pow)
    #                 rov_movement.run_all_motors_cw(pow)
    #             else:
    #                 print("pow:", pow)
    #                 rov_movement.run_all_motors_ccw(-pow)
    #
    #             deger = input()
    #             if deger == "a":
    #                 if pow <= 100:
    #                     pow += 10
    #             elif deger == "d":
    #                 if pow >= -100:
    #                     pow -= 10
    #             elif deger == "c":
    #                 break
    #             else:
    #                 print("Your input is '" + deger + "'. Please enter valid input.")
    #                 print("Motor hızını değiştirmek için 'a' veya 'd' giriniz\n"
    #                       "Kapatmak için 'c' giriniz\n")
    #     else:
    #         print("Your input is '" + secenek + "'. Please enter valid input.")
    # except KeyboardInterrupt:
    #     print("KeyboardInterrupt yakalandı")

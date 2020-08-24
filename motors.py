import json
import math
from threading import Thread, Lock
from time import sleep
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)
p2t = {}


class NotInCorrectRange(Exception):
    pass


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
                control.throttle = self.power_to_throttle(current_power * self.pervane)
                prev_power = current_power
        self.power = 0

    @staticmethod
    def power_to_throttle(power):
        if not -100 <= power <= 100:
            raise NotInCorrectRange("Power must be between -100 and 100.")

        global p2t
        if not p2t:
            with open('p2t.json', 'r') as j:
                p2t = json.load(j)
        return p2t[power]

    def motor_initialize(self):
        self.control = kit.continuous_servo[self.pin]
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
        self.arm = StandardServo(arm_pin)
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
        self.arm.change_angle(180)
        self.arm_status = True

    def close_arm(self):
        self.arm.change_angle(0)
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
        self.arm.stop()

    def close(self):
        self.stop()


if __name__ == '__main__':
    try:
        for i in range(6, 8):
            print("pin:", i)
            m = ContinuousRotationServo(i)
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

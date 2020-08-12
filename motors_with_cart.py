import math
from time import sleep
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)


class NotInCorrectRange(Exception):
    pass


class ContinuousRotationServo:
    max_freq = 1900
    min_freq = 1100
    middle_point = (max_freq + min_freq) / 2
    power_multiplier = ((max_freq - min_freq) / 2) / 100

    def __init__(self, pin):
        self.control = None
        self.pin = pin
        self.motor_initialize()

    def motor_initialize(self):
        self.control = kit.continuous_servo[self.pin]
        self._change_power(0)

    def _change_power(self, power):
        """
        :param power: this parameter takes a value between -100 and 100. Negative values​make it work backward,
                      positive values​make it work forward.
        :return:
        """
        self.control.throttle = power / 100

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
        return self._change_power(0)


class StandardServo:
    max_degree = 180
    min_freq = 1100
    max_freq = 1900

    def __init__(self, pin):
        self.control = None
        self.pin = pin
        self.motor_initialize()

    def motor_initialize(self):
        self.control = kit.servo[self.pin]
        self.control.actuation_range = self.max_degree
        self.control.set_pulse_width_range(self.min_freq, self.max_freq)
        self.change_angle(0)

    def change_angle(self, angle):
        self.control.angle = angle


class RovMovement:
    def __init__(self, xy_lf_pin, xy_rf_pin, xy_lb_pin, xy_rb_pin, z_lf_pin, z_rf_pin, z_lb_pin, z_rb_pin, arm_pin):
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
        self._initialize_motors()
        sleep(2)

    def _initialize_motors(self):
        print("All motors initializing...")
        for i in list(range(0, 100)) + list(range(100, -100, -1)) + list(range(-100, 1)):
            for motor in self.all_motors_list:
                motor.run_bidirectional(i)
                sleep(0.05)
        print("All motors initialized...")

    def go_up(self, power):
        power_per_motor = power / 4
        for motor in self.z_motors_list:
            motor.run_clockwise(power_per_motor)

    def go_down(self, power):
        power_per_motor = power / 4
        for motor in self.z_motors_list:
            motor.run_counterclockwise(power_per_motor)

    def turn_left(self, power):
        power_per_motor = power / 4
        self.xy_rf.run_clockwise(power_per_motor)
        self.xy_lf.run_counterclockwise(power_per_motor)
        self.xy_lb.run_clockwise(power_per_motor)
        self.xy_rb.run_counterclockwise(power_per_motor)

    def turn_right(self, power):
        power_per_motor = power / 4
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
        power_per_motor = power / 4

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

    def open_arm(self):
        self.arm.change_angle(180)
        self.arm_status = True

    def close_arm(self):
        self.arm.change_angle(0)
        self.arm_status = False

    def toggle_arm(self):
        if self.arm_status:
            self.close_arm()
        else:
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

    def close(self):
        self.stop()


rov_movement = RovMovement(xy_lf_pin=0, xy_rf_pin=1, xy_lb_pin=2, xy_rb_pin=3,
                           z_lf_pin=4, z_rf_pin=5, z_lb_pin=6, z_rb_pin=7, arm_pin=8)


def motor_xy_control(que):
    while True:
        value = que.get()

        if not value["xy_plane"]["magnitude"] == 0.0 or value["turn_itself"] == 0.0:
            power = value["xy_plane"]["magnitude"]
            degree = value["xy_plane"]["angel"]
            rov_movement.go_xy(power, degree)
        else:
            power = value["turn_itself"]
            if power > 0:
                rov_movement.turn_right(abs(power))
            else:
                rov_movement.turn_left(abs(power))


def motor_z_control(que):
    while True:
        power = que.get()
        if power > 0:
            rov_movement.go_up(abs(power))
        else:
            rov_movement.go_down(abs(power))


if __name__ == '__main__':
    rov_movement = RovMovement(xy_lf_pin=0, xy_rf_pin=1, xy_lb_pin=2, xy_rb_pin=3,
                               z_lf_pin=4, z_rf_pin=5, z_lb_pin=6, z_rb_pin=7, arm_pin=8)
    try:
        import getch

        power = 0
        char = "w"
        while True:
            previous = char
            char = getch.getch()
            if previous != char:
                rov_movement.stop()

            if char == "a":
                print("Hareket: sola git", "\tGüç:", power)
                rov_movement.go_xy(power, 270)
            elif char == "s":
                print("Hareket: geri git", "\tGüç:", power)
                rov_movement.go_xy(power, 180)
            elif char == "d":
                print("Hareket: sağa git", "\tGüç:", power)
                rov_movement.go_xy(power, 90)
            elif char == "w":
                print("Hareket: ileri git", "\tGüç:", power)
                rov_movement.go_xy(power, 0)
            elif char == "y":
                print("Hareket: yüksel", "\tGüç:", power)
                rov_movement.go_up(power)
            elif char == "u":
                print("Hareket: alçal", "\tGüç:", power)
                rov_movement.go_down(power)
            elif char == "q":
                print("Hareket: sola dön", "\tGüç:", power)
                rov_movement.turn_left(power)
            elif char == "e":
                print("Hareket: sağa dön", "\tGüç:", power)
                rov_movement.turn_right(power)
            elif char == "j":
                print("Hareket: güçü arttır", "\tGüç:", power)
                if power <= 90:
                    power += 10
            elif char == "k":
                print("Hareket: güçü azalt", "\tGüç:", power)
                if power >= 10:
                    power -= 10
            else:
                rov_movement.stop()
                print("Tanımsız karaktere basıldı")
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
    except KeyboardInterrupt:
        print("KeyboardInterrupt yakalandı")

    rov_movement.close()

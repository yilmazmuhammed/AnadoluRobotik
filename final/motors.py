import math
from time import sleep

import os

os.system("sudo pigpiod")
import pigpio

pi = pigpio.pi()


class NotInCorrectRange(Exception):
    pass


class Motor:
    max_freq = 1900
    min_freq = 1100
    middle_point = (max_freq + min_freq) / 2
    power_multiplier = ((max_freq - min_freq) / 2) / 100

    def __init__(self, pin):
        self.control = None
        self.pin = pin
        self.motor_initialize()

    def motor_initialize(self):
        self.change_power(0)
        self.control = None

    def change_power(self, power):
        """
        :param power: this parameter takes a value between -100 and 100. Negative values​make it work backward,
                      positive values​make it work forward.
        :return:
        """
        power *= -1
        power = power * self.power_multiplier
        pi.set_servo_pulsewidth(self.pin, self.middle_point + power)
        pass

    def run_clockwise(self, power):
        """
        Suyu geriye ittirir. Motor ileriye doğru hareket etmek ister.
        :param power:
        :return:
        """
        if not 0 <= power <= 100:
            raise NotInCorrectRange("Power must be between 0 and 100.")
        return self.change_power(power)

    def run_counterclockwise(self, power):
        """
        Suyu ileriye ittirir. Motor geriye doğru hareket etmek ister.
        :param power:
        :return:
        """
        if not 0 <= power <= 100:
            raise NotInCorrectRange("Power must be between 0 and 100.")
        return self.change_power(-power)

    def run_bidirectional(self, power):
        if power >= 0:
            self.run_clockwise(power)
        else:
            self.run_counterclockwise(-power)

    def stop(self):
        return self.change_power(0)


class RovMovement:
    def __init__(self, xy_lf_pin, xy_rf_pin, xy_lb_pin, xy_rb_pin, z_lf_pin, z_rf_pin, z_lb_pin, z_rb_pin):
        self.xy_lf = Motor(xy_lf_pin)
        self.xy_rf = Motor(xy_rf_pin)
        self.xy_lb = Motor(xy_lb_pin)
        self.xy_rb = Motor(xy_rb_pin)
        self.z_lf = Motor(z_lf_pin)
        self.z_rf = Motor(z_rf_pin)
        self.z_lb = Motor(z_lb_pin)
        self.z_rb = Motor(z_rb_pin)
        self.z_motors_list = [self.z_lf, self.z_rf, self.z_lb, self.z_rb]
        self.xy_motors_list = [self.xy_lf, self.xy_rf, self.xy_lb, self.xy_rb]
        self.all_motors_list = self.z_motors_list + self.xy_motors_list
        sleep(2)

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
        pi.stop()


if __name__ == '__main__':
    rov_movement = RovMovement(xy_lf_pin=0, xy_rf_pin=0, xy_lb_pin=0, xy_rb_pin=0,
                               z_lf_pin=0, z_rf_pin=0, z_lb_pin=0, z_rb_pin=0)
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

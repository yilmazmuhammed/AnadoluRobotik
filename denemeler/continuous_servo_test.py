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
        self.change_power(0)

    def change_power(self, power):
        """
        :param power: this parameter takes a value between -100 and 100. Negative values​make it work backward,
                      positive values​make it work forward.
        :return:
        """
        power *= -1
        self.control.throttle = power / 100

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


if __name__ == '__main__':
    motor = ContinuousRotationServo(1)
    max_power = 50
    for i in range(0, max_power):
        motor.run_bidirectional(i)
        sleep(0.1)
    for i in range(max_power, -max_power, -1):
        motor.run_bidirectional(i)
        sleep(0.1)
    for i in range(-max_power, 1):
        motor.run_bidirectional(i)
        sleep(0.1)


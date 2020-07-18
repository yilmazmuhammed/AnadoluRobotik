import math

import pygame

pygame.init()
pygame.joystick.init()
clock = pygame.time.Clock()


class Joystick:
    def __init__(self, x_axis=0, y_axis=1, turn_axis=2, z_axis=3, joystick_order=0):
        self.joystick_order = joystick_order
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.turn_axis = turn_axis
        self.z_axis = z_axis

        self.joystick = pygame.joystick.Joystick(self.joystick_order)
        self.joystick.init()
        self.name = self.joystick.get_name()

    def _get_data_init(self):
        pygame.event.get()
        self.joystick = pygame.joystick.Joystick(self.joystick_order)
        self.joystick.init()

    def get_data(self):
        ret = {"xy_plane": {"angel": 0, "magnitude": 0}, "z_axis": 0, "turn_itself": 0}
        self._get_data_init()

        x = self.joystick.get_axis(self.x_axis)
        y = self.joystick.get_axis(self.y_axis)

        if x == 0 and y < 0:
            angle = 0
        elif x > 0 and y < 0:  # 0-90
            angle = math.atan(abs(x) / abs(y))
        elif x > 0 and y == 0:
            angle = math.pi * 1 / 2
        elif x > 0 and y > 0:  # 90-180
            angle = math.pi * 1 / 2 + math.atan(abs(y) / abs(x))
        elif x == 0 and y > 0:
            angle = math.pi
        elif x < 0 and y > 0:  # 180-270
            angle = math.pi + math.atan(abs(x) / abs(y))
        elif x < 0 and y == 0:
            angle = math.pi * 3 / 2
        elif x < 0 and y < 0:  # 270-360
            angle = math.pi * 3 / 2 + math.atan(abs(y) / abs(x))
        else:
            angle = 0
        degree = angle / math.pi * 180

        abs_x, abs_y = abs(x), abs(y)
        if abs_x == 0 and abs_y == 0:
            magnitude = 0
        elif abs_x <= 1 and abs_y <= 1:
            bigger = abs_x if abs_x > abs_y else abs_y
            magnitude = 1 / bigger

        ret["xy_plane"]["angel"] = degree
        ret["xy_plane"]["magnitude"] = magnitude

        ret["z_axis"] = self.joystick.get_axis(self.z_axis)

        ret["turn_itself"] = self.joystick.get_axis(self.turn_axis)

        return ret


if __name__ == '__main__':
    j = Joystick()
    while True:
        print(j.get_data())

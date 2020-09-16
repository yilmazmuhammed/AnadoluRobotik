from time import sleep

import pygame
import os
import numpy as np
import math
from threading import Thread


class SharedOutput():

    def __init__(self):
        self.ret_dict = {
            "xy_plane": {
                "angel": 0,  # jotstick çubuğunun ileri geri ve sağa sola ittirilmesi
                "magnitude": 0
            },
            "z_axes": 0,  # 5 ve 3 numaralı butonlara basılması durumu
            "turn_itself": 0,
            "robotik_kol": 0,  # joystick çubuğunun kendi eksininde döndürülmesi hareketi
            "asagi_bak": 0,
            "dik_dur": 0
        }
        self.x = 0
        self.y = 0
        self.k = 1

    def update_xy(self):
        self.angel_calculator()

    def update_z(self, z):
        self.ret_dict["z_axes"] = z

    def update_turn(self, turn):
        self.ret_dict["turn_itself"] = turn

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def update_kol(self):
        self.k = -1 * self.k
        self.ret_dict["robotik_kol"] = self.k

    def angel_calculator(self):
        x = self.x
        y = self.y

        if x == 0 and y == 0:
            angel = 0
        elif x > 0:
            if y > 0:
                angel = math.atan(y / x)
            elif (y < 0):
                angel = 2 * np.pi + math.atan(y / x)
            else:
                angel = 0
        elif x < 0:
            if y > 0:
                angel = np.pi + math.atan(y / x)
            elif y < 0:
                angel = np.pi + math.atan(y / x)
            else:
                angel = np.pi
        else:
            if y > 0:
                angel = np.pi / 2
            else:
                angel = np.pi * 3 / 2

        degree = angel * (180 / np.pi)
        if 0 <= degree <= 45:
            degree = 0
        elif 45 < degree <= 135:
            degree = 90
        elif 135 < degree <= 225:
            degree = 180
        elif 225 < degree <= 315:
            degree = 270
        elif 315 < degree <= 360:
            degree = 0

        if x == 0:
            self.ret_dict["xy_plane"]["angel"] = degree
            self.ret_dict["xy_plane"]["magnitude"] = abs(y)
        elif math.atan(y / x) < 1:
            self.ret_dict["xy_plane"]["angel"] = degree
            self.ret_dict["xy_plane"]["magnitude"] = abs(x)
        else:
            self.ret_dict["xy_plane"]["angel"] = degree
            self.ret_dict["xy_plane"]["magnitude"] = abs(y)


class Joystick:

    def __init__(self):
        self.shared_obj = SharedOutput()
        pygame.init()
        self.done = False
        self.clock = pygame.time.Clock()
        pygame.joystick.init()
        # self.button_pressed = 0
        # self.dic_initializer()
        self.joystick = None
        self.joystick_count = None
        self.name = None
        self.axes = None

    def for_initializer(self):
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        self.name = self.joystick.get_name()
        self.axes = self.joystick.get_numaxes()

        self.get_z_values()
        self.get_look_down()
        self.get_stand_upright()

    def while_initializer(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.JOYBUTTONDOWN:
                if pygame.joystick.Joystick(0).get_button(0) == 1:
                    self.shared_obj.update_kol()
                    # print("Joystick button released.")
            """elif event.type == pygame.JOYBUTTONUP:
                #if pygame.joystick.Joystick(self.i).get_button(0)==1:
                #self.button_pressed = 0
                print("Joystick button released.")"""

        self.joystick_count = pygame.joystick.get_count()

    def get_z_values(self):
        # self.shared_obj.update_z(round(pygame.joystick.Joystick(0).get_axis(3), 2))
        self.shared_obj.update_z(pygame.joystick.Joystick(0).get_hat(0)[1])

    def get_look_down(self):
        self.shared_obj.ret_dict["asagi_bak"] = pygame.joystick.Joystick(0).get_button(10)

    def get_stand_upright(self):
        self.shared_obj.ret_dict["dik_dur"] = pygame.joystick.Joystick(0).get_button(11)

    def joysticks(self):
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

        name = joystick.get_name()
        axes = joystick.get_numaxes()

        for i in range(axes):
            axis = joystick.get_axis(i)

            if i == 0:
                # if(axis<0):
                #     print("kol sola doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")
                # if(axis>0):
                #     print("kol sağa doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")
                # #self.x = axis
                self.shared_obj.set_y(axis)
                # self.shared_obj.set_x(axis)
                # print("x: " + str(axis))

            elif i == 1:
                # if(axis<0):
                #     print("kol ileri doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")
                # if(axis>0):
                #     print("kol geri doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")
                # #self.y = axis
                self.shared_obj.set_x(-1 * axis)
                # self.shared_obj.set_y( axis)
                # print("y: " + str(axis))

            elif i == 2:
                # if(axis<0):
                #     print("kol saat yönünün tersine doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")
                # if(axis>0):
                #     print("kol saat yönününe doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")
                self.shared_obj.update_turn(axis)

            # elif i == 3:
            #     self.shared_obj.update_z(round(-axis, 3))

        self.shared_obj.update_xy()

    def buttons(self):

        joystick = pygame.joystick.Joystick(0)
        buttons = joystick.get_numbuttons()

        for i in range(buttons):
            button = joystick.get_button(i)
            if button > 0:
                if i == 0:
                    print("z ekseninde yukarı çıkılıyor")
                    # self.ret_dict["z_axes"] = 1
                    self.shared_obj.update_kol()
            else:
                if i == 0:
                    print("z ekseninde yukarı çıkılıyor")
                    # self.ret_dict["z_axes"] = 1
                    self.shared_obj.update_kol()

    def quit(self):
        pygame.quit()


if __name__ == '__main__':
    # # Joystick variables are creating
    # joystick_values = {}
    # joystick_thread = Thread(target=joystick_control, args=(joystick_values,))
    # joystick_thread.start()
    # # Lidars variables are created
    #
    # while True:
    #     print(joystick_values)
    #     # sleep(0.1)

    Joy_obj = Joystick()

    while not Joy_obj.done:
        # print("1asd")
        Joy_obj.while_initializer()  # , args=(scriptA + argumentsA))
        if Joy_obj.joystick_count:
            # print(joystick_count)

            Joy_obj.for_initializer()
            # Joy_obj.for_initializer(i) # thread_S yap done() ile kontrol et olup olmadığını sonra diğerlerini threadle
            Joy_obj.joysticks()  # , args=(str(i)))
            # Joy_obj.joysticks()
            # Joy_obj.buttons()
            # if Joy_obj.button_pressed == 1:
            print(Joy_obj.shared_obj.ret_dict)
            sleep(0.1)

        Joy_obj.clock.tick(20)

    Joy_obj.quit()

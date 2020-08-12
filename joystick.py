from time import sleep

import pygame
import os
import numpy as np
import math
from threading import Thread


class SharedOutput():

    def __init__(self):
        self.ret_dict = {"xy_plane": {"angel":0,            #jotstick çubuğunun ileri geri ve sağa sola ittirilmesi
                                      "magnitude":0},
                        "z_axes":0,                         #5 ve 3 numaralı butonlara basılması durumu
                        "turn_itself":0}                    #joystick çubuğunun kendi eksininde döndürülmesi hareketi
        self.x = 0
        self.y = 0

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

    def angel_calculator(self):
        x = self.x
        y = self.y

        if x==0 and y==0:
            angel = 0
        elif x>0:
            if y>0:
                angel = math.atan(y/x)
            elif(y>0):
                angel = 2*np.pi + math.atan(y/x)
            else:
                angel = 0
        elif x<0:
            if y>0:
                angel = np.pi + math.atan(y/x)
            elif y<0:
                angel = np.pi + math.atan(y/x)
            else:
                angel = np.pi
        else:
            if y>0:
                angel = np.pi/2
            else:
                angel = np.pi*3/2

        if x==0:
            self.ret_dict["xy_plane"]["angel"] = angel*(180/np.pi)
            self.ret_dict["xy_plane"]["magnitude"] = y
        elif math.atan(y/x)<1:
            self.ret_dict["xy_plane"]["angel"] = angel*(180/np.pi)
            self.ret_dict["xy_plane"]["magnitude"] = x
        else:
            self.ret_dict["xy_plane"]["angel"] = angel*(180/np.pi)
            self.ret_dict["xy_plane"]["magnitude"] = y

class Joystick:

    def __init__(self):
        self.shared_obj = SharedOutput()
        pygame.init()
        self.done = False
        self.clock = pygame.time.Clock()
        pygame.joystick.init()
        #self.button_pressed = 0
        #self.dic_initializer()

    def for_initializer(self, i):
        #print("asdsf")
        #print(i)
        i = int(i)
        self.joystick = pygame.joystick.Joystick(i)
        self.joystick.init()

        self.name = self.joystick.get_name()
        self.axes = self.joystick.get_numaxes()

        self.i = i

    def while_initializer(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.JOYBUTTONDOWN:
                #self.button_pressed = 1
                print("Joystick button pressed.")
            elif event.type == pygame.JOYBUTTONUP:
                #self.button_pressed = 0
                print("Joystick button released.")

        self.joystick_count = pygame.joystick.get_count()

    def joysticks(self):

        for i in range(pygame.joystick.get_count()):

            joystick = pygame.joystick.Joystick(self.i)
            joystick.init()

            name = joystick.get_name()
            axes = joystick.get_numaxes()

            for i in range(axes):
                axis = joystick.get_axis(i)

                if(i==0):
                    # if(axis<0):
                    #     print("kol sola doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")
                    # if(axis>0):
                    #     print("kol sağa doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")
                    # #self.x = axis
                    self.shared_obj.set_y(-1*axis)
                    #self.shared_obj.set_x(axis)
                    #print("x: " + str(axis))

                elif(i==1):
                    # if(axis<0):
                    #     print("kol ileri doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")
                    # if(axis>0):
                    #     print("kol geri doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")
                    # #self.y = axis
                    self.shared_obj.set_x(axis)
                    #self.shared_obj.set_y( axis)
                    #print("y: " + str(axis))

                elif(i==2):
                    # if(axis<0):
                    #     print("kol saat yönünün tersine doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")
                    # if(axis>0):
                    #     print("kol saat yönününe doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")
                    self.shared_obj.update_turn( axis)

                elif(i==3):
                    self.shared_obj.update_z(round(-axis, 3))

            self.shared_obj.update_xy()

    def buttons(self):

        joystick = pygame.joystick.Joystick(self.i)
        buttons = joystick.get_numbuttons()

        for i in range(buttons):
            button = joystick.get_button(i)
            if button>0:
                if(i==5):
                    print("z ekseninde yukarı çıkılıyor")
                    #self.ret_dict["z_axes"] = 1
                    self.shared_obj.update_z(1)
                if(i==3):
                    print("z ekseninde aşağı iniliyor")
                    #self.ret_dict["z_axes"] = -1
                    self.shared_obj.update_z(1)

    def quit(self):
        pygame.quit()



def joystick_control(que):

    Joy_obj = Joystick()
    print(Joy_obj.done)

    while 0==Joy_obj.done:
        #print("1asd")
        t1 = Thread(target=Joy_obj.while_initializer)#, args=(scriptA + argumentsA))
        #Joy_obj.while_initializer()
        t1.start()
        #print(joystick_count)

        for i in range(Joy_obj.joystick_count):
            t1.join()
            t2 = Thread(target=Joy_obj.for_initializer, args=(str(i)))
            t2.start()
            t2.join()
            #Joy_obj.for_initializer(i) # thread_S yap done() ile kontrol et olup olmadığını sonra diğerlerini threadle
            t3 = Thread(target=Joy_obj.joysticks)#, args=(str(i)))
            t4 = Thread(target=Joy_obj.buttons)#, args=(str(i)))
            t3.start()
            t4.start()
            t3.join()
            t4.join()
            #Joy_obj.joysticks()
            #Joy_obj.buttons()
            #if Joy_obj.button_pressed == 1:
            # print(Joy_obj.shared_obj.ret_dict)
            que.put(Joy_obj.shared_obj.ret_dict)
            sleep(0.1)
        Joy_obj.clock.tick(20)

    Joy_obj.quit()

if __name__ == '__main__':

    Joy_obj = Joystick()
    print(Joy_obj.done)

    while 0==Joy_obj.done:
        #print("1asd")
        t1 = Thread(target=Joy_obj.while_initializer)#, args=(scriptA + argumentsA))
        #Joy_obj.while_initializer()
        t1.start()
        #print(joystick_count)

        for i in range(Joy_obj.joystick_count):
            t1.join()
            t2 = Thread(target=Joy_obj.for_initializer, args=(str(i)))
            t2.start()
            t2.join()
            #Joy_obj.for_initializer(i) # thread_S yap done() ile kontrol et olup olmadığını sonra diğerlerini threadle
            t3 = Thread(target=Joy_obj.joysticks)#, args=(str(i)))
            t4 = Thread(target=Joy_obj.buttons)#, args=(str(i)))
            t3.start()
            t4.start()
            t3.join()
            t4.join()
            #Joy_obj.joysticks()
            #Joy_obj.buttons()
            #if Joy_obj.button_pressed == 1:
            print(Joy_obj.shared_obj.ret_dict)
            sleep(0.1)

        Joy_obj.clock.tick(20)

    Joy_obj.quit()
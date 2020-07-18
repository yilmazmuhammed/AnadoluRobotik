import pygame
import os
import numpy as np
import math
#import motors

class TextPrint(object):
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)
    def tprint(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, (self.x, self.y))
        self.y += self.line_height
    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15
    def indent(self):
        self.x += 10
    def unindent(self):
        self.x -= 10

class Joystick:

    def __init__(self):
        #print(pygame())
        #self.pygame_object = pygame.init()
        #print(type(self.pygame_object))
        pygame.init()
        #print(self.pygame_object)
        self.done = False
        #clock = self.pygame_object.time.Clock()
        clock = pygame.time.Clock()
        #self.pygame_object.joystick.init()
        pygame.joystick.init()
        self.dic_initializer()
        self.x = self.y = 0

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

        if math.atan(y/x)<1:
            self.ret_dict["xy_plane"]["angel"] = angel*(180/np.pi)
            self.ret_dict["xy_plane"]["magnitude"] = (x**2+y**2)**(1/2)*math.cos(angel)#*acos(angel)
        else:
            self.ret_dict["xy_plane"]["angel"] = angel*(180/np.pi)
            self.ret_dict["xy_plane"]["magnitude"] = (x**2+y**2)**(1/2)*math.sin(angel)#*asin(angel)

    def for_initializer(self):
        #print(type(pygame.joystick.Joystick(i)))
        self.joystick = pygame.joystick.Joystick(i)
        self.joystick.init()

        self.name = self.joystick.get_name()
        self.axes = self.joystick.get_numaxes()

    def while_initializer(self):
        for event in pygame.event.get():    
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.JOYBUTTONDOWN:
                print("Joystick button pressed.")
            elif event.type == pygame.JOYBUTTONUP:
                print("Joystick button released.")

    def dic_initializer(self):
        self.ret_dict = {"xy_plane": {"angel":0,            #jotstick çubuğunun ileri geri ve sağa sola ittirilmesi
                                      "magnitude":0},
                        "z_axes":0,                         #5 ve 3 numaralı butonlara basılması durumu
                        "turn_itself":0}                    #joystick çubuğunun kendi eksininde döndürülmesi hareketi

    def is_button_press(self):
        for event in pygame.event.get():
        
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.JOYBUTTONDOWN:
                print("Joystick button pressed.")
            elif event.type == pygame.JOYBUTTONUP:
                print("Joystick button released.")

    def joysticks(self):

        for i in range(pygame.joystick.get_count()):

            joystick = pygame.joystick.Joystick(i)
            joystick.init()

            name = joystick.get_name()
            axes = joystick.get_numaxes()

            for i in range(axes):
                axis = joystick.get_axis(i)

                if(i==0):
                    if(axis<0):
                        print("kol sola doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")                
                    if(axis>0):
                        print("kol sağa doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")
                    self.x = axis
                
                elif(i==1):
                    if(axis<0):
                        print("kol ileri doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")                
                    if(axis>0):
                        print("kol geri doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")
                    self.y = axis                

                elif(i==2):
                    if(axis<0):
                        print("kol saat yönünün tersine doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")                
                    if(axis>0):
                        print("kol saat yönününe doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")
                    self.ret_dict["turn_itself"] = axis
                    
            angel_calculator(self)

    def buttons(self):

        joystick = pygame.joystick.Joystick(i)
        buttons = joystick.get_numbuttons()

        for i in range(buttons):            
            button = joystick.get_button(i)
            if(i==5):
                print("z ekseninde yukarı çıkılıyor")
                self.ret_dict["z_axes"] = 1
            if(i==3):
                print("z ekseninde aşağı iniliyor")
                self.ret_dict["z_axes"] = -1

    def quit(self):
        pygame.quit()


if __name__ == '__main__':

    Joy_obj = Joystick()

    while Joy_obj.done:

        Joy_obj.while_initializer()
        Joy_obj.for_initializer()
        Joy_obj.joysticks()
        Joy_obj.buttons()
        print(Joy_obj.ret_dict)
        clock.tick(20)

    Joy_obj.quit()
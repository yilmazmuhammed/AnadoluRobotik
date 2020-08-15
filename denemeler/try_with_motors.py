import pygame
import os
import numpy as np
import math
import motors_with_pigpio

# Robotik kol pin ayarlama, 75-81 satirda servo güc degerleri
os.system("sudo pigpiod")
import pigpio
robotkol=21
ac = True
pi = pigpio.pi()
pi.set_servo_pulsewidth(robotkol, 0)


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

def angel_calculator(x,y):

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
        return angel*(180/np.pi), (x**2+y**2)**(1/2)*math.cos(angel)#*acos(angel)
    else:
        return angel*(180/np.pi), (x**2+y**2)**(1/2)*math.sin(angel)#*asin(angel)


pygame.init()
done = False
clock = pygame.time.Clock()
pygame.joystick.init()


while not done:
    for event in pygame.event.get():
    
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.JOYBUTTONDOWN:
            
            #robot kol
            if(bool(ac)==True):
                    pi.set_servo_pulsewidth(robotkol, 1900)
                    ac=False
            elif(bool(ac)==False):
                    pi.set_servo_pulsewidth(robotkol, 1100)
                    ac=True
                    
            print("Joystick button pressed.")
        elif event.type == pygame.JOYBUTTONUP:
            print("Joystick button released.")

    joystick_count = pygame.joystick.get_count()
    print(joystick_count)


    for i in range(joystick_count):

        joystick = pygame.joystick.Joystick(i)
        joystick.init()

        name = joystick.get_name()
        axes = joystick.get_numaxes()

        for i in range(axes):
            axis = joystick.get_axis(i)

            if(i==0):
                if(axis<0):
                    print("kol sola doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")
                    motors_with_pigpio.run_counterclockwise(abs(axis))
                if(axis>0):
                    print("kol sağa doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")
                    motors_with_pigpio.run_clockwise(abs(axis))
            
            elif(i==1):
                if(axis<0):
                    print("kol ileri doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")
                    motors_with_pigpio.run_counterclockwise(abs(axis))
                if(axis>0):
                    print("kol geri doğru:" + str(abs(axis)) + "değeri kadar itiliyor.")
                    motors_with_pigpio.run_clockwise(abs(axis))

            elif(i==2):
                if(axis<0):
                    print("3. joystick yukarı doğru :" + str(abs(axis)) + "değeri kadar")
                    motors_with_pigpio.run_counterclockwise(abs(axis))
                if(axis>0):
                    print("3. joystick aşağı doğru :" + str(abs(axis)) + "değeri kadar") 
                    motors_with_pigpio.run_clockwise(abs(axis))


    #motors.run_clockwise(x_axes)
    #motors.run_counterclockwise(y_axes)

    clock.tick(20)


pygame.quit()
import pygame
import os


# Define some colors.
BLACK = pygame.Color('black')
WHITE = pygame.Color('white')
#print(BLACK)
#print(WHITE)

# This is a simple class that will help us print to the screen.
# It has nothing to do with the joysticks, just outputting the
# information.
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


pygame.init()

# Set the width and height of the screen (width, height).
#screen = pygame.display.set_mode((500, 700))

#pygame.display.set_caption("My Game")

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates.
clock = pygame.time.Clock()
print(clock)
# Initialize the joysticks.
pygame.joystick.init()

# Get ready to print.
#textPrint = TextPrint()
#print(textPrint)

while not done:
    #
    # EVENT PROCESSING STEP
    #
    # Possible joystick actions: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
    # JOYBUTTONUP, JOYHATMOTION
    for event in pygame.event.get(): # User did something.
    
        if event.type == pygame.QUIT: # If user clicked close.
            done = True # Flag that we are done so we exit this loop.
        elif event.type == pygame.JOYBUTTONDOWN:
            print("Joystick button pressed.")
        elif event.type == pygame.JOYBUTTONUP:
            print("Joystick button released.")

    joystick_count = pygame.joystick.get_count()
    #print(joystick_count)

    for i in range(joystick_count):

        joystick = pygame.joystick.Joystick(i)
        joystick.init()

        # Get the name from the OS for the controller/joystick.
        name = joystick.get_name()
        #print("name of joystick" + name)

        # Usually axis run in pairs, up/down for one, and left/right for
        # the other.
        axes = joystick.get_numaxes()
        #print("***********************AXES SAYISI: : ")
        #print(axes)
        duty_cycle = 50


        for i in range(axes):
            #print("kacinci axes: ")
            #print(i)
            axis = joystick.get_axis(i)
            #print(type(axis))

            if(axis<0):
                print("kacinci axes: ")
                print(i)
                print("axis değeri: ")
                print(axis)
                duty_cycle = abs(axis)*100/2 + 50
            
            if(axis>0):
                print("kacinci axes: ")
                print(i)
                print("axis değeri: ")
                print(axis)
                duty_cycle = 50 - abs(axis)*100/2

                

        buttons = joystick.get_numbuttons()
        #print("****************BUTTON SAYISI: ")
        #print(buttons)
        for i in range(buttons):
            #print("kacinci button: ")
            #print(i)
            button = joystick.get_button(i)
            if(button>0):# or button[1]>0):
                print("kacinci button: ")
                print(i)
                print("button degeri: ")
                print(button)
                duty_cycle = 100
            #print("button")
            #print(button)

        hats = joystick.get_numhats()
        #print("*******************HAT SAYISI: ")
        #print(hats)
        for i in range(hats):
            #print("kacinci hat: ")
            #print(i)
            hat = joystick.get_hat(i)
            if(hat[0]>0 or hat[1]>0):
                print("kacinci hat: ")
                print(i)
                print("hat degeri: ")
                print(hat)
                duty_cycle = 0

        print("duty_cycle: ")
        print(duty_cycle)

    clock.tick(20)
    #os.system('clear')


pygame.quit()
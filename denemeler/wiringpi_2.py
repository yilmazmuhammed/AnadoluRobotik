import time
import wiringpi

wiringpi.wiringPiSetupGpio()
pins = 18

wiringpi.pinMode(pins, wiringpi.GPIO.PWM_OUTPUT)
#wiringpi.pinMode(17, wiringpi.GPIO.PWM_OUTPUT)

wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)
wiringpi.pwmSetClock(192)
wiringpi.pwmSetRange(2000)
print ("program")

while True:
    print ("on 150")
    wiringpi.pwmWrite(pins, 150)
    time.sleep(2.0)
    print ("on 160")
    wiringpi.pwmWrite(pins, 160)
    time.sleep(5.0)
    print ("off 130")
    wiringpi.pwmWrite(pins, 130)
    time.sleep(2.0)
    print ("on 120")
    wiringpi.pwmWrite(pins, 120) 
    time.sleep(2.0)
    print ("stop")
    wiringpi.pwmWrite(pins, 0)

# Servo Control
import time
import wiringpi

# use 'GPIO naming'
wiringpi.wiringPiSetupGpio()

# set #18 to be a PWM output
wiringpi.pinMode(18, wiringpi.GPIO.PWM_OUTPUT)

# set the PWM mode to milliseconds stype
wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)

# divide down clock
wiringpi.pwmSetClock(192)
wiringpi.pwmSetRange(2000)

# PWM pulses for thruster:
# 110 = 1100 µs (full reverse)
# 150 = 1500 µs (stopped + initialize)
# 190 = 1900 µs (full forward)
# initialize thruster
wiringpi.pwmWrite(18, 150)

# wait for initialization (2 seconds)
time.sleep(2.0)

# set to some speed
wiringpi.pwmWrite(18, 170)
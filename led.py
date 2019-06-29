#!/user/bin/env python3

from RPi import GPIO
import time

Led = 12  # pin 11

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(Led, GPIO.OUT)
    GPIO.output(Led, GPIO.HIGH)


def loop():

    while True:
        print('led on')
        GPIO.output(Led, GPIO.LOW)
        time.sleep(2)
        print('led off')
        GPIO.output(Led, GPIO.HIGH)
        time.sleep(2)

def destroy():
    GPIO.output(Led, GPIO.HIGH)
    GPIO.cleanup()

if __name__ == "__main__":
    print('Press Ctrl+C to end the program...')
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()


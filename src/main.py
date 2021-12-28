import RPi.GPIO as GPIO
from gpiozero import Buzzer
import time


def buzz(pitch, duration):
    buzzer = Buzzer(4)
    period = 1.0 / pitch
    delay = period / 2
    cycles = int(duration * pitch)
    buzzer.beep(on_time=period, off_time=period, n=int(cycles/2))


def main():
    led = 12
    relay = 11

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(led, GPIO.OUT)
    GPIO.setup(relay, GPIO.OUT)


    GPIO.output(led, GPIO.HIGH)

    for _ in range(20):
        GPIO.output(relay, GPIO.HIGH)
        buzz(float(260), 0.33)
        time.sleep(0.33)
        GPIO.output(relay, GPIO.LOW)
        time.sleep(0.33)

    GPIO.cleanup()

if __name__ == '__main__':
    main()
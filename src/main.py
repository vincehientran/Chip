import RPi.GPIO as GPIO
import time

led = 12
relay = 11

GPIO.setmode(GPIO.BOARD)
GPIO.setup(led, GPIO.OUT)
GPIO.setup(relay, GPIO.OUT)


GPIO.output(led, GPIO.HIGH)

while True:
    GPIO.output(relay, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(relay, GPIO.LOW)
    time.sleep(0.5)

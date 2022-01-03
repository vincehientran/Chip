from gpiozero import OutputDevice, PWMOutputDevice
import time

class MotorControl(object):
    def __init__(self, ena, in1, in2, in3, in4, enb):
        self.leftWheelSpeed = 1
        self.rightWheelSpeed = 1

        self.ena = PWMOutputDevice(ena)
        self.ena.frequency = 1000
        self.ena.value = self.leftWheelSpeed
        self.in1 = OutputDevice(in1, active_high=True, initial_value=False)
        self.in2 = OutputDevice(in2, active_high=True, initial_value=False)

        self.enb = PWMOutputDevice(enb)
        self.enb.frequency = 1000
        self.enb.value = self.rightWheelSpeed
        self.in3 = OutputDevice(in3, active_high=True, initial_value=False)
        self.in4 = OutputDevice(in4, active_high=True, initial_value=False)

    def setSpeed(self, speed):
        self.leftWheelSpeed = speed
        self.rightWheelSpeed = speed
        self.ena.value = speed
        self.enb.value = speed

    def setSpeedLeft(self, speed):
        self.leftWheelSpeed = speed
        self.ena.value = speed

    def setSpeedRight(self, speed):
        self.rightWheelSpeed = speed
        self.enb.value = speed

    def forward(self, seconds, speed=1):
        self.setSpeed(speed)

        # turn every wheel forward
        self.in1.on()
        self.in2.off()
        self.in3.on()
        self.in4.off()

        time.sleep(seconds)

        # turn off every wheel
        self.stop() 

    def backward(self, seconds, speed=1):
        self.setSpeed(speed)

        # turn every wheel forward
        self.in1.off()
        self.in2.on()
        self.in3.off()
        self.in4.on()

        time.sleep(seconds)

        # turn off every wheel
        self.stop() 

    def stop(self):
        # reset everything
        self.in1.off()
        self.in2.off()
        self.in3.off()
        self.in4.off()
        self.ena.value = self.leftWheelSpeed
        self.enb.value = self.rightWheelSpeed

    def turnRight(self, seconds, speed=1):
        self.setSpeed(speed)

        # turn left wheels backward
        self.in1.off()
        self.in2.on()

        # turn right wheels foward
        self.in3.on()
        self.in4.off()

        time.sleep(seconds)

        # turn off every wheel
        self.stop()

    def turnLeft(self, seconds, speed=1):
        self.setSpeed(speed)

        # turn left wheels foward
        self.in1.on()
        self.in2.off()

        # turn right wheels backward
        self.in3.off()
        self.in4.on()

        time.sleep(seconds)

        # turn off every wheel
        self.stop()
        
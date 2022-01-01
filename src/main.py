from gpiozero import Buzzer, LED, OutputDevice

import cv2
import time

# buzzer = Buzzer(4)

# def buzz(pitch, duration):
#     period = 1.0 / pitch
#     delay = period / 2
#     cycles = int(duration * pitch)
#     buzzer.beep(on_time=period, off_time=period, n=int(cycles/2))

# def main():
#     led = LED(18)
#     relay = OutputDevice(17, active_high=True, initial_value=False)

#     led.on()

#     for _ in range(20):
#         relay.on()
#         buzz(float(260), 0.33)
#         time.sleep(0.33)
#         relay.off()
#         time.sleep(0.33)

def main():
    cam = cv2.VideoCapture(0)

    while True:
        ret, image = cam.read()
        cv2.imshow('Imagetest',image)
        k = cv2.waitKey(1)
        if k != -1:
            break
    cv2.imwrite('testimage.jpg', image)
    cam.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
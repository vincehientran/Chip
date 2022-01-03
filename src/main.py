from types import ModuleType
from gpiozero import OutputDevice

import cv2 as cv
from gpiozero.output_devices import Motor
import numpy as np
import threading
import time

from MotorControl import MotorControl

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

global turnConstant, isRunning

def edgeDetection(image):
    grayscale = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    threshold = cv.adaptiveThreshold(grayscale,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv.THRESH_BINARY,641,7)
    cannyEdge = cv.Canny(threshold, 15, 30)
    cannyEdge = cv.dilate(cannyEdge, cv.getStructuringElement(cv.MORPH_RECT, (3, 3)), iterations=1)
    return cannyEdge

def regionOfInterest(image):
    height = image.shape[0]
    polygons = np.array([ [(10, height), (630, height), (630, height - 100), (420, 100), (220, 100), (10, height - 100)] ])
    mask = np.zeros_like(image)
    cv.fillPoly(mask, polygons, 255)
    cropped = cv.bitwise_and(image, mask)
    return cropped

def lineDetection(image):
    lines = cv.HoughLinesP(image, 3, 2*(np.pi/180), 200, np.array([]), minLineLength=20, maxLineGap = 50)
    lineImage = np.zeros_like(image)
    lanes = None
    if lines is not None:
        lanes = avgLines(image, lines)
        for lane in lanes:
            x1, y1, x2, y2 = lane
            cv.line(lineImage, (x1, y1), (x2, y2), (255, 0, 0), 2)

    return lineImage, lanes

# find the slope and the point where the line intersects the bottom edge of the image
def lineParameters(shape, x1, y1, x2, y2):
    if -0.01 < x2-x1 < 0.01:
        slope = 1000
        bottomEdgeIntercept = x1
        return slope, bottomEdgeIntercept
    else:
        slope = (y2 - y1) / (x2 - x1)
        yIntercept = (slope * -x1) + y1
        bottomEdgeIntercept = (shape[1] - yIntercept) / slope
        if bottomEdgeIntercept < -100:
            bottomEdgeIntercept = -100
        if bottomEdgeIntercept > 740:
            bottomEdgeIntercept = 740
        return slope, bottomEdgeIntercept

def avgLines(image, lines):
    leftCandidates = []
    rightCandidates = []
    bottomEdgeIntercepts = []

    # find average xIntercepts
    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        slope, bottomEdgeIntercept = lineParameters(image.shape, x1, y1, x2, y2)
        
        bottomEdgeIntercepts.append(bottomEdgeIntercept)
    
    avgBottomEdgeIntercepts = 0
    for bottomEdgeIntercept in bottomEdgeIntercepts:
        avgBottomEdgeIntercepts += bottomEdgeIntercept / len(bottomEdgeIntercepts)

    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        slope, bottomEdgeIntercept = lineParameters(image.shape, x1, y1, x2, y2)

        # when the x-intercept is less than the average, then it is a leftCandidate
        if bottomEdgeIntercept < avgBottomEdgeIntercepts:
            leftCandidates.append((slope, bottomEdgeIntercept))
        else:
            rightCandidates.append((slope, bottomEdgeIntercept))
        
    # print(len(leftCandidates), len(rightCandidates))
    # print(avgBottomEdgeIntercepts)

    leftLine = None
    rightLine = None
    if len(leftCandidates) > 0:
        leftAverage = np.average(leftCandidates, axis=0)
        left_y1 = image.shape[0]
        left_y2 = int(left_y1 * (1/3))
        left_x1 = int(leftAverage[1])    # this is the bottomEdgeIntercept
        left_x2 = int( (left_y2 + (leftAverage[0]*leftAverage[1]) - left_y1) / leftAverage[0])
        leftLine = np.array([left_x1, left_y1, left_x2, left_y2])

    if len(rightCandidates) > 0:
        rightAverage = np.average(rightCandidates, axis=0)
        right_y1 = image.shape[0]
        right_y2 = int(right_y1 * (1/3))
        right_x1 = int(rightAverage[1])    # this is the bottomEdgeIntercept
        right_x2 = int( (right_y2 + (rightAverage[0]*rightAverage[1]) - right_y1) / rightAverage[0])
        rightLine = np.array([right_x1, right_y1, right_x2, right_y2])

    if leftLine is not None and rightLine is not None:
        return np.array([leftLine, rightLine])
    elif leftLine is not None:
        # did not detect 2 lane lines
        return np.array([leftLine])
    elif rightLine is not None:
        # did not detect 2 lane lines
        return np.array([rightLine])
    else:
        return []

def removeHorizontal(image):
    # initalize masks so we can remove the horizontal lines from the image
    horizontal = np.copy(image)
    horizontal = cv.blur(horizontal,(2,2))

    # make a mask for the horizontal lines
    cols = horizontal.shape[1]
    horizontal_size = cols // 10
    horizontalStructure = cv.getStructuringElement(cv.MORPH_RECT, (horizontal_size, 1))
    horizontal = cv.erode(horizontal, horizontalStructure)
    horizontal = cv.dilate(horizontal, horizontalStructure)
    horizontal = cv.blur(horizontal,(6,6))
    horizontal = (255-horizontal)
    horizontal = cv.threshold(horizontal,250,255,cv.THRESH_BINARY)[1]

    return cv.bitwise_and(image, horizontal), horizontal

# aligns the vehicle to the road
def align(shape, lanes):
    if lanes is not None:
        if len(lanes) == 2:
            slopeLeft = slope(lanes[0])
            slopeRight = slope(lanes[1])

            # keep in mind (0,0) is the top left corner and x and y rises down and to the right
            sumSlopeNormalized = -(slopeLeft + slopeRight)
            
            x1L, y1L, x2L, y2L = lanes[0]
            x1R, y1R, x2R, y2R = lanes[1]
            _, bottomEdgeInterceptLeft = lineParameters(shape, x1L, y1L, x2L, y2L)
            _, bottomEdgeInterceptRight = lineParameters(shape, x1R, y1R, x2R, y2R)
            centerOfLane = (bottomEdgeInterceptLeft + bottomEdgeInterceptRight) / 2
            centerOfImage = (shape[1]/2)
            difference = (centerOfLane - centerOfImage)
            if difference > 25:
                if (slopeLeft > 0 and slopeRight > 0):
                    return 0
                elif (slopeLeft < 0 and slopeRight < 0):
                    return 100 / sumSlopeNormalized
                else:
                    return difference / 50
            elif difference < -25:
                if (slopeLeft > 0 and slopeRight > 0):
                    return 100 / sumSlopeNormalized
                elif (slopeLeft < 0 and slopeRight < 0):
                    return 0
                else:
                    return difference / 50
            else:
                if (slopeLeft > 0 and slopeRight > 0) or (slopeLeft < 0 and slopeRight < 0):
                    return 100 / sumSlopeNormalized
                else:
                    return 0

            # print(slopeLeft + slopeRight)

# stop the vehicle at a crosswalk
def stop(crosswalk):
    height = crosswalk.shape[0]
    width = crosswalk.shape[1]
    for i in range(height - 130, height):
        for j in range(int(width//2) - 3, int(width//2) + 3):
            if crosswalk[i][j] == 0:
                return True
    return False

def slope(line):
    x1, y1, x2, y2 = line
    if (x2 - x1) == 0:
        return 100
    return (y2 - y1) / (x2 - x1)

def execute(vid):
    global turnConstant, isRunning
    while(isRunning):
        # Capture the video frame
        # by frame
        ret, frame = vid.read()

        # Display the resulting frame
        cannyEdge = edgeDetection(frame)
        mask = regionOfInterest(cannyEdge)
        mask, crosswalk = removeHorizontal(mask)
        try:
            lineImage, lanes = lineDetection(mask)
            if (stop(crosswalk)):
                print('STOP')
            else:
                turnConstant = align(cannyEdge.shape, lanes)
                print(turnConstant)
            # cv.imshow('line', lineImage)
            # cv.imshow('edge', cannyEdge)
            # cv.imshow('crosswalk', crosswalk)
        except:
            continue

        # the 'q' button is set as the
        # quitting button you may use any
        # desired button of your choice
        # if cv.waitKey(1) & 0xFF == ord('q'):
        #     break

    # After the loop release the cap object
    vid.release()
    # Destroy all the windows
    # cv.destroyAllWindows()

# control the 4 wheels using a steering constant
def steer(turnConstant):
    # negative turnConstant means turn left
    # positive turnConstant means turn right
    pass


def main():
    global turnConstant, isRunning
    isRunning = True

    # # define a video capture object
    # vid = cv.VideoCapture(0)

    # t1 = threading.Thread(target=execute, args=(vid,))
    # t1.start()

    # userInput = input()
    # while userInput != 'q':
    #     userInput = input()
    # isRunning = False

    mc = MotorControl(25,8,7,17,27,22)

    mc.forward(3, speed=1)
    time.sleep(1)
    mc.forward(3, speed=0.5)
    time.sleep(1)
    mc.backward(3, speed=1)
    time.sleep(1)
    mc.backward(3, speed=0.5)
    time.sleep(1)
    mc.turnLeft(1)
    mc.turnRight(1)
    
        

if __name__ == '__main__':
    main()
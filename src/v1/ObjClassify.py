import cv2

class ObjClassify(object):
    def __init__(self):
        self.threshold = 0.56

        self.classNames= []
        classFile = '../../res/coco.names'
        with open(classFile, 'rt') as f:
            self.classNames = f.read().rstrip('\n').split('\n')

        configPath = '../../res/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
        weightsPath = '../../res/frozen_inference_graph.pb'

        self.model = cv2.dnn_DetectionModel(weightsPath, configPath)
        self.model.setInputSize(320,320)
        self.model.setInputScale(1.0/ 127.5)
        self.model.setInputMean((127.5, 127.5, 127.5))
        self.model.setInputSwapRB(True)

    def detect(self, image):
        classIds, confs, bbox = self.model.detect(image,confThreshold=self.threshold)
        objects = []
        if len(classIds) != 0:
            for classId, confidence, box in zip(classIds.flatten(),confs.flatten(),bbox):
                objects.append((self.classNames[classId-1], confidence, box))
        return objects

    def printObj(self, objects):
        for (name, confidence, box) in objects:
            print('Name:', name)
            print('Confidence:', confidence)
            print('Box:', box, '\n')
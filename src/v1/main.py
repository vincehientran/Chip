import cv2
from ObjClassify import ObjClassify



def main():
    objClassify = ObjClassify()

    vid = cv2.VideoCapture(0)
    
    while(True):
        ret, frame = vid.read()

        objects = objClassify.detect(frame)

        for (name, confidence, box) in objects:
            cv2.rectangle(frame, box,(0,0,255),1)
            cv2.putText(frame, name.upper(), (box[0]+10, box[1]+30),
                        cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,255),1)
            
        cv2.imshow('frame', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    vid.release()
    cv2.destroyAllWindows()
    

if __name__ == '__main__':
    main()
import cv2
import numpy as np
from matrixOperations import MatrixOperations
import os

class BodyDetector:

    def __init__(self):
        #print "init"
        RORATION_STEP = 1
        ENABLE_ROTATION =0
        minAngleRange = -5
        maxAngleRange = 5
        face_cascade_name = "haarcascade_frontalface_alt.xml"
        eyes_cascade_name = "haarcascade_eye_tree_eyeglasses.xml"

    def enableRotation(self, rotationStep, range):
        self.ENABLE_ROTATION = 1
        self.ROTATION_STEP = rotationStep
        self.minAngleRange = -1 * range;
        self.maxAngleRange = range


    def getFace(self, image, angle, count, eye, path):
        totalfaces = []
        frame_gray  =cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        frame_gray = cv2.equalizeHist(frame_gray)
        rotFrame_gray = frame_gray.copy()

        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')

        eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')



        faces = face_cascade.detectMultiScale(frame_gray, 1.1,3)

        if self.ENABLE_ROTATION:
            maxIter = 3
            while maxIter > 0:
                sign = -1
                inc = self.ROTATION_STEP
                if (hasattr(faces, 'size')):
                    while faces.size == 0:
                        frame_gray =  MatrixOperations.rotateImage(rotFrame_gray, rotFrame_gray, angle)
                        faces = face_cascade.detectMultiScale(frame_gray, 1.1,3)
                        angle = angle+ (self.ROTATION_STEP * sign * inc)
                        sign = sign* -1
                        inc=inc+1
                angle = angle+ (self.ROTATION_STEP * sign * inc)
                sign = sign* -1
                inc=inc+1
                maxIter = maxIter - 1
            for(x,y,w,h) in faces:
                x = x-20
                y = y-20
                w = w+40
                h= h+40
                #cv2.rectangle(image, (x,y), (x+w, y+h), (255,0,0), 2)
                roi_gray = frame_gray[y:y+h, x:x+w]
                roi_color = image[y:y+h, x:x+w]
                totalfaces.append(roi_color)
        else:
            faces = face_cascade.detectMultiScale(frame_gray, 1.1,3, 0, (30, 30))


        #cv2.imshow('image', image)
        #cv2.waitKey(0)

        #saving images
        facePath = path + "/Faces"

        if not os.path.exists(facePath):
            os.makedirs(facePath)


        for i in range(0, len(totalfaces)):
            facePath1 = facePath + '/Face_'
            cv2.imwrite(facePath1+str(i)+".jpg", totalfaces[i])

        return faces






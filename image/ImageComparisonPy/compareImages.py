import numpy as np
import cv2
import sys
from edgeDetector import EdgeDetector

def compare(fileNameA, fileNameB):
    try:

            imgA = cv2.imread(fileNameA)
            imgB = cv2. imread(fileNameB)
            edgeDetector = EdgeDetector()

            #first remove black borders
            #imgA = edgeDetector.removeBorder(imgA)
            #imgB = edgeDetector.removeBorder(imgB)

            hA, wA = imgA.shape[:2]
            hB, wB = imgB.shape[:2]
           # print imgA.shape
            #print imgB.shape

            #cv2.imshow('w1', imgA)
            #cv2.imshow('w2', imgB)
            #cv2.waitKey(0)

            sizeA = wA * hA
            sizeB = wB * hB
            #print wA, hA, wB, hB

            if sizeA > sizeB:
                imgA = cv2.resize(imgA,  (wB, hB), interpolation=cv2.INTER_CUBIC)
            else:
                if sizeB > sizeA:
                    imgB = cv2.resize(imgB, (wA, hA), interpolation=cv2.INTER_CUBIC)
                else:
                    if wA!= wB:
                        imgB = cv2.resize(imgB, (wA, hA), interpolation=cv2.INTER_CUBIC)


            output = edgeDetector.compareTwoImage(imgA, imgB)
            #print "output ", output
            #print output
            return output
    except:
        #print sys.exc_info()[0]
        #print -2
        return -2



import numpy as np
import cv2
import sys
import os
from BodyDetector import BodyDetector


def main():
    myBodyDetector = BodyDetector()
    try:

            if len(sys.argv) >1:
                fileName = sys.argv[1];


                img = cv2.imread(fileName)

                path1 = fileName.split('.')[0]+'.txt'
                imageInfo = open(path1, 'w')
                path = os.path.split(os.path.abspath(fileName))[0]
                #print path

                #filewrite = open(path,'w')
                myBodyDetector.enableRotation( 1 ,45)
                totalfaces = myBodyDetector.getFace(img, 45,0,1,path)

                imageInfo.write(str(len(totalfaces)) + "\n")
                for (x,y,w,h) in totalfaces:
                    line = str(x)+" "+str(y)+" "+str(w)+" "+str(h)
                    imageInfo.write(line+"\n")



    except:
        print sys.exc_info()
        print -2
        return -2

if __name__ == "__main__":
    return_value= main()

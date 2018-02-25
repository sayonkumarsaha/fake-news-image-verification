import cv2


class MatrixOperations:

    def __init__(self):
        print ""

    def rotateImage(self, fromI,  fromroi, angle):
        rows, cols = fromroi.shape
        cx = (rows/2, cols/2)
        R = cv2.getRotationMatrix2D(cx, angle, 1)



        toI = cv2.warpAffine(fromI, R, (cols, rows))
        return  toI


    #def rotatedImageBB(self,R, bb):

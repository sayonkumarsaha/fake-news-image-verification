from imageDetector import ImageDetector
import numpy as np
import cv2
import pylab
import time

class EdgeDetector:

    def __init__(self):
        self.lowThreshold = 100
        self.maxThreshold = 3* self.lowThreshold
        self.kernelSize = 30
        self.count = 0


    def compareTwoImage(self, imgA, imgB):
        #cv2.imshow('w1', imgA)
        #cv2.imshow('w2', imgB)
        #cv2.waitKey(0)

        hA, wA = imgA.shape[:2]
        hB, wB = imgB.shape[:2]
        #print wA, hA, wB, hB

        imgDetector = ImageDetector(imgA, imgB)
        aDiff = imgA.copy()
        bDiff = imgA.copy()

        #add blur
        cv2.medianBlur(imgA, 9, aDiff)
        cv2.medianBlur(imgB, 9, bDiff)


        result =0
        kernelSize = 30

        #convert to grey scale
        aGray = cv2.cvtColor(aDiff, code= cv2.COLOR_BGR2GRAY)
        bGray = cv2.cvtColor(bDiff, code= cv2.COLOR_BGR2GRAY)
        #print type(aGray), type(aGray[0,0])

        ##cv2.imwrite('imgAGray.jpg', aGray)
        #cv2.imwrite('imgBGray.jpg', bGray)
        #cv2.imshow('imgA', aGray)
        #cv2.imshow('imgB', bGray)
        #cv2.waitKey(0)
        #added step to convert first to binary then get difference

        #thr, aGrayBi = cv2.threshold(aGray.copy(), 20, 255, cv2.THRESH_BINARY)
        #thr, bGrayBi = cv2.threshold(bGray, 20, 255, cv2.THRESH_BINARY)
        #imgDiffBi = aGrayBi -  bGrayBi


        #aGray = np.array(aGray, dtype=float)
        #bGray = np.array(bGray, dtype=float)
        #imageDiff = aGray - bGray
        imageDiff = cv2.absdiff(aGray, bGray)
        #print "reg diff", imageDiff.sum()

        #print imageDiff.min(), imageDiff.max()
        #imageDiff = (imageDiff - imageDiff.min())/(imageDiff.max() - imageDiff.min())
        #imageDiff = imageDiff*255
        #imageDiff = np.array(imageDiff, dtype=int)
        #print imageDiff.min(), imageDiff.max()
        #print imageDiff
        #cv2.imshow('difference', imageDiff)
        #cv2.imwrite('imgDiff.jpg', imageDiff)

        #pylab.matshow(imageDiff, cmap='Greys_r')
        #pylab.show()
        #cv2.waitKey(0)

        #morphological operation
        dilation_size = 1

        element = cv2.getStructuringElement(cv2.MORPH_RECT, (2*dilation_size+1, 2*dilation_size+1),(dilation_size, dilation_size))

        imageDiff = cv2.morphologyEx(imageDiff, cv2.MORPH_OPEN, element)
        thr, imageDiff = cv2.threshold(imageDiff, 20, 255, cv2.THRESH_BINARY)


        #cv2.imshow('morph. operator', imageDiff)
        #cv2.imwrite('morphImg.jpg', imageDiff)
        #cv2.waitKey(0)

        sum = imageDiff.sum()

        #print (1.0*sum)/aGrayBi.sum()
        #if (1.0*sum)/aGrayBi.sum() > 0.9:
        #   print "images are not related"
        #    return -1
        if sum == 0:
            return 0
            #print "result 0%"
            #exit(0)

        #self.compareImgHistogramEdge(imgA, imgB)

        (result, edgeImgA, edgeImgB) = self.compareImgPreEdge(imgDetector, self, self.kernelSize)
        cv2.imwrite('edgeImgA.jpg', edgeImgA)
        cv2.imwrite('edgeImgB.jpg', edgeImgB)
        #case 1
        if result in range(0, 10):
            return 0
        if result > 80:
            #print "images are altered ", result
            return 1
            #print "images match and not altered"
            #exit(0)

        #case 2
        _, imgEdgeThrA = cv2.threshold(edgeImgA,  0.5, 255, cv2.THRESH_BINARY)
        _, imgEdgeThrB = cv2.threshold(edgeImgB,  0.5, 255, cv2.THRESH_BINARY)

        edgImgADest = edgeImgA.copy()
        edgeImgBDest = edgeImgB.copy()

        imgDetector.setImages(edgImgADest, edgeImgBDest)

        imgDetector.contains()

        needle = imgDetector.getImageNeedle()
        haystack = imgDetector.getImageHaystack()

        cv2.imwrite('edgeImgA2.jpg', needle)
        cv2.imwrite('edgeImgB2.jpg', haystack)

        #needle = self.scaleto1(needle)
        #haystack = self.scaleto1(haystack)



        result2 = self.checkMatchSimilarity(needle, haystack, self.kernelSize)
        output = 0
        #if result2 > 80:
        #    print "images are not equal", result, result2
        #    output = 2
        if result2 < result:
            #print "images match", result, result2
            output = 0
        else:
            #print "images might have been altered", result, result2
            output = 1
        return output


    def compareImgHistogramEdge(self,img1, img2):
        imagedet = ImageDetector(img1, img2)
        imagedet.isEqual(img1, img2)

    #checking method is not convincing. Needs review
    def checkMatchSimilarity(self, a, b, filter):
        hA, wA = a.shape[:2]
        #print hA, wA

        t=0
        tt=0


        for i in range(0, hA-filter, filter):
            for j in range(0, wA-filter, filter):
                #print i, j, wA-filter, hA-filter
                tmpa = np.matrix(a[i: i+filter, j: j+filter])
                tmpb = np.matrix(b[i:i+filter, j:j+filter])
                tmpSum = np.sum(tmpa, dtype=np.int64) - np.sum(tmpb, dtype=np.int64)
                #tSum = cv2.absdiff(tmpa, tmpb)#tmpa - tmpb
                #if(tSum.sum() > 0):

                tt= tt+abs(tmpSum)#tSum.sum()
                if(tmpSum >0):
                    t = t+tmpSum


        totaledge = a.sum() + b.sum()

        #s = a - b
        #print (s.sum()*1.0) / a.sum()
        result = (tt/a.sum())*100

        #print totaledge, result

        totaldiff = cv2.absdiff(a,b)
        #print totaldiff.sum(), a.sum(), b.sum()

        #result = ((1.0*totaldiff.sum())/a.sum())*100
        return result
        #exit(0)
        #s = [np.matrix(a[i:i+filter, j:j+filter]).sum()  for i in range(0, wA-filter) for j in  range(0, hA - filter, filter) ]
        #t = [np.matrix(b[i:i+filter, j:j+filter]).sum() for i in range(0, wA-filter) for j in  range(0, hA - filter, filter) ]

        #r = [s_i - t_i for s_i, t_i in zip(s, t) if s_i > t_i and s_i - t_i > 0]

        #print r
        #print st
        #time.sleep(10)
        #r = [st[i] for i in range(0, len(st)) if st[i] > 0]
        #print len(r), len(s), len(a)
        #t = [(np.matrix(a[i:i+filter, j:j+filter]).sum() -  np.matrix(b[i:i+filter, j:j+filter]).sum()) for i in range(0, wA-filter) for j in  range(0, hA - filter) ]
        #t = [(np.matrix(a[i: i+filter, j: j+filter])).sum()  - (np.matrix(b[i:i+filter, j:j+filter])).sum() for i in range(0, wA-filter) for j in  range(0, hA - filter)]
        #totalEdge = a.sum() + b.sum()
        #print "totaledge", totalEdge
        #print "edge difference ", sum(r)
        #result = (sum(r)/ a.sum())* 100;
        #print "percentage of mismatch", result
        #return result



    def compareImgPreEdge(self, imgDetector, edgeDetector, kernelSize):
        needle = imgDetector.getImageNeedle()
        haystack = imgDetector.getImageHaystack()

        edgeImgA = edgeDetector.getEdgeImage(needle)
        edgeImgB = edgeDetector.getEdgeImage(haystack)

        thresh1, edgeImgADisplay = cv2.threshold(edgeImgA, 0.5, 255, cv2.THRESH_BINARY)
        thresh2, edgeImgBDisplay = cv2.threshold(edgeImgB, 0.5, 255, cv2.THRESH_BINARY)

        #cv2.imshow("imgA contors", edgeImgADisplay)
        #cv2.waitKey(0)


        result = self.checkMatchSimilarity(edgeImgA, edgeImgB, kernelSize)

        return (result, edgeImgA, edgeImgB)


    def getEdgeImage(self, img):
        imgBlur = cv2.blur(img, (3,3))
        detected_edges = cv2.Canny(imgBlur, self.lowThreshold, self.maxThreshold, self.kernelSize)
        return detected_edges



    def removeBorder(self, img):
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        #v2.imshow('w', gray)
        #cv2.waitKey(0)
        _,thresh = cv2.threshold(gray,1,255,cv2.THRESH_BINARY)
        #print thresh
        imTmp, contours,hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        #cv2.drawContours(img, contours, 0, (0,255,0), 3)
        #cv2.imshow('cont', img)
        #cv2.waitKey(0)
        #print contours
        #if len(contours) >1:
        #    contours.sort(key=lambda x: x[0])
        #    print contours

        cnt = contours[0]
        x,y,w,h = cv2.boundingRect(contours[0])
        #print x,y,w,h
        area = 0
        for i in range(0, len(contours)):
            a, b, c, d = cv2.boundingRect(contours[i])
            new_area = c*d
            if area < new_area:
                area = new_area
                x = a
                y = b
                w = c
                h = d
        #print x,y,w,h

        crop = img[y:y+h,x:x+w]
        #cv2.imshow('cont', crop)
        #cv2.waitKey(0)
        return crop

    def scaleto1(self, img):
        _, imgTh = cv2.threshold(img, 0.5, 1, cv2.THRESH_BINARY)
        return imgTh
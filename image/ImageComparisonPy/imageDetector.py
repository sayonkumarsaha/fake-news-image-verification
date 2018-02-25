import numpy as np
import cv2
from matplotlib import pyplot as plt

class ImageDetector:
    #print "class"

    def __init__(self, needle, haystack):
        self.needle = needle
        self.haystack = haystack
        self.__good_machtes = []
        self.__keypointsA = []
        self.__keypointsB = []


    def getImageNeedle(self):
        return self.needle

    def getImageHaystack(self):
        return self.haystack

    def contains(self):
        if len(self.needle.shape) == 3:
            needleGray = cv2.cvtColor(self.needle, None, cv2.COLOR_BGR2GRAY)
        else:
            needleGray = self.needle.copy()
        if len(self.haystack.shape) == 3:
            haystackGray = cv2.cvtColor(self.haystack, None, cv2.COLOR_BGR2GRAY)
        else:
            haystackGray = self.haystack.copy()


        #cv2.imshow('hay1', haystackGray)
        #cv2.waitKey(0)

        #cv2.imshow('hay', haystackGray)
        #cv2.waitKey(0)

        #cv2.imshow('need', needleGray)
        #cv2.waitKey(0)

        minHessian = 400
        surf = cv2.xfeatures2d.SURF_create(minHessian, upright=True)
        kp1, des1 = surf.detectAndCompute(needleGray, None)
        kp2, des2 = surf.detectAndCompute(haystackGray, None)

        # FLANN parameters
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks=50)   # or pass empty dictionary

        flann = cv2.FlannBasedMatcher(index_params, search_params)

        matches =flann.knnMatch(des1,des2,k=2)

        good = []
        for m,n in matches:
            if m.distance < 0.7*n.distance:
                good.append(m)

        MIN_MATCH_COUNT = 10

        #print len(good)
        if len(good)>MIN_MATCH_COUNT:
            srcp = np.float32([ kp1[m.queryIdx].pt for m in good ])
            #print srcp
            src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
            #print src_pts
            dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
            matchesMask = mask.ravel().tolist()
            #print M


            #transform the image
            h,w = needleGray.shape
            pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
            dst = cv2.perspectiveTransform(pts,M)


            #print np.int32(dst)
            haystackOrgGray = haystackGray.copy()
            haystackGray = cv2.polylines(haystackGray,[np.int32(dst)],True,255,3, cv2.LINE_AA)
            haystackGray = cv2.polylines(haystackGray,[np.int32(pts)],True,255,1, cv2.LINE_AA)
        #else:
            #print "too little points"


        draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                   singlePointColor = None,
                   matchesMask = matchesMask, # draw only inliers
                   flags = 2)


        img3 = cv2.drawMatches(needleGray,kp1,haystackGray,kp2,good,None,**draw_params)
        #cv2.imshow('w', img3)
        #cv2.waitKey(0)

        pts1 = np.float32([[0,0],[w,0],[0,h],[w,h]])

        pts2 = np.float32([dst[0][0], dst[3][0], dst[1][0], dst[2][0]])#[[106,40],[58,284], [464, 287], [424, 70]])
        ##print pts1
        #print pts2
        M1 = cv2.getPerspectiveTransform(pts2,pts1)

        newImg = cv2.warpPerspective(haystackOrgGray,M1,(w,h))

        ##cv2.imshow('newimg', newImg)
        ##cv2.imshow('needle', needleGray)
        #cv2.waitKey(0)

        #cv2.imshow('hay', haystackGray)
        #cv2.waitKey(0)

        #cv2.imshow('need', needleGray)
        #cv2.waitKey(0)
        self.setImages(needleGray, newImg)
        #self.alignImage(kp1,kp2, good, haystackGray)
        #max_dist = 0;
        #min_dist = 100;

        #print des1
        #print [x.distance for x in matches[0:]]

    def alignImage(self, kp1, kp2, m, img):
        a = kp1[m[3].queryIdx].pt
        b = kp2[m[3].trainIdx].pt
        #print a,b
        c = np.subtract(a,b)
        #print c
        #translateNeedle = \
        self.translateImg(c[0], c[1], img)

    def translateImg(self, x , y, img):
        m = np.array([1,0])
        n = np.array([0,1])
        m = np.append(m, x)
        n = np.append(n, y)
        m = np.append(m,n)
        m = np.reshape(m, (2,3))
        #print m
        cols,rows = img.shape
        res = cv2.warpAffine(img, m, (rows, cols))
        #cv2.imshow('transformed', res)
        #cv2.waitKey(0)
        return res

    def setImages(self, a, b):
        self.needle = a
        self.haystack = b



    def isEqual(self, img1, img2):
        print "euqal comparison"
        minHessian = 400
        surf = cv2.xfeatures2d.SURF_create(minHessian, upright=True)



        #surf.upright = True

        kp1, des1 = surf.detectAndCompute(img1, None)
        kp2, des2 = surf.detectAndCompute(img2, None)

        imgt = cv2.drawKeypoints(img2,kp2,None,(255,0,0),4)

        cv2.imshow('w', imgt)
        cv2.waitKey(0)
        print len(kp2)

        # FLANN parameters
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks=50)   # or pass empty dictionary

        flann = cv2.FlannBasedMatcher(index_params, search_params)

        matches = flann.knnMatch(des1,des2,k=2)

        # Need to draw only good matches, so create a mask
        matchesMask = [[0,0] for i in xrange(len(matches))]

        # ratio test as per Lowe's paper
        for i,(m,n) in enumerate(matches):
            if m.distance < 0.7*n.distance:
                matchesMask[i]=[1,0]

        img3 = np.array([])

        draw_params = dict(matchColor = (0,255,0),
                           singlePointColor = (255,0,0),
                           matchesMask = matchesMask,
                           flags = 0)


        img3 = cv2.drawMatchesKnn(img1,kp1,img2,kp2,matches,None,**draw_params)


        #plt.imshow(img3,),plt.show()
        #cv2.imshow('w', img3)
        #cv2.waitKey(0)
        distances = [x[1].distance for x in matches]
        print distances
        min_dist = min(distances)
        good = [x for x in distances if (x<= 2*min_dist)]
        print good
        print len(good)
        check = (len(good) / len(kp1) * 0.5) + (len(good) / len(kp2) * 0.5)
        print check


    def isEqualHistogram(self, img1, img2):
        #calculate 2-dim histogram to incode color information
        print "eqaul"

        hsvA = cv2.cvtColor(img1,  cv2.COLOR_BGR2HSV)
        hsvB  = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)

        h_bins = 50
        s_bins = 60
        histSize = [h_bins, s_bins]

        h_ranges = [0, 256]
        s_ranges = [0, 180]

        channels = [0,1]

        hist_base = cv2.calcHist([hsvA], [0, 1], None, histSize, h_ranges+s_ranges)
        hist_base = cv2.normalize( hist_base, None, 0, 1, cv2.NORM_MINMAX, -1);


        hist_test = cv2.calcHist([hsvB], [0, 1], None, histSize, h_ranges+s_ranges)
        hist_test = cv2.normalize( hist_test, None, 0, 1, cv2.NORM_MINMAX, -1);

        for i in range(0,4):
            base_base = cv2.compareHist(hist_base, hist_base, i)
            base_test = cv2.compareHist(hist_base, hist_test, i)
            print("method ",i,"base half", base_base, "base test", base_test)

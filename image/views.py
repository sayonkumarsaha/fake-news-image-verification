# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from image.models import Image, Article

from django.http import HttpResponse, JsonResponse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
import hashlib, urllib, json
import datetime
import logging
import sys
import kmeansScript as kmean
from ImageComparisonPy.compareImages import compare
import urllib2
from BeautifulSoup import BeautifulSoup
import xml.etree.cElementTree as ET
import subprocess
from PIL import Image
import base64
from pprint import pprint
import requests

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

THUMBNAIL_SIZE = [125, 125]
MAX_NUMBER_OF_IMAGES_TO_COMPARE = 10

"""
Change the following local path as per requirement.
"""
IMAGE_SAVE_PATH = "/media/sayon/data/alldata/workspace/tempDump/"
XML_SAVE_PATH= "/media/sayon/data/alldata/workspace/newsverifier/web/carrot2-cli-3.11.0/input/"

"""
Temporary JSON string till the issue of empty JSON List being returned randomly is fixed
"""
TESTJSON_RELATED_IMAGES=[{
                               u'sourceUrl': u'https%3A%2F%2Fwww.pinterest.com%2Fdavidsonluna%2Fdilbert%2F&docid=7pW4fFfB0nHSWM&tbnid=ksUsh5sjLNEIsM%3A&vet=10ahUKEwj6g7W96O3UAhUDUBQKHW-_DSwQMwjyASgAMAA..i',
                               u'pageUrl': u'https%3A%2F%2Fs-media-cache-ak0.pinimg.com%2F736x%2F79%2Fea%2Fec%2F79eaec5b39a6cdebd68862b85db493b0--desk-calendars-su.jpg'
                             },
                             {
                               u'sourceUrl': u'http%3A%2F%2Fwww.andrewsmcmeel.com%2Fcatalog%2Fdetail%3Fsku%3D9781449465155&docid=FZdk3tE7kZUw5M&tbnid=hMZqp1SSpssdOM%3A&vet=10ahUKEwj6g7W96O3UAhUDUBQKHW-_DSwQMwj1ASgDMAM..i',
                               u'pageUrl': u'http%3A%2F%2Fwww.andrewsmcmeel.com%2Fimages%2Fdefault-source%2Fcatalog%2F9781449465155_frontcover.jpg%3FStatus%3DMaster%26sfvrsn%3D0'
                             }]






"""
Note: Disabled Cross Site Request Forgery (CSRF) protection to get the request running. Temporary Solution.
"""
@csrf_exempt
def detectImageAction(request):
    """
        detectImageAction: takes request as sent from the Extension containing following parameters:
        - requestID: a generated ID per request send from the extension to handle the correct response
        - image: URL of original image
        Downloads the image from the url, performs face extraction and returns the extracted face information.
    """
    reqId = request.POST['requestID']

    imageFilename = "RequestId_" + reqId + "_detectImage.jpg"
    imageUrl= urllib2.unquote(request.POST['image'])
    imageFile = IMAGE_SAVE_PATH + imageFilename
    urllib.urlretrieve(imageUrl, imageFile)

    imageWidth, imageHeight = getImageSize(imageFile)
    pedestrians, faces= detectFaces(imageFile)

    response_data = {}
    response_data['pedestrians'] = pedestrians
    response_data['faces'] = faces
    response_data['width'] = imageWidth
    response_data['height'] = imageHeight

    print (json.dumps(response_data, indent=5))
    return JsonResponse(response_data)

def getImageSize(filePath):
    resolution = Image.open(filePath).size
    return resolution[0], resolution[1]

def detectFaces(imageFile):

    FACE_DETECTOR_TOOL_PATH = "FaceDetector/"
    faceDetectionProcess = subprocess.Popen("cd " + FACE_DETECTOR_TOOL_PATH
                                            + ";"
                                            + "python main.py" + " " + imageFile,
                                            shell=True)
    faceDetectionProcess.wait()
    outputFaceInfoFilePath = imageFile.split('.')[0] + '.txt'
    with open(outputFaceInfoFilePath) as f:
        outputFaceInfo = f.readlines()
    outputFaceInfo = [x.strip() for x in outputFaceInfo]

    totalFaces= outputFaceInfo.pop(0)
    faces=[]
    faceNumber=0
    for face in outputFaceInfo:
        facePath= IMAGE_SAVE_PATH+"/Faces/Face_"+str(faceNumber)+".jpg"
        currFace = {}
        currFace['x'] = face.split()[0]
        currFace['y'] = face.split()[1]
        currFace['width'] = face.split()[2]
        currFace['height'] = face.split()[3]
        currFace['location'] = ""
        currFace['img_loc'] = facePath
        currFace['img_url'] = uploadAndGetUrl(facePath)
        faces.append(currFace)
        faceNumber=faceNumber+1

    #TODO: Extract Pedestrians
    pedestrians=""

    return pedestrians, faces

#TODO: Upload Image to an external server or internal DFKI server and get URL for Reverse Image Search
def uploadAndGetUrl(imagePath):
    imageUrl="dummy url"
    return imageUrl

"""
Note: Disabled Cross Site Request Forgery (CSRF) protection to get the request running. Temporary Solution.
"""
@csrf_exempt
def compareImageAction(request):
    """
        CompareImageAction: takes request as sent from the Extension containing following parameters:
        - requestID: a generated ID per request send from the extension to handle the correct response
        - original_image: URL of original image
        - images: contains encoded URLs of top 10 results from image reverse search
    """
    #TODO: Separate the textClustering functionality when the new URL ready at Javascript side
    textClustering=True

    reqId = request.POST['requestID']
    originalImageFilename = "RequestId_" + reqId + "_originalImage.jpg"

    originalImageUrl = request.POST['original_image']
    originalImageFile = downloadImage(originalImageUrl, originalImageFilename)

    #TODO: Fix the issue of empty JSON List being returned randomly
    jsonImages = json.loads(urllib2.unquote(request.POST['images']))
    if not jsonImages:
        logger.warning("Proceeding with dummy version: Empty list of Related Images!")
        jsonImages=TESTJSON_RELATED_IMAGES

    if (textClustering):
        root = ET.Element("searchresult")
        ET.SubElement(root, "query").text = "default query"

    xmlFileName = "RequestId_" + reqId + "_pageInfo"

    similarityScoreList = []
    relatedPageUrlList = []
    relatedImageUrlList = []
    numOfImagesCompared = 0

    for singleImage in jsonImages:

        relatedImageUrl = urllib2.unquote(singleImage.get('pageUrl'))
        relatedPageUrl = urllib2.unquote(singleImage.get('sourceUrl'))
        relatedImageUrlList.append(relatedImageUrl)
        relatedPageUrlList.append(relatedPageUrl)
        relatedImageFilename = "RequestId_" + reqId \
                               + "_relatedImage_" + str(numOfImagesCompared + 1) \
                               + ".jpg"
        try:
            if (textClustering):
                pageTitle, pageDescription = getPageTitleAndDescription(relatedPageUrl)
                doc = ET.SubElement(root, "document")
                ET.SubElement(doc, "title").text = pageTitle
                ET.SubElement(doc, "snippet").text = pageDescription.decode('utf-8')
                ET.SubElement(doc, "url").text = relatedPageUrl
                ET.ElementTree(root).write(XML_SAVE_PATH + xmlFileName+".xml")

            downloadPath=IMAGE_SAVE_PATH + relatedImageFilename
            urllib.urlretrieve(relatedImageUrl, downloadPath)
            similarityScoreList.append(compare(originalImageFile, downloadPath))

            numOfImagesCompared = numOfImagesCompared + 1

        except Exception:
            logger.warning('Could not open an URL. Ignored and proceeding!')
            pass

        logger.info("Compared %s images successfully!" % str(numOfImagesCompared))
        if numOfImagesCompared == MAX_NUMBER_OF_IMAGES_TO_COMPARE:
            break

    if (textClustering):

        """
        Change the following local path as per requirement.
        """
        #TODO: Change the absolute URLs into Relative URLs as per the path in the repository
        SCRIPT_FILE_PATH = "/media/sayon/data/alldata/workspace/newsverifier/web/carrot2-cli-3.11.0/"
        SCRIPT_FILE_NAME = "batch.sh"
        XML_INPUT_PATH = "/media/sayon/data/alldata/workspace/newsverifier/web/carrot2-cli-3.11.0/input/"
        JSON_OUTPUT_PATH = "/media/sayon/data/alldata/workspace/newsverifier/web/carrot2-cli-3.11.0/output/"

        compareResult = json.dumps(
                            {'requestId': reqId,
                             'originalImageUrl': originalImageUrl,
                             'relatedImageUrls': relatedImageUrlList,
                             'relatedPageUrls': relatedPageUrlList,
                             'similarityScores': similarityScoreList,
                             'clusters': getTextClusters(SCRIPT_FILE_PATH,
                                                         SCRIPT_FILE_NAME,
                                                         XML_INPUT_PATH,
                                                         xmlFileName,
                                                         JSON_OUTPUT_PATH)
                             }, indent=5)
    else:
        compareResult = json.dumps(
                            {'requestId': reqId,
                             'originalImageUrl': originalImageUrl,
                             'relatedImageUrls': relatedImageUrlList,
                             'relatedPageUrls': relatedPageUrlList,
                             'similarityScores': similarityScoreList
                            }, indent=5)
    print (compareResult)
    return JsonResponse(compareResult, safe=False)

def getTextClusters(scriptPath, scriptFileName, inputPath, inputFileName, outputPath):

    changeDirectoryCommand = "cd " + scriptPath
    bashFileExecutionCommand = "sh " + scriptFileName + " " \
                               + inputPath + inputFileName + ".xml" \
                               + " -f JSON -t -o " + outputPath
    clusteringProcess = subprocess.Popen(
                                    changeDirectoryCommand + ";" + bashFileExecutionCommand,
                                    shell=True)
    clusteringProcess.wait()

    outputFileName= inputFileName+".json"
    clusteredOutput = json.loads(open(outputPath+outputFileName).read())

    return clusteredOutput["clusters"]

#TODO: Possible Issue: raise HTTPError: HTTP Error 404: Not Found
def downloadImage(imageSource, imgFilename):
    downloadPath = IMAGE_SAVE_PATH + imgFilename
    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}
    imageDownloadRequest = urllib2.Request(imageSource, headers=hdr)
    imageDownloadResponse= urllib2.urlopen(imageDownloadRequest).read()
    with open(downloadPath, 'wb') as out:
        out.write(imageDownloadResponse)
    return downloadPath

def getPageTitleAndDescription(url):
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    pageTitle = soup.find('title').renderContents()
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.getText()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    pageDescription = text.encode('utf-8')
    return pageTitle, pageDescription







"""
Note: Disabled Cross Site Request Forgery (CSRF) protection to get the request running. Temporary Solution.
"""
@csrf_exempt
def clusterAction(request):
    """
       Populating the Article table in the DB with the request data received.
       Request parameters:
       - json: Json text of related images in form of Json objects
       - firstDate: first appearance of the image (in form of Unix timestamp
       - tag: associated tags with the image from Google
       - image: image URL
       - articleUrl: article URL
       - pubDate: date of publish of the article
       - requestID: unique ID associated with the request (intended to handle multiple users)
    """
    requestID = request.POST['requestID']

    dateList = []
    articleList = []

    imageOfArticleUrlHash = getMd5(request.POST['image'])
    if not Article.objects.filter(articleImageUrlHash=imageOfArticleUrlHash).exists():

        article = addNewArticle(request, imageOfArticleUrlHash)
        logger.info('Article: Added to the DB successfully!')
        relatedImages = json.loads(urllib.unquote_plus(request.POST['json']))

        for image in relatedImages:

            if image.get('date'):
                relatedImageUrlHash = getMd5(image.get('imageUrl'))
                if not (Image.objects.filter(imageUrlHash=relatedImageUrlHash)).exists():
                    addNewRelatedImage(article, image, relatedImageUrlHash)
                    logger.info('Related Image: Added to the DB successfully!')
                else:
                    logger.info('Related Image: Already exists in the DB!')

                dateList.append(str(Image.objects.get(imageUrlHash=relatedImageUrlHash).date))
                articleList.append(str(Image.objects.get(imageUrlHash=relatedImageUrlHash).pageUrl))

            else:
                logger.warning('Related Image: Ignored. Missing associated date!')

    else:
        logger.info('Article: Already exists in the DB!')
        existingArticle = Article.objects.get(articleImageUrlHash=imageOfArticleUrlHash)
        relatedImages = Image.objects.filter(relatedImage=existingArticle)
        for image in relatedImages:
            dateList.append(str(image.date))
            articleList.append(str(image.pageUrl))

    clusteredOutput = kmean.run(dateList, articleList)

    response_data = {}
    response_data['image'] = ""
    response_data['date'] = clusteredOutput
    response_data['firstDate'] = str(datetime.datetime.fromtimestamp(float(request.POST['firstDate']) / 1000))
    response_data['requestID'] = requestID
    return JsonResponse(response_data)

def updateKMeanInput(dateList, date, articleList, articleUrl):
    return dateList.append(str(date)), articleList.append(str(articleUrl))

def getMd5(string):
    return (hashlib.md5(string.encode('utf-8')).hexdigest())







def addNewArticle(articleRequest, imageOfArticleUrlHash):
    """
    Populating the Article table in the DB with the request data received.
    """
    articleData = Article()
    articleData.url = articleRequest.POST['articleUrl']
    articleData.articleImage = articleRequest.POST['image']
    articleData.articleImageUrlHash = imageOfArticleUrlHash
    articleData.date = datetime.datetime.strptime((articleRequest.POST['pubDate'].split(' ')[0]), '%m/%d/%Y').strftime(
        '%Y-%m-%d')
    # TODO: Fix consistency of data retrieval
    """
    Issue: ValueError: could not convert string to float. Fails for some URLs like the following:
    https: // www.theregister.co.uk / 2017 / 04 / 04 / google_opens_patent_pool_for_android /
    https://www.theregister.co.uk/2017/06/14/labour_will_vote_against_bbc_tv_licence_changes/
    """
    articleData.firstDateRetrieved = datetime.datetime.fromtimestamp(float(articleRequest.POST['firstDate']) / 1000)
    # TODO: articleData.text = articleRequest.POST['article']
    articleData.tags = articleRequest.POST['tag']
    articleData.save()
    return articleData







def addNewRelatedImage(article, imageInfo, imageUrlHash):
    """
        Populating the Image table in the DB with the related images information.
        It is parsed from the JSON received in the request data for a given article.
    """
    imageData = Image()
    imageData.imageUrlHash = imageUrlHash
    #TODO: RuntimeWarning: Naive datetime received while time zone support is active.
    imageData.date = datetime.datetime.fromtimestamp(float(imageInfo.get('date')) / 1000)
    imageData.imageUrl = imageInfo.get('imageUrl')
    imageData.pageUrl = imageInfo.get('pageUrl')
    imageData.resolutionX = imageInfo.get('resX')
    imageData.resolutionY = imageInfo.get('resY')
    imageData.thumbnail = isThumbnail(imageInfo.get('resX'), imageInfo.get('resY'))
    imageData.relatedImage = article
    imageData.save()

def isThumbnail(resX, resY):
    return (int(resX) <= THUMBNAIL_SIZE[0] and int(resY) <= THUMBNAIL_SIZE[1])
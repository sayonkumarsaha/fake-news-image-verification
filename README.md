# fake-news-image-verification-experiment

## Only a part of the entire source code:
This repository contains only a part of the source code. It is not expected to run locally. It is part of a project dealing with detecting fake news articles based on screening morphed or fake images.

## Clustering similar images on the web:
In order to fetch similar images on the web for a given image, google reverse search techniques is used. Meta information from all the closest images are extracted. K-means clustering is used to further cluster most similar images from the pool. Images are compares using techniques such as image historgarm, edge detectors, and some other openCV image processing methodologies. 

## Extracting faces in the image to verify article
Face detection in images are done by re-using stump-based adaboost frontal face detector and tree-based 20x20 frontal eye detector. The extracted faces are further searched on the web to extract meta information about the person and compare it with the mentions in the news article text for verification.
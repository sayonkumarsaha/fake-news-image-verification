# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models

"""
The model to store the article information.
"""
class Article(models.Model):
    id = models.AutoField(primary_key=True)
    #tag/tags associated with the article image from Google RIS
    tags = models.CharField(max_length=255, null=True, default="defaultTag")
    #TODO: text of article?
    text = models.CharField(max_length=255, null=False, default="defaultText")
    #source URL of article
    url = models.CharField(max_length=2048, null=False, default="defaultUrl")
    #url of the image in article
    articleImage = models.CharField(max_length=2048, null=False, default="defaultImage")
    articleImageUrlHash = models.CharField(max_length=2048, null=False, default="defaultArticleImageUrlHash")
    #date published of article
    date = models.DateField()
    #the first appearance of the image in the the article over the internet (supposedly)
    firstDateRetrieved = models.DateField()

    class Meta:
        db_table = "article"

"""
The model to store information about related images to the image in article
"""
class Image(models.Model):
    id = models.AutoField(primary_key=True)
    imageUrl = models.CharField(max_length =2048)
    imageUrlHash = models.CharField(max_length=2048, null=False, default="defaultImageUrlHash");
    pageUrl = models.CharField(max_length=2048)
    date = models.DateTimeField('date published')
    resolutionX = models.IntegerField()
    resolutionY = models.IntegerField()
    thumbnail = models.BooleanField()
    relatedImage = models.ForeignKey('Article', default=0)

    class Meta:
        db_table = "image"
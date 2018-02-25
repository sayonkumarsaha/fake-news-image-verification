from django.conf.urls import url
from . import views

urlpatterns =  [
            url(r'^api/cluster/', views.clusterAction, name='clusterAction'),
            url(r'^api/compare/', views.compareImageAction, name='compareImageAction'),
            url(r'^api/detect/', views.detectImageAction, name='detectImageAction')
]
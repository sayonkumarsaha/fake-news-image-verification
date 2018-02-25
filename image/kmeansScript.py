from __future__ import print_function

from sklearn.datasets import make_blobs
import sys

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.dates as mtd
import matplotlib.cm as cm
import numpy as np


import json
import time as ti
from datetime import datetime as dt

#def format_date(x, pos=None):
#     return mtd.num2date(x).strftime('%Y-%m-%d') #use FuncFormatter to format dates


def run(articles, data):

    log = open('logfile.log', 'w')
    try:
        #data = dates.split(",")
        #articles = articles.split(',')

        articles = np.array(articles)

        #TODO: convert date 
        #print(articles)
        
        #print(dt.datetime.strptime(data[0].split(' ')[0], '%Y-%m-%d' ))
        
        
        s=data[0].split(' ')[0]
        dateobject = dt.strptime(s, "%Y-%m-%d")
        #print(dateobject)
        
        #print(int(ti.mktime(dateobject.timetuple())) * 1000)

        

        #print(datetime.strptime(data[0].split(' ')[0], '%Y-%m-%d'))
        #timestamp = time.mktime(time.strptime(data[0], '%Y-%m-%d %H:%M:%S'))
        #print(timestamp)

       
        data = np.array([[int(ti.mktime(( dt.strptime((x.split(' ')[0]), "%Y-%m-%d")).timetuple())) * 1000, 1] for x in data])
        #print(data)

        dist = -2
        bestK = 1
        bestCtr = 1
        centers = []
        # Initialize the clusterer with n_clusters value and a random generator
        # seed of 10 for reproducibility.
        range_n_clusters = 10 if articles.size>10 else articles.size

        for n_clusters in range(2, range_n_clusters):

            clusterer = KMeans(n_clusters=n_clusters, random_state=10)
            cluster_labels = clusterer.fit_predict(data)

            #print(cluster_labels)


            silhouette_avg = silhouette_score(data, cluster_labels)

            if dist < silhouette_avg:
                dist = silhouette_avg
                bestK = cluster_labels
                bestCtr = n_clusters
                centers = clusterer.cluster_centers_

            #sample_silhouette_values = silhouette_samples(data, cluster_labels)
            #print("For n_clusters =", n_clusters,                  "The average silhouette_score is :", silhouette_avg)
            #print(sample_silhouette_values)



        #print(data[2][0])
        import time
        import datetime
        #print(data[:,0])
        #print(time.localtime(data[0,0]))
        d= np.array([time.strftime('%Y-%m-%d', time.localtime(long(x)/1000)) for x in data[:,0]])
        
        #print(d)
        #d = np.array([time.strptime(x) for x in d])
        #print(bestK)
        #print(centers)


        clusters = {}
        #print (bestCtr)
        #print(articles[0])
        #f = open("output.txt", "w")
        output_dates = []
        
        #print("file opened")
        if bestCtr > 1:
            cluster_centers = np.array([time.strftime('%Y-%m-%d', time.localtime(long(x/1000))) for x in centers[:,0]])
            #print(cluster_centers)

            #clusters['centers'] = cluster_centers

            clusters_final = []
            for cluster_no in range(0, bestCtr):
                
                item = {}

                #print(cluster_no)
                cluster_item = [time.strftime('%Y-%m-%d', time.localtime(long(data[i][0] )/1000))for i, x in enumerate(bestK) if x == cluster_no]
                cluster_articles = [articles[i] for i, x in enumerate(bestK) if x == cluster_no]
                #print(cluster_item)
                clusters_final.append(cluster_item)
                #item['center'] = cluster_centers[cluster_no]
                #item['data' ] = cluster_articles
                item['date'] = cluster_centers[cluster_no]
                item['count'] = len(cluster_articles)
                item['members' ] = cluster_articles
                clusters[str(cluster_no)] = item
                #f.write(cluster_centers[cluster_no]+'\n')
                #f.write(str(len(cluster_articles))+'\n')
                #for c in cluster_articles:
                #    f.write(c+'\n')

            #print(clusters_final)
            #clusters['data'] = clusters_final
        else:
             clusters['centers'] = time.strftime('%Y-%m-%d', time.localtime(long(np.mean(data[:,0])/1000)))
             clusters['data'] = articles;

        json_clusters = json.dumps(clusters)
        #print(json_clusters)

        #f.write(json_clusters)
        #f.write("END")
        #f.close()

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        xs = []
        ys = []
        zs = []
        for dd in d:
            time = dd.split("-")
            xs.append(int(time[0]))
            ys.append(int(time[1]))
            zs.append(int(time[2]))

        ax.scatter(xs, ys, zs)
        ax.set_xlabel('year')
        ax.set_ylabel('month')
        ax.set_zlabel('day')

        #print(xs)

        ax.set_xlim(1990, 2016)
        ax.set_ylim(1,12)

        #uncomment this line to see result of graphically clustering dates
        #plt.show()
        #print(json_clusters)
        return clusters
    except Exception as e:
        #print(e.message)
        log.write("failed")
        log.write(str(e.message))

#dates =['2017-05-03 00:00:00+00:00', '2017-05-03 00:00:00+00:00', '2017-05-07 00:00:00+00:00', '2017-05-04 00:00:00+00:00', '2017-05-26 00:00:00+00:00', '2017-05-04 00:00:00+00:00', '2017-05-03 00:00:00+00:00', '2017-05-07 00:00:00+00:00', '2017-05-16 00:00:00+00:00', '2017-05-08 00:00:00+00:00', '2017-05-04 00:00:00+00:00', '2017-05-04 00:00:00+00:00', '2017-05-04 00:00:00+00:00', '2017-05-05 00:00:00+00:00', '2017-05-03 00:00:00+00:00']
#articles = ['http://iamflashdance.com/2017/05/03/chris-rock-admits-to-cheating-on-his-ex-wife-i-was-a-piece-of-sht/', 'http://www.mzshyneka.com/2017/05/chrisrock-divorce-ex-wife/', 'http://fyintertainment.com/2017/05/scandal-married-chris-rock-cheat-wife-kerry-washington/', 'http://www.kokolife.tv/news/2017/05/04/chris-rock-talks-infidelity-divorce-finding-god-covers-rolling-stones-magazine/', 'http://www.kijiji.ca/v-tickets/city-of-toronto/hes-gonna-get-you-suckas-chris-rock-lower-bowl-aisle-seats/1267580540', 'http://fyintertainment.com/2017/05/no-laughing-matter-chris-rock-admits-bad-husband/', 'https://byroncrawford.wordpress.com/2017/05/03/chris-rock-in-a-hard-place-on-infidelity-his-new-tour-and-starting-over/', 'http://septin911.net/2017/05/chris-rock-reveals-cheated-wife-another-celebrity/', 'http://www.fathers-4-justice.org/2017/05/comedian-chris-rock-says-family-courts-leave-fing-mind/', 'https://getpocket.com/@dmhale0920/share/2205450', 'https://www.yahoo.com/celebrity/m/51249676-30a3-3bf2-b7df-d0c27da1fa9b/ss_chris-rock-reveals-he-cheated.html', 'https://www.lovebscott.com/news/chris-rock-reveals-cheated-wife-another-celebrity-piece-sht', 'https://www.reddit.com/r/MGTOW/comments/69971k/chris_rock_would_i_ever_get_married_again/', 'http://blindgossip.com/?p=85174', 'http://www.rollingstone.com/tv/features/chris-rock-cover-story-on-his-new-tour-and-starting-over-w479496']
#run(articles, dates)

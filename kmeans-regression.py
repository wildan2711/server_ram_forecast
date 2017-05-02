from sklearn import cluster
from sklearn import linear_model
from matplotlib import pyplot
from requests import get
import numpy as np
import time
import datetime

URL = "http://localhost:5000/memory/percent"
FILE_URL = "ram_centroids_" + str(datetime.date.today()) + ".csv"

def save(data):
    np.savetxt(FILE_URL, data, fmt='%.5f', delimiter=',')

def retrieve():
    try:
        r = get(URL)
        response = r.json()
        data = [int(time.clock()), int(response)]
        print(data)
        return data 
    except Exception as e:
        print("Error %s" % e)
        return None

k = 5
kmeans = cluster.KMeans(n_clusters=k)
regr = linear_model.LinearRegression()

data = np.array([retrieve()])

while True:
    d = retrieve()
    if d is not None:
        data = np.concatenate((data, [d]))
    print(data)
    if len(data) > k:
        kmeans.fit(data)

        labels = kmeans.labels_
        centroids = kmeans.cluster_centers_
        save(centroids)
        # x = [centroids[:,0]]
        # y = [centroids[:,1]]
        # print(x)
        # print(y)
        # regr.fit(x, y)
        # print(regr.coef_)

    # for i in range(k):
    #     # select only data observations with cluster label == i
    #     ds = data[np.where(labels==i)]
    #     # plot the data observations
    #     pyplot.plot(ds[:,0],ds[:,1],'o')
    #     # plot the centroids
    #     lines = pyplot.plot(centroids[i,0],centroids[i,1],'kx')
    #     # make the centroid x's bigger
    #     pyplot.setp(lines,ms=15.0)
    #     pyplot.setp(lines,mew=2.0)
    time.sleep(1)
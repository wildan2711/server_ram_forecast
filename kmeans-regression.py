from sklearn import cluster
from sklearn import linear_model
from requests import get
import numpy as np
import time
import datetime
import csv
import libvirt
import json

IP = "192.168.122.46"
SERVER_NAME = "generic"
URL = "http://"+IP+":8080/memory/percent"
REALTIME_URL = "ram_realtime_" + str(datetime.date.today()) + ".csv"
CENTROIDS_URL = "ram_centroids_" + str(datetime.date.today()) + ".csv"
REGRESSION_URL = "ram_regression_" + str(datetime.date.today()) + ".csv"
PREDICTION_URL = "ram_prediction_" + str(datetime.date.today()) + ".csv"
SERVER_STATUS_URL = "server_status.json"

RAM_MAP = [1048576, 2097152, 4194304] # Kilobytes

TIME_START = time.clock()

def save(url, data):
    np.savetxt(url, data, fmt='%.5f', delimiter=',')

def save_prediction(url, data):
    myfile = open(url, 'a')
    wr = csv.writer(myfile, delimiter=',')
    wr.writerow(data)

def retrieve():
    try:
        r = get(URL)
        response = r.json()
        time_now = (time.clock() - TIME_START)*100
        data = [time_now, int(response)]
        return data 
    except Exception as e:
        print("Error %s" % e)
        return None

def write_server_status(ram):
    status = {
        "name": SERVER_NAME,
        "ip": IP,
        "ram": ram
    }
    with open(SERVER_STATUS_URL, 'w') as file:
        json.dump(status, file)    

def read_server_status():
    with open(SERVER_STATUS_URL, 'rd') as file:
        status = json.load(file)
    return status

def reconfigure(ram):
    import libvirt
    conn = libvirt.open()
    vm = conn.lookupByName(SERVER_NAME)
    currentMem = vm.memoryStats()['actual']
    vm.setMemory(ram)
    newMem = vm.memoryStats()['actual']
    conn.close()
    print "Reconfigured "+currentMem+"KB -> "+newMem
    return newMem

def recommend(prediction):
    status = read_server_status()
    if prediction > 80:
        # Increase
        recommendation = status["ram"] + 1
        if recommendation == len(RAM_MAP):
            print "Penggunaan memory melebihi batas"
            return
    elif prediction < 20:
        # decrease
        recommendation = status["ram"] - 1
        if recommendation == -1:
            print "Penggunaan memory di bawah minimal"
            return
    else:
        print prediction
        return
    write_server_status(recommendation)
    ram = reconfigure(RAM_MAP[recommendation])

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
        save(REALTIME_URL, data)
        kmeans.fit(data)

        labels = kmeans.labels_
        centroids = kmeans.cluster_centers_
        save(CENTROIDS_URL, centroids)
        x = centroids[:,[0]]
        y = centroids[:,[1]]
        regr.fit(x, y)
        save(REGRESSION_URL, regr.coef_)
        # prediksi 2 detik setelahnya
        future = d[0] + 2
        prediction = [future, regr.predict(future).tolist()[0][0]]
        save_prediction(PREDICTION_URL, prediction)
        # print(prediction)
        recommend(prediction[1])
        
    time.sleep(1)

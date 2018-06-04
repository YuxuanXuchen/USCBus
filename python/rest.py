#!/usr/bin/python2.7
from flask import Flask
import utils
import threading
from sys import platform

app = Flask(__name__)
lock = threading.Lock()
result = ""

@app.route('/')
def index():
    lock.acquire()
    ret = result
    lock.release()
    return ret

def runRest():
    app.run(host='0.0.0.0', port=8888)

def getData():
    w = utils.webFetcher()
    while 1:
        try:
            w.getWebpage()
            w.getRoutes()
            w.getStops()
            global result
            lock.acquire()
            result = w.jsonResult()
            lock.release()
        except Exception as e:
            print("Error: " + str(e))
    w.cleanup()

if __name__ == '__main__':
    thread1 = threading.Thread(target=runRest)
    thread2 = threading.Thread(target=getData)
    thread1.start()
    thread2.start()

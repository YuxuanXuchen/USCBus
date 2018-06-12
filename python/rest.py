#!/usr/bin/python2.7
from flask import Flask
import utils, beautifulSoup, threading, time, sys, signal, os, time
import logging
from logging.handlers import RotatingFileHandler
from sys import platform

app = Flask(__name__)
lock = threading.Lock()
result = ""

if platform == "linux" or platform == "linux2":
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.INFO)
    log_handler = RotatingFileHandler("app.log", mode='a', maxBytes=5*1024*1024,
                                     backupCount=2, encoding=None, delay=0)
    log_handler.setLevel(logging.INFO)
    log.addHandler(log_handler)

@app.route('/')
def index():
    lock.acquire()
    ret = result
    lock.release()
    return ret

def runRest():
    app.run(host='0.0.0.0', port=8888)

def getData():
    global result
    w = utils.webFetcher()
    while 1:
        try:
            w.run()
            lock.acquire()
            result = w.jsonResult()
            lock.release()
            w.close()
        except Exception as e:
            print("Error: " + str(e))
            try:
                w.cleanUp()
            except:
                pass
            time.sleep(1)
            w = utils.webFetcher()
    w.cleanup()

def getDataBS4():
    global result
    w = beautifulSoup.beautifulSoupFetcher()
    while 1:
        try:
            w.run()
            lock.acquire()
            result = w.getResult()
            lock.release()
        except Exception as e:
            print("Error: " + str(e))
        finally:
            w.cleanup()

if __name__ == '__main__':
    thread1 = threading.Thread(target=runRest)
    thread2 = threading.Thread(target=getDataBS4)
    thread3 = threading.Thread(target=getDataBS4)
    def signal_handler(signal, frame):
        print('\nKilling the server')
        os.kill(os.getpid(), 9)
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    thread1.start()
    thread2.start()
    time.sleep(5)
    thread3.start()
    while 1:
        time.sleep(0.5)

#!/usr/bin/python2.7
from flask import Flask
import utils, threading, time, sys, signal, os
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
lock = threading.Lock()
result = ""

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
        except Exception as e:
            print("Error: " + str(e))
            try:
                w.cleanUp()
            except:
                pass
            time.sleep(1)
            w = utils.webFetcher()
    w.cleanup()

if __name__ == '__main__':
    thread1 = threading.Thread(target=runRest)
    thread2 = threading.Thread(target=getData)
    thread3 = threading.Thread(target=getData)
    def signal_handler(signal, frame):
        print('\nKilling the server')
        os.kill(os.getpid(), 9)
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    thread1.start()
    thread2.start()
    time.sleep(10)
    thread3.start()
    while 1:
        time.sleep(0.5)

from flask import Flask
import utils
import threading, Queue



app = Flask(__name__)
lock = threading.Lock()
result = ""

@app.route('/')
def index():
    lock.acquire()
    ret = result
    lock.release()
    return ret

def getData():
    while 1:
        try:
            w = utils.webFetcher()
            w.getRoutes()
            w.getStops()
            lock.acquire()
            global result
            result = w.jsonResult()
            lock.release()
            w.cleanUp()
        except:
            pass

if __name__ == '__main__':
    thread1 = threading.Thread(target=app.run(host='0.0.0.0'))
    thread2 = threading.Thread(target=getData)
    thread1.start()
    thread2.start()
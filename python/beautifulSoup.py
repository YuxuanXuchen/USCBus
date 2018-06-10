import requests, constants, re
from bs4 import BeautifulSoup

class beautifulSoupFetcher:
    def __init__(self):
        self.routes = []
        self.stops = []
        self.result = {}

    def getRoutes(self):
        startPage = requests.get(constants.uscBusesTextUrl)
        soup = BeautifulSoup(startPage.content, 'html.parser')
        for eachHtml in soup.findAll("a"):
            routeId = re.search('/(\d+?)/', eachHtml['href']).group(1)
            eachRoute = [eachHtml.get_text(), routeId]
            self.routes.append(eachRoute)

    def getStops(self):
        for eachRoute in self.routes:
            eachRouteStops = []
            routeId = eachRoute[1]
            startPage = requests.get(constants.uscBusesRouteUrl%routeId)
            soup = BeautifulSoup(startPage.content, 'html.parser')
            for eachHtml in soup.findAll("a"):
                try:
                    stopId = re.search('stops/(\d*)', eachHtml['href']).group(1)
                except AttributeError:
                    continue
                eachStop = [eachHtml.get_text(), stopId]
                # print stopId + " " + eachHtml.get_text()
                eachRouteStops.append(eachStop)
            eachRouteData = [eachRoute[0], eachRoute[1], eachRouteStops]
            self.stops.append(eachRouteData)

    def getData(self):
        for eachRouteData in self.stops:
            routeId = eachRouteData[1]
            for eachStop in eachRouteData[2]:
                stopId = eachStop[1]
                startPage = requests.get(constants.uscBusesRouteStopUrl % (routeId, stopId))
                soup = BeautifulSoup(startPage.content, 'html.parser')
                for eachHtml in soup.findAll("li"):
                    try:
                        eachHtml['class']
                    except:
                        print eachHtml.get_text()

if __name__ == "__main__":
    b = beautifulSoupFetcher()
    b.getRoutes()
    b.getStops()
    b.getData()

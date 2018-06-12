import requests, constants, re, json
from bs4 import BeautifulSoup


class beautifulSoupFetcher:
    def __init__(self):
        self.routes = []
        self.stops = []
        self.result = []

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
            startPage = requests.get(constants.uscBusesRouteUrl % routeId)
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
            eachRouteResult = []
            routeId = eachRouteData[1]
            for eachStop in eachRouteData[2]:
                stopId = eachStop[1]
                startPage = requests.get(constants.uscBusesRouteStopUrl % (routeId, stopId))
                soup = BeautifulSoup(startPage.content, 'html.parser')
                eachStopResult = {"stopId": stopId, "stopName": eachStop[0]}
                eachStopTimeResult = []
                for eachHtml in soup.findAll("li"):
                    try:
                        eachHtml['class']
                    except:
                        dict = self.processData(eachHtml.get_text())
                        if dict is not None:
                            eachStopTimeResult.append(dict)
                eachStopResult["time"] = eachStopTimeResult
                eachRouteResult.append(eachStopResult)
            self.result.append({"routeId": routeId, "routeName": eachRouteData[0], "routeTime": eachRouteResult})


    def processData(self, s):
        try:
            if "is currently arriving." in s:
                busNum = re.search('Bus (.+?) is currently arriving', s).group(1)
                due = '0'
                arriveTime = ""
            else:
                busNum = re.search('Bus (.+?) arrive', s).group(1)
                due = re.search('in (\d+?) minute', s).group(1)
                arriveTime = re.search('at (.+?)\.', s).group(1)
            return {"busNum": busNum, "due": due, "arriveTime": arriveTime}
        except Exception as e:
            return None

    def run(self):
        self.getRoutes()
        self.getStops()
        self.getData()

    def getResult(self):
        return json.dumps(self.result)

    def cleanup(self):
        self.routes = []
        self.stops = []
        self.result = []

if __name__ == "__main__":
    b = beautifulSoupFetcher()
    b.run()
    print b.getResult()
    # print b.processData("Bus A747 arrives in 2 minutes at 8:21 PM.")
    # print b.processData("Arrival predictions are not available at this time.")

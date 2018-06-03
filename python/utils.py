from selenium import webdriver
import constants
import logging
import time
import json

class webFetcher:
    def __init__(self):
        self.driver = webdriver.Chrome()
        logging.basicConfig(filename= constants.webFetcherLogFile, level=logging.DEBUG)
        self.driver.get(constants.uscBusesUrl)
        self.validRoutes = []
        self.stops = {}
        self.result = {}
        if not "USC Buses" in self.driver.title:
            raise Exception("webpage load failed: %s", self.driver.title)
        time.sleep(2)
        logging.debug("webpage loaded successfully")

    def getRoutes(self):
        routes = self.driver.find_elements_by_xpath('//*[@id="routeSelect"]/*')
        #time.sleep(1)
        for elem in routes:
            if not elem.get_attribute('value') == '0' and \
                    not elem.get_attribute('class') == "route_arrival_menu_item_disable":
                self.validRoutes.append(elem.text)

    def getStops(self):
        for eachRoute in self.validRoutes:
            xpath = "//*[@id='routeSelect']/option[text()='%s']" % eachRoute
            self.driver.find_element_by_xpath(xpath).click()
            time.sleep(1)
            stops = self.driver.find_elements_by_xpath('//*[@id="stopSelect"]/*')
            resultEachRoute = []
            for elem in stops:
                if not elem.get_attribute('value') == '0':
                    stopName = elem.text
                    xpath_stop = "//*[@id='stopSelect']/option[text()='%s']" % stopName
                    self.driver.find_element_by_xpath(xpath_stop).click()
                    time.sleep(0.6)
                    prediction = self.driver.find_element_by_xpath('//*[@id="predictions_area"]').text
                    updateTime = self.driver.find_element_by_xpath('//*[@id="arrivals_time"]').text
                    dict = {'stop':stopName, 'prediction': prediction, "updateTime": updateTime}
                    resultEachRoute.append(dict)
                    # print elem.text
            self.result[eachRoute] = resultEachRoute

    def jsonResult(self):
        return json.dumps(self.result)

    def cleanUp(self):
        self.driver.close()

    def printJsonResult(self):
        print json.dumps(self.result, indent=4, sort_keys=True)


if __name__ == '__main__':
    w = webFetcher()
    w.getRoutes()
    w.getStops()
    w.printJsonResult()
    w.cleanUp()
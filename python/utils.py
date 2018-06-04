#!/usr/bin/python2.7
from selenium import webdriver
import constants
import logging
import time
import json
from pyvirtualdisplay import Display
from sys import platform

class webFetcher:
    def __init__(self):
        if platform == "linux" or platform == "linux2":
            self.display = Display(visible=0, size=(800, 600))
            self.display.start()
            self.driver = webdriver.Firefox()
        elif platform == "darwin":
            self.driver = webdriver.Chrome()
        logging.basicConfig(filename=constants.webFetcherLogFile, level=logging.DEBUG)
        self.validRoutes = []
        self.stops = {}
        self.result = {}

    def getWebpage(self):
        self.driver.get(constants.uscBusesUrl)
        if not "USC Buses" in self.driver.title:
            raise Exception("webpage load failed: %s", self.driver.title)
        time.sleep(2)
        logging.debug("webpage loaded successfully")

    def refreshPage(self):
        self.driver.refresh()
        time.sleep(2)

    def getRoutes(self):
        routes = self.driver.find_elements_by_xpath('//*[@id="routeSelect"]/*')
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
            self.result[eachRoute] = resultEachRoute

    def jsonResult(self):
        return json.dumps(self.result)

    def cleanUp(self):
        self.driver.close()
        if platform == "linux" or platform == "linux2":
            self.display.stop()

    def printJsonResult(self):
        print json.dumps(self.result, indent=4, sort_keys=True)


if __name__ == '__main__':
    w = webFetcher()
    w.getWebpage()
    w.getRoutes()
    w.getStops()
    w.printJsonResult()
    w.cleanUp()
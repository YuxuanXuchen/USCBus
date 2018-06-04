#!/usr/bin/python2.7
from selenium import webdriver
import constants
import logging
import time
import json
from pyvirtualdisplay import Display
from sys import platform
from selenium.webdriver.support.ui import Select

class webFetcher:
    def __init__(self):
        if platform == "linux" or platform == "linux2":
            self.display = Display(visible=0, size=(800, 600))
            self.display.start()
        self.driver = webdriver.Firefox()
        logging.basicConfig(filename=constants.webFetcherLogFile, level=logging.DEBUG)
        self.validRoutes = []
        self.stops = {}
        self.result = {}

    def getWebpage(self):
        self.driver.get(constants.uscBusesUrl)
        if not "USC Buses" in self.driver.title:
            raise Exception("webpage load failed: %s", self.driver.title)
        self.cleanData()
        time.sleep(2)
        logging.debug("webpage loaded successfully")

    def cleanData(self):
        self.validRoutes = []
        self.stops = {}
        self.result = {}

    def getRoutes(self):
        routes = self.driver.find_elements_by_xpath('//*[@id="routeSelect"]/*')
        for elem in routes:
            if not elem.get_attribute('value') == '0' and \
                    not elem.get_attribute('class') == "route_arrival_menu_item_disable":
                self.validRoutes.append(elem.text)

    def getStops(self):
        for eachRoute in self.validRoutes:
            routeSelect = Select(self.driver.find_element_by_id('routeSelect'))
            routeSelect.select_by_visible_text(eachRoute)
            time.sleep(1)
            stops = self.driver.find_elements_by_xpath('//*[@id="stopSelect"]/*')
            resultEachRoute = []
            for elem in stops:
                if not elem.get_attribute('value') == '0':
                    stopName = elem.text
                    stopSelect = Select(self.driver.find_element_by_id('stopSelect'))
                    stopSelect.select_by_visible_text(stopName)
                    time.sleep(0.6)
                    updateTime = self.driver.find_element_by_xpath('//*[@id="arrivals_time"]').text
                    try:
                        dueIn = self.driver.find_element_by_xpath('//*[@id="predictions_area"]/span[1]').text.strip()
                        arrivingVehicle = self.driver.find_element_by_class_name("arriving_vehicle").text
                        arrivalBus = arrivingVehicle.split(" @ ")[0]
                        arrivalTime = arrivingVehicle.split(" @ ")[1]
                        dict = {'stop': stopName, 'due': dueIn, "busNum": arrivalBus, "arrivalTime": arrivalTime, "updateTime": updateTime}
                    except:
                        dict = {'stop':stopName, 'prediction': "None", "updateTime": updateTime}
                    resultEachRoute.append(dict)
            self.result[eachRoute] = resultEachRoute

    def jsonResult(self):
        return json.dumps(self.result)

    def cleanUp(self):
        self.driver.close()
        if platform == "linux" or platform == "linux2":
            self.display.stop()

    def formatJsonResult(self):
        return json.dumps(self.result, indent=4, sort_keys=True)

    def run(self):
        self.getWebpage()
        self.getRoutes()
        self.getStops()

if __name__ == '__main__':
    w = webFetcher()
    w.run()
    print w.formatJsonResult()
    w.cleanUp()

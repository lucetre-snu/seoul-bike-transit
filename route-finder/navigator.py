import time
from bs4 import BeautifulSoup
import datetime

from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class KakaoRouteFinder:
    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def fetch_bike(self, verbose=True, init=True, time_delta=0.2):
        if init:
            self.driver.find_element(by=By.CSS_SELECTOR, value=f"#biketab").click()
            time.sleep(2)
            
        if verbose:
            for li in self.driver.find_elements(by=By.CSS_SELECTOR, value=f"div.BikeRouteResultView > ul > li"):
                li.click()        
                time.sleep(time_delta)
                
        element = self.driver.find_element(by=By.CSS_SELECTOR, value=f"div.BikeRouteResultView")
        return element.get_attribute('innerHTML')
    
    def fetch_walk(self, verbose=False, init=True, time_delta=0.2):
        if init:
            self.driver.find_element(by=By.CSS_SELECTOR, value=f"#walktab").click()
            time.sleep(time_delta)

        element = self.driver.find_element(by=By.CSS_SELECTOR, value=f"div.WalkRouteResultView")
        return element.get_attribute('innerHTML')
        
    def fetch_transit(self, verbose=True, init=True, time_delta=0.2, init_time=2.0):    
        if init:
            self.driver.find_element(by=By.CSS_SELECTOR, value=f"#transittab").click()
            time.sleep(init_time)

        if verbose:
            for route in self.driver.find_elements(by=By.CSS_SELECTOR, value=f"li.TransitRouteItem"):
                route.click()
                for more_route in route.find_elements(by=By.CSS_SELECTOR, value=f"span.moreBtn"):
                    more_route.click()
                    time.sleep(time_delta)
                time.sleep(time_delta)

        element = self.driver.find_element(by=By.CSS_SELECTOR, value=f"ul.TransitTotalPanel")
        return element.get_attribute('innerHTML')

    def find_route_by_url(self, type, base_url, verbose=True, init=True, time_delta=0.2, init_time=2.0):
        self.driver.get(base_url)
        time.sleep(time_delta)
        
        try:
            self.driver.find_element(by=By.CSS_SELECTOR, value="#dimmedLayer").click()
        except ElementNotInteractableException:
            pass

        try:
            if (type == 'bike'):
                return self.fetch_bike(verbose, init)
            elif (type == 'transit'):
                return self.fetch_transit(verbose, init, init_time=init_time)
            elif (type == 'walk'):
                return self.fetch_walk(verbose, init)
            else:
                return None
        except Exception as e:
            # print('find_route_by_url', e)
            pass


    def find_route_by_congnamul(self, type, origin, dest, rt1='ORIGIN', rt2='DESTINATION', verbose=False, init=False, time_delta=0.2, init_time=2.0):
        (org_x, org_y) = origin
        (des_x, des_y) = dest
        base_url = f"https://map.kakao.com/?map_type=TYPE_MAP&target={type}&rt={int(org_x)},{int(org_y)},{int(des_x)},{int(des_y)}&rt1={rt1}&rt2={rt2}"
        return self.find_route_by_url(type, base_url, verbose, init, time_delta, init_time)
        

    def find_route_by_keyword(self, type, origin, dest, time_delta=0.2, init_time=2.0):
        base_url = f"https://map.kakao.com/?map_type=TYPE_MAP&target={type}&sName={origin}&eName={dest}"
        return self.find_route_by_url(type, base_url, verbose=True, init=(type=='transit'), time_delta=time_delta, init_time=init_time)

    def __del__(self):
        self.driver.close()


def extract_route(type, route):
    res = []
    soup = BeautifulSoup(route, 'html.parser')
    if (type == 'bike'):
        for route in (soup.find_all('li', {"class": "BikeRouteItem"})):
            res.append({
                "mode": route.find('span', {"class": "mode"}).text,
                "time": route.find('span', {"class": "time"}).text.strip(),
                "distance": route.find('span', {"class": "distance"}).text,
                "altitude": route.find('span', {"class": "altitude"}).text,
                "calories": route.find('span', {"class": "calories"}).text,
            })
    elif (type == 'transit'):
        for route in (soup.find_all('li', {"class": "TransitRouteItem"})):
            res.append({
                "time": route.find('span', {"class": "time"}).text.strip(),
                "info": route.find('span', {"class": "walkTime"}).get('title'),
            })
    elif (type == 'walk'):
        for route in (soup.find_all('li', {"class": "WalkRouteItem"})):
            res.append({
                "mode": route.find('span', {"class": "mode"}).text,
                "time": route.find('span', {"class": "time"}).text.strip(),
                "info": route.find('div', {"class": "info"}).text.strip(),
            })
    return res


def calc_timedelta(str_time):
    delta = datetime.timedelta()
    for t in str_time.strip().split():
        if t.find('시간') != -1:
            delta += datetime.timedelta(hours=int(t.replace("시간", "")))
        elif t.find('분') != -1:
            delta += datetime.timedelta(minutes=int(t.replace("분", "")))
        elif t.find('초') != -1:
            delta += datetime.timedelta(seconds=int(t.replace("초", "")))
    return delta
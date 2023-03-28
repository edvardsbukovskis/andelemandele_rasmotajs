from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import multiprocessing

options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)
driver.get("https://www.andelemandele.lv/perle/8000069/koka-spele/")
soup = BeautifulSoup(driver.page_source, 'html.parser')
price = int(soup.find("span", class_="product__price old-price").text.split(' ')[0])

print(type(price))









"""
dict = {}

dict["category"] = {"counter":0}
dict["category"]["price"] = [1]
dict["category"]["price"].append(10)

print(dict)
"""
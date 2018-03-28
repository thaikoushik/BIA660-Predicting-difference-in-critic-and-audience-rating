"""
    Author: Koushik Thai
"""
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import json
import io
import os 

# Initialized Chrome driver
driver = webdriver.Chrome()

# Default wait time from the driver
wait = WebDriverWait(driver, 10)

# Function to open the local file and fetch the URL and get the page source of the movies one by one 
def openFile(path):
    data = json.load(open(path))
    i=0
    for movie in data['movies']:
        i+=1;
        # Breaking if 5000 movies are reached 
        if i>5000: break
        movieName = movie['movieName']
        movieURL = movie['movieURL']
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dir_path = os.path.join(script_dir, "PROJHTML")  # will return 'feed/address'
        try:
            os.makedirs(dir_path) 
        except OSError:
            pass
        path = os.path.join(dir_path)
        driver.get(movieURL)
        html = driver.page_source
        soupified = BeautifulSoup(html)
        with io.open(path+"/movie"+str(i)+".html",'wb') as f:
            f.write(soupified.encode('utf-8'))


if __name__ == "__main__": 
    openFile('data.txt')
driver.quit()
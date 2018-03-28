"""
    Author: Koushik Thai
"""
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

# Get the text field from the item Selector
def get_field_text_if_exists(item, selector):
    """Extracts a field by a CSS selector if exists."""
    try:
        return item.find_element_by_css_selector(selector).text
    except NoSuchElementException:
        return ""

# Get the href text from the selector if any
def get_link_if_exists(item, selector):
    """Extracts an href attribute value by a CSS selector if exists."""
    try:
        return item.find_element_by_css_selector(selector).get_attribute("href")
    except NoSuchElementException:
        return ""

# Movie Dictionary initialized
movieInfo = dict()
# Intialized the Chrome driver
driver = webdriver.Chrome()
# Default wait time
wait = WebDriverWait(driver, 10)

# All the movies link
driver.get('http://www.rottentomatoes.com/browse/dvd-streaming-all/')

# click more until no more results to load
while True:
    try:
        more_button = wait.until(EC.visibility_of_element_located((By.XPATH , '//*[@id="show-more-btn"]/button')))
        more_button.click()
    except TimeoutException:
        break

# wait for results to load
wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.mb-movies')))

# Empty array to store the movies
movieInfo['movies'] = []
# parse results
for result in driver.find_elements_by_css_selector('.mb-movie'):
    movieURL = get_link_if_exists(result, 'a')
    movieName = get_field_text_if_exists(result, 'h3')
    #movieInfo[movieName] = movieURL 
    movieInfo['movies'].append({'movieName':movieName,'movieURL':movieURL})

with open('data.txt','w') as outfile:
    json.dump(movieInfo,outfile)
    
driver.quit()
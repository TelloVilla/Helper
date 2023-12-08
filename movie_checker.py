from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from collections import namedtuple
import requests

options = FirefoxOptions()
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)



Theater = namedtuple("Theater", [
    "name",
    "movies"
])

Movie = namedtuple("Movie", [
    "title",
    "showings"
])

def movie_check(zipcode):
    url = "https://www.fandango.com/" + str(zipcode) + "_movietimes"

    movie_showings = []
    driver.get(url)
    driver.implicitly_wait(1.5)
    theatre_list = driver.find_elements(by=By.CSS_SELECTOR, value=".fd-theater")
    theater = theatre_list[0].find_element(by=By.CSS_SELECTOR, value=".fd-theater__name")
    theater_name = theater.find_element(by=By.TAG_NAME, value="a")
    showtimes = theatre_list[0].find_elements(by=By.CSS_SELECTOR, value=".fd-movie")
    for show in showtimes:
        title = show.find_element(By.CSS_SELECTOR, value=".fd-movie__title")
        time = show.find_elements(by=By.CSS_SELECTOR, value=".showtime-btn--available")
        showings = []
        for t in time:
            showings.append(t.text)

        movie_item = Movie(title.text, showings)

        movie_showings.append(movie_item)
            
    closest_theater = Theater(theater_name.text, movie_showings)
    driver.quit()

    return closest_theater

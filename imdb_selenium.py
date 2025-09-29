# importing selenium webdriver to scrape static pages
from selenium import webdriver

# These to parse and get the website
from bs4 import BeautifulSoup
import requests

# These are used to define waiting time after selenium does something so that it doesn't return an error while the page is still loading
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# These are used to install Chrome Driver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# These set the time for requests to avoid the site tagging the request as bot
import time
import random

# Pandas is for working with dataframe
import pandas as pd

# This is to generate random code for files saved
from uuid import uuid4

# to download Selenium driver
options = webdriver.ChromeOptions()
options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)
options.add_argument("--headless=new")
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# This code is used to assess the driver on the pc after downloading. The driver above was commented out after it had downloaded.
path = r"C:\Users\HP\.wdm\drivers\chromedriver\win64\140.0.7339.207\chromedriver-win32\chromedriver.exe"
driver = webdriver.Chrome(service=Service(path), options=options)

# scrapping imdb for the genre
genre_url = "https://www.imdb.com/search/title/"
# Set headers so that the web does not think request is a bot attack.
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/140.0.0.0 Safari/537.36"
}
response = requests.get(genre_url, headers=header)
soup = BeautifulSoup(response.text, "lxml")

# [5] in the code above is because the genre division on the web page is the 6th division, so I am selecting just the 6th division and not all that fall into that class.
div = soup.find_all("div", class_="ipc-accordion__item__content")[5]

# Note the [:-1] in the code below is because there was a number after every genre, so, that is to select the words up to the last one.
# .strip here and after removes whitespaces makes data cleaning easier
genre_spans = div.find_all("span", class_="ipc-chip__text")
genres = [
    g.text[:-1].strip() if g.text[-1].isdigit() else g.text.strip() for g in genre_spans
]


# Container for all movie data
all_movies_data = []


def extract_movie(movie):
    try:
        name_element = (
            movie.find(
                "h3",
                class_="ipc-title__text ipc-title__text--reduced",
            )
        )
        name = name_element.get_text(strip=True)

        # I want to get the imdb id so that while doing multiple scrapes the script can check that the ids are not duplicated
        link_element = movie.find("a", class_="ipc-title-link-wrapper")
        imdb_id = link_element['href'].split("/")[2] if link_element and link_element['href'] else "N/A"

        # year, movie duration and  movie certificaton are all in the same div and with the same span, therefore the following
        metadata_div = movie.find(
            "div", class_="sc-15ac7568-6 fqJJPW dli-title-metadata"
        )
        year, movie_duration, certification = "N/A", "N/A", "N/A"
        if metadata_div:
            spans = metadata_div.find_all("span") 
            year = spans[0].text.strip() if len(spans) > 0 else "N/A"
            movie_duration = spans[1].text.strip() if len(spans) > 1 else "N/A"
            certification = spans[2].text.strip() if len(spans) > 2 else "N/A"

        # ratings and ratings vote count are also same div and span, but vote count is sort of dependent on ratings, therefore a little different approach
        rating_span = movie.find(
            "span",
            class_="ipc-rating-star--rating",
        )
        vote_count_span = movie.find("span", class_ = "ipc-rating-star--voteCount")
        ratings = rating_span.get_text(strip = True) if rating_span else "N/A"
        rating_votes_count = vote_count_span.get_text(strip = True).strip("()") if vote_count_span else "N/A"

        return {
        "name":name,
        "imdb_id": imdb_id,
        "year": year,
        "ratings": ratings,
        "vote_count":rating_votes_count,
        "movie_duration":movie_duration,
        "movie_certification":certification,
        }
            
    except Exception as e:
            print(f"Error processing movie in genre {genre}: {e}")
            return None

# loop over each genre
for genre in genres:
    print(f"Scraping genre: {genre}")
    movies_collected = 0
    genre_movies = []
    seen_imdb_ids = set()

    while movies_collected < 100:    
        genre_url = f"https://www.imdb.com/search/title/?genres={genre}&count=50"
        driver.get(genre_url)
        # Wait for the movie list to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ipc-metadata-list-summary-item__c"))
            )
        except Exception as e:
            print(f"Error loading page for genre {genre}: {e}")
            continue


        movie_soup = BeautifulSoup(driver.page_source, "lxml")

        # now, to the important features I need to get.
        movies = movie_soup.find_all("div", class_="ipc-metadata-list-summary-item__c")
        print(f"Found {len(movies)} movies for genre: {genre}")

        for movie in movies:
             if movies_collected >= 100:
                  break
             
             movie_data = extract_movie(movie)
             if movie_data and movie_data.get("imdb_id") not in seen_imdb_ids:
                  movie_data["genre"] = genre 
                  genre_movies.append(movie_data)
                  seen_imdb_ids.add(movie_data["imdb_id"])
                  movies_collected +=1

            #print progress
            if movies_collected % 100 == 0:
                print(f"Collected {movies_collected} movies for {genre}")
        
        #click see more
        try:
            see_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[@class='ipc-see-more__text' and text()='50 more']"))
            )
            see_more_button.click()

        except Exception as e:
            print(f"Error clicking '50 more' button: {e}")

        except requests.RequestException as e:
            print(f"Error fetching page for {genre}: {e}")
            time.sleep(5)  # Wait longer before retrying
            continue
    break
print(genre_movies)





                  
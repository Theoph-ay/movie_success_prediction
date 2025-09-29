#This is a base code that returns the first 25 movies for the first genre, I'd loop through this in other scripts to get the data I need.


#BeautifulSoup and request for the scraping
from bs4 import BeautifulSoup
import requests
#pandas for data manipulation
import pandas as pd
#time to space request
import time
#to set random time to make request
import random


base_url = "https://www.imdb.com/search/title/"
#Set headers so that the web does not think request is a bot attack.
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/140.0.0.0 Safari/537.36"
}
response = requests.get(base_url, headers=header)
soup = BeautifulSoup(response.text, "lxml")

div = soup.find_all("div", class_ ="ipc-accordion__item__content")[5]
#[5] in the code above is because the genre division on the web page is the 6th division, so I am selecting just the 5th division and not all that fall into that class.


genre_spans = div.find_all("span", class_="ipc-chip__text")
genres = [g.text[:-1].strip() if g.text[-1].isdigit() else g.text.strip() for g in genre_spans]

#Note the [:-1] in the code above is because there was a number after every genre, so, that is to select the words up to the last one.
# .strip here and after removes whitespaces makes data cleaning easier

# Container for all movie data
all_movies_data = []

#loop over each genre
for genre in genres:
    
    genre_url = f"https://www.imdb.com/search/title/?genres={genre}"
    movie_resp = requests.get(genre_url, headers=header)
    movie_soup = BeautifulSoup(movie_resp.text,"lxml")

    #now, to the important features I need to get.
    movies = movie_soup.find_all("li", class_="ipc-metadata-list-summary-item")
    print(len(movies))
    name = movies.find("div", class_="ipc-title ipc-title--base ipc-title--title ipc-title--title--reduced ipc-title-link-no-icon ipc-title--on-textPrimary sc-3cb45114-2 gReSCf dli-title with-margin").a.text.split(".")[1].strip()

    #year, movie duration and  movie certificaton are all in the same div and with the same span, therefore the following
    metadata_div = movies.find("div", class_="sc-15ac7568-6 fqJJPW dli-title-metadata")
    spans = metadata_div.find_all("span")
    year = spans[0].text.strip()
    movie_duration = spans[1].text.strip()
    certification = spans[2].text.strip() if len(spans) >1 else "Series"

    #ratings and ratings vote count are also same div and span, but vote count is sort of dependent on ratings, therefore a little different approach
    rating_text = movie_soup.find("div", class_="sc-17ce9e4b-0 ddMjUi sc-15ac7568-2 kzodIA dli-ratings-container").span.text.strip()
    parts = rating_text.split()
    ratings = parts[0]
    rating_votes_count = parts[1].strip("()")





#I pasted the scraper.py base code in grok to loop over, but this did not fully work because it only returned first 25 movies of each genre.
#This is because the imdb site does't use pagination, it uses a static dynamic website
#Therefore there is a need to use selenium which is in the imdb_selenium.py script

from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import random
import os
from uuid import uuid4

# Set headers to avoid being flagged as a bot
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/140.0.0.0 Safari/537.36"
}

# Container for all movie data
all_movies_data = []

# Get genres from main page
base_url = "https://www.imdb.com/search/title/"
response = requests.get(base_url, headers=header)
soup = BeautifulSoup(response.text, "lxml")
div = soup.find_all("div", class_="ipc-accordion__item__content")[5]
genre_spans = div.find_all("span", class_="ipc-chip__text")
genres = [g.text[:-1].strip() if g.text[-1].isdigit() else g.text.strip() for g in genre_spans]

# Function to extract movie data from a single movie element
def extract_movie_data(movie):
    try:
        # Extract title
        title_elem = movie.find("div", class_="ipc-title")
        title = title_elem.a.text.split(".", 1)[1].strip() if title_elem and title_elem.a else "N/A"

        # Extract year, duration, and certification
        metadata_div = movie.find("div", class_="sc-15ac7568-6")
        year, duration, certification = "N/A", "N/A", "N/A"
        if metadata_div:
            spans = metadata_div.find_all("span")
            year = spans[0].text.strip() if len(spans) > 0 else "N/A"
            duration = spans[1].text.strip() if len(spans) > 1 else "N/A"
            certification = spans[2].text.strip() if len(spans) > 2 else "N/A"

        # Extract ratings and vote count
        rating_elem = movie.find("div", class_="sc-17ce9e4b-0")
        ratings, rating_votes_count = "N/A", "N/A"
        if rating_elem and rating_elem.span:
            rating_text = rating_elem.span.text.strip()
            parts = rating_text.split()
            ratings = parts[0] if parts else "N/A"
            rating_votes_count = parts[1].strip("()") if len(parts) > 1 else "N/A"

        return {
            "title": title,
            "year": year,
            "duration": duration,
            "certification": certification,
            "ratings": ratings,
            "rating_votes_count": rating_votes_count
        }
    except Exception as e:
        print(f"Error processing movie: {e}")
        return None

# Loop through each genre
for genre in genres:
    print(f"Scraping genre: {genre}")
    movies_collected = 0
    page = 1
    genre_movies = []

    while movies_collected < 1500:
        # Construct URL with pagination
        genre_url = f"https://www.imdb.com/search/title/?genres={genre}&start={(page-1)*50+1}"
        try:
            # Make request with error handling
            movie_resp = requests.get(genre_url, headers=header)
            movie_resp.raise_for_status()
            movie_soup = BeautifulSoup(movie_resp.text, "lxml")

            # Find all movies on the page
            movies = movie_soup.find_all("li", class_="ipc-metadata-list-summary-item")
            print(f"Page {page} for {genre}: Found {len(movies)} movies")  # Added line to show movies per page
            if not movies:
                print(f"No more movies found for {genre} at page {page}")
                break

            # Process each movie
            for movie in movies:
                if movies_collected >= 1500:
                    break
                    
                movie_data = extract_movie_data(movie)
                if movie_data:
                    movie_data["genre"] = genre
                    genre_movies.append(movie_data)
                    movies_collected += 1

                # Print progress
                if movies_collected % 100 == 0:
                    print(f"Collected {movies_collected} movies for {genre}")

            # Increment page
            page += 1

            # Random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))

        except requests.RequestException as e:
            print(f"Error fetching page {page} for {genre}: {e}")
            time.sleep(5)  # Wait longer before retrying
            continue

    # Add genre movies to main list
    all_movies_data.extend(genre_movies)
    print(f"Finished collecting {len(genre_movies)} movies for {genre}")

    # Save intermediate results to avoid data loss
    df = pd.DataFrame(all_movies_data)
    df.to_csv(f"im db_movies_{uuid4()}.csv", index=False)

# Create final DataFrame and save
final_df = pd.DataFrame(all_movies_data)
final_df.to_csv("imdb_movies_final.csv", index=False)
print(f"Scraping complete. Total movies collected: {len(all_movies_data)}")
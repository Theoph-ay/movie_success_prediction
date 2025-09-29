# Importing required libraries
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import pandas as pd
from uuid import uuid4
from selenium.common.exceptions import TimeoutException, WebDriverException, ElementClickInterceptedException

# Setup Chrome options
options = webdriver.ChromeOptions()
options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)
options.add_argument("--headless=new")  # Consider removing for testing
options.add_argument("--disable-blink-features=AutomationControlled")  # Anti-bot evasion
options.add_experimental_option("excludeSwitches", ["enable-automation"])

# Initialize Chrome driver
path = r"C:\Users\HP\.wdm\drivers\chromedriver\win64\140.0.7339.207\chromedriver-win32\chromedriver.exe"
driver = webdriver.Chrome(service=Service(path), options=options)

# Scraping IMDb for genres
genre_url = "https://www.imdb.com/search/title/"
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
}
response = requests.get(genre_url, headers=header)
soup = BeautifulSoup(response.text, "lxml")

# Extract genres (limit to first genre for testing)
div = soup.find_all("div", class_="ipc-accordion__item__content")[5]
genre_spans = div.find_all("span", class_="ipc-chip__text")
genres = [
    g.text[:-1].strip() if g.text[-1].isdigit() else g.text.strip() for g in genre_spans
]
genres = genres[:1]  # Test only the first genre

# Container for all movie data
all_movies_data = []

# Function to extract movie details
def extract_movie(movie):
    try:
        # Extract movie name
        name_element = movie.find("h3", class_="ipc-title__text")
        if name_element:
            raw_name = name_element.get_text(strip=True)
            # Remove leading number and period (e.g., "1. ", "2. ")
            name = re.sub(r'^\d+\.\s*', '', raw_name)
        else:
            name = "N/A"

        # Extract IMDb ID
        link_element = movie.find("a", class_="ipc-title-link-wrapper")
        imdb_id = link_element['href'].split("/")[2] if link_element and link_element['href'] else "N/A"

        # Extract metadata (year, duration, certification)
        metadata_div = movie.find("div", class_="sc-15ac7568-6 fqJJPW dli-title-metadata")
        year, movie_duration, certification = "N/A", "N/A", "Series"
        if metadata_div:
            spans = metadata_div.find_all("span")
            year = spans[0].text.strip() if len(spans) > 0 else "N/A"
            movie_duration = spans[1].text.strip() if len(spans) > 1 else "N/A"
            certification = spans[2].text.strip() if len(spans) > 2 else "Series"

        # Extract ratings and vote count
        rating_span = movie.find("span", class_="ipc-rating-star--rating")
        vote_count_span = movie.find("span", class_="ipc-rating-star--voteCount")
        ratings = rating_span.get_text(strip=True) if rating_span else "N/A"
        rating_votes_count = vote_count_span.get_text(strip=True).strip("()") if vote_count_span else "N/A"

        return {
            "name": name,
            "imdb_id": imdb_id,
            "year": year,
            "ratings": ratings,
            "vote_count": rating_votes_count,
            "movie_duration": movie_duration,
            "movie_certification": certification
        }
    except Exception as e:
        print(f"Error extracting movie data: {e}")
        return {
            "name": "N/A",
            "imdb_id": "N/A",
            "year": "N/A",
            "ratings": "N/A",
            "vote_count": "N/A",
            "movie_duration": "N/A",
            "movie_certification": "Series"
        }

# Scrape first genre
genre = genres[0]
print(f"Scraping genre: {genre}")
movies_collected = 0
genre_movies = []
seen_imdb_ids = set()
max_attempts = 3  # Maximum retry attempts for clicking "See More"

# Load the initial page
genre_url = f"https://www.imdb.com/search/title/?genres={genre}&title_type=feature&count=50"
try:
    driver.get(genre_url)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "ipc-metadata-list-summary-item__c"))
    )
except Exception as e:
    print(f"Error loading initial page for genre {genre}: {e}")
    driver.quit()
    exit()

while movies_collected < 100:
    attempt = 0
    while attempt < max_attempts:
        try:
            # Parse current page
            movie_soup = BeautifulSoup(driver.page_source, "lxml")
            movies = movie_soup.find_all("div", class_="ipc-metadata-list-summary-item__c")
            print(f"Found {len(movies)} movies for genre {genre} on attempt {attempt + 1}")

            if not movies:
                print(f"No movies found for genre {genre}")
                break

            # Process new movies
            for movie in movies:
                if movies_collected >= 100:
                    break
                
                movie_data = extract_movie(movie)
                if movie_data and movie_data.get("imdb_id") not in seen_imdb_ids and movie_data["name"] != "N/A":
                    movie_data["genre"] = genre
                    genre_movies.append(movie_data)
                    seen_imdb_ids.add(movie_data["imdb_id"])
                    movies_collected += 1

                    # Print progress
                    if movies_collected % 10 == 0:
                        print(f"Collected {movies_collected} movies for {genre}")

            # Check for "See More" button
            try:
                see_more_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[@class='ipc-see-more__text' and contains(text(), 'more')]"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", see_more_button)
                time.sleep(random.uniform(0.5, 1))  # Brief pause after scrolling
                driver.execute_script("arguments[0].click();", see_more_button)  # JavaScript click
                time.sleep(random.uniform(2, 5))  # Increased sleep time
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ipc-metadata-list-summary-item__c"))
                )
                break  # Exit retry loop if successful
            except (TimeoutException, ElementClickInterceptedException) as e:
                print(f"Error clicking 'See More' button on attempt {attempt + 1}: {e}")
                attempt += 1
                if attempt == max_attempts:
                    print(f"No more pages for genre {genre} after {max_attempts} attempts")
                    break
                time.sleep(random.uniform(1, 3))  # Wait before retrying
            except Exception as e:
                print(f"Unexpected error clicking 'See More' button: {e}")
                attempt += 1
                if attempt == max_attempts:
                    print(f"No more pages for genre {genre} after {max_attempts} attempts")
                    break
        except WebDriverException as e:
            print(f"WebDriver error on attempt {attempt + 1}: {e}")
            attempt += 1
            if attempt == max_attempts:
                print(f"Failed to load page after {max_attempts} attempts")
                break
        time.sleep(random.uniform(1, 3))  # Wait before retrying

    if attempt == max_attempts or not movies:
        break

# Add genre movies to all movies
all_movies_data.extend(genre_movies)
print(f"Finished scraping {len(genre_movies)} movies for genre {genre}")

# Close the driver
driver.quit()

# Save data to a DataFrame and print
df = pd.DataFrame(all_movies_data)
print(df)

# Save to CSV
df.to_csv(f"movies_test_{uuid4()}.csv", index=False)
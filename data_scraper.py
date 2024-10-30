import os
import re
import warnings

import pandas as pd
from colorama import Fore
from colorama import init as colorama_init
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
import time

warnings.filterwarnings('ignore')
colorama_init()

########################################################################
WAIT_TIME = 4  # Default wait time(Seconds) before each bot action.
APP_NAME = "Clash of Clans"  # From validated input in validation.py
NUM_OF_CALL = 100  # From validated input in validation.py
USER = os.getlogin()  # Getting active user name.
FULL_PATH = f"reviews/{APP_NAME.title()}_reviews.csv"

########################################################################


# url to google playstore games page
URL = 'https://play.google.com/store/games'
# URL = 'https://play.google.com/store/apps/details?id=de.rewe.app.mobile'

# Windowless mode feature (Chrome) and chrome message handling.
options = webdriver.ChromeOptions()
options.headless = True  # Runs driver without opening a chrome browser.
options.add_experimental_option("excludeSwitches", ["enable-logging"])

# Initialization of web driver"C:\Users\phili\Documents\chromedriver-win64\chromedriver.exe"
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Use ChromeDriverManager to dynamically download and manage ChromeDriverdriver = webdriver.Chrome('C:\\Users\\phili\\Documents\\chromedriver_win32 (1)\\chromedriver.exe')  # Optional argument, if not specified will search path.
# driver = webdriver.Chrome(options=options)
# Optional argument, if not specified will search path.

# driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options = options)
driver.get(URL)

reviews_list = []
ratings_list = []
app_reviews_ratings = {}


def navigate_app():
    """
    Function finds and clears the search box, enters the name of the app
    hits the enter button the navigates to the app page.
    """
    # Just some friendly user message
    print("Scraping data....")
    print("Exercise patience as this may take up to 10 minutes or more.")
    # Finds the search icon by ID and clicks on it
    search_icon = driver.find_element(by=By.CLASS_NAME, value="google-material-icons.r9optf")
    search_icon.click()
    # Enter app name into search bar and hits enter
    search_box = driver.find_element(by=By.CLASS_NAME, value="HWAcU")
    search_box.clear()  # Clear search box
    # Deleted enter game name; enter_game_name = search_box.send_keys(app_name.lower())
    search_box.send_keys(APP_NAME.lower())
    time.sleep(WAIT_TIME)
    search_box.send_keys(Keys.ENTER)  # Clicks enter for search box
    time.sleep(WAIT_TIME)
    clickable_box = driver.find_element(by=By.CLASS_NAME, value="Qfxief")
    app_page_url = clickable_box.get_attribute('href')
    print(app_page_url)
    driver.get(app_page_url)
    open_all_reviews()


def open_all_reviews():
    """This function navigates to the 'See all reviews' link and clicks it"""
    # Wait for reviews section to be present
    grid_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-g-id="reviews"]'))
    )
    
    # Find all buttons with this class
    buttons = driver.find_elements(By.CLASS_NAME, 'VfPpkd-LgbsSe')
    print(f"Found {len(buttons)} buttons with class VfPpkd-LgbsSe")
    
    # Click the last button
    last_button = buttons[-1]
    print("Clicking last button with text:", last_button.text)
    driver.execute_script("arguments[0].click();", last_button)
    
    # Wait for the reviews dialog to appear and be fully loaded
    time.sleep(2)
    
    # Try to find and click cancel button if it exists
    try:
        cancel_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-id="IbE0S"]'))
        )
        driver.execute_script("arguments[0].click();", cancel_button)
    except:
        print("Cancel button not found or not clickable, continuing...")
    
    # Locate the scrollable area for reviews
    review_scroll = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "fysCi"))
    )
    
    # Rest of the function...
    popup = driver.find_element(by=By.CLASS_NAME, value="VfPpkd-wzTsW")
    print(f"popup {popup}")
    review_scroll = driver.find_element(by=By.CLASS_NAME, value="fysCi")
    # Just some friendly user message
    print("Fetching data, hang in there....")
    
    # Scroll through reviews using JavaScript
    for _ in tqdm(range(NUM_OF_CALL)):
        # Scroll down by 500 pixels each time
        driver.execute_script("arguments[0].scrollTop += 500;", review_scroll)
        # Small delay to allow content to load
        time.sleep(0.5)

    # Your function to collect reviews
    collect_reviews()


def collect_reviews():
    """
    This function gatheres all the data and stores them inside a dictionary
    """
    time.sleep(WAIT_TIME)
    # Just some friendly user message
    print("Currently organizing data....")
    time.sleep(1)
    print("This may take some time, based on the amount of data you're scraping.... hang in there a bit.")
    reviews = driver.find_elements(by=By.CLASS_NAME, value="h3YV2d")  # Locates reviews
    star_ratings = driver.find_elements(by=By.CLASS_NAME, value="iXRFPc")  # Locates ratings
    time.sleep(WAIT_TIME)
    for (review, rating) in zip(reviews, star_ratings):
        review = review.text  # Extracts reviews
        star_rating = rating.get_attribute("aria-label")  # Extracts the strings from "aria-label" attribute
        star_rating = re.findall(r"\d", star_rating) # Extracts the integer rating as list
        star_rating = star_rating[0]  # Removes rating from list

        reviews_list.append(review)  # adds each review to reviews list
        ratings_list.append(star_rating)  # adds each rating to ratings list

    # Creates dictionary and adds list of reviews and ratings
    app_reviews_ratings["reviews"] = reviews_list
    app_reviews_ratings["ratings"] = ratings_list
    driver.quit()  # Closes driver window and ends driver session
    save_review_dataframe()


def save_review_dataframe():
    """
    Saves dataframe in CSV file format.
    """
    # Just some friendly user message
    print("Storing data, almost done....")
    reviews_ratings_df = pd.DataFrame(app_reviews_ratings)
    reviews_ratings_df = reviews_ratings_df.iloc[1:, ]
    time.sleep(2)
    # Convert to CSV and save in Downloads.
    reviews_ratings_df.to_csv(FULL_PATH, index=False)
    data_rows = "{:,}".format(reviews_ratings_df.shape[0])
    print(
        "\n"f"{Fore.LIGHTGREEN_EX}{data_rows} rows of data have been saved to downloadas as {APP_NAME.title()}_reviews.csv.")
    print("See you again next time ;-)")


if __name__ == "__main__": # Main function
    navigate_app()

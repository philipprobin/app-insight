import requests
from bs4 import BeautifulSoup
from google_play_scraper import app as get_app_details, reviews as get_app_reviews, Sort
import re
from pathlib import Path
from langdetect import detect
from utils.file_handler import FileHandler


def clean_description(description):
    description = re.sub(r'<.*?>', '', description)  # Remove HTML tags
    description = re.sub(r'http\S+|www\S+', '', description)  # Remove links
    description = ' '.join(description.split())  # Remove extra whitespace
    return description


def fetch_reviews(app_id, max_reviews=200, region="us"):
    """Fetch up to max_reviews English reviews for a specific app."""
    review_data = []
    batch_size = 100  # Number of reviews to fetch per batch
    batch_number = 1  # Track the current batch number
    lang = "en" if region.lower() == "us" else "de"

    while len(review_data) < max_reviews:
        try:
            # Fetch a batch of reviews
            result, _ = get_app_reviews(
                app_id,
                lang=lang,
                country=region,
                count=batch_size,
                sort=Sort.NEWEST
            )

            if not result or len(result) < batch_size:
                print(f"No more reviews available after batch {batch_number}.")
                break

            print(
                f"Processing batch {batch_number} for app ID {app_id} - {len(review_data)} {lang} reviews collected so far")

            for review in result:
                content = review["content"]
                try:
                    if detect(content) == lang:
                        review_data.append(content)
                        if len(review_data) >= max_reviews:
                            break
                except:
                    continue

            batch_number += 1

        except Exception as e:
            print(f"Failed to fetch reviews for app ID {app_id} in batch {batch_number}: {e}")
            break

    print(f"Finished fetching reviews for app ID {app_id} - Total {lang} reviews collected: {len(review_data)}")
    return review_data[:max_reviews]


def fetch_apps(app_id, region="us", num_results=10, save_dir=Path("competitors")):
    """Fetch app details and reviews for a reference app and its competitors."""
    reference_app_data = {}

    # Fetch reference app details
    try:
        app_details = get_app_details(app_id)
        reference_app_data = {
            "inAppProductPrice": app_details.get('inAppProductPrice', "N/A"),
            "reviews": fetch_reviews(app_id, max_reviews=200, region=region),
            "ratings": app_details.get('score', "No rating"),
            "installs": app_details.get('installs', "Unknown installs"),
            "title": app_details['title'],
            "description": clean_description(app_details.get('description', 'Description not found')),
            "genre": app_details.get('genre', 'Genre not found'),
            "app_id": app_id,
            "icon_url": app_details.get("icon"),  # Directly get icon URL from app details
        }
        print(f"Fetched details for app ID {app_id}.")
    except Exception as e:
        print(f"Failed to fetch details for app ID {app_id}: {e}")

    search_term = reference_app_data["title"]

    """Fetches apps data including up to 200 reviews and saves to JSON."""
    hl, gl = ("de", "DE") if region.lower() == "de" else ("en", "US")
    search_term_formatted = search_term.replace(" ", "%20")
    url = f"https://play.google.com/store/search?q={search_term_formatted}&c=apps&hl={hl}&gl={gl}"

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to retrieve the page.")
        return {}

    soup = BeautifulSoup(response.text, 'html.parser')

    # Collect competitor apps
    competitors_data = []
    for idx, app in enumerate(soup.find_all('a', class_='Si6A0c Gy4nib'), start=1):
        if idx > num_results:
            break
        title = app.find('span', class_='DdYX5').text if app.find('span', 'DdYX5') else None
        link = "https://play.google.com" + app['href'] if app.has_attr('href') else None
        package_name = link.split("id=")[-1] if link else None
        icon_url = app.find('img', class_='T75of stzEZd')['src'] if app.find('img', class_='T75of stzEZd') else None

        if package_name:
            try:
                app_details = get_app_details(package_name)
                competitor_info = {
                    "inAppProductPrice": app_details.get('inAppProductPrice', "N/A"),
                    "reviews": fetch_reviews(package_name, max_reviews=200, region=region),
                    "ratings": app_details.get('score', "No rating"),
                    "installs": app_details.get('installs', "Unknown installs"),
                    "title": title,
                    "description": clean_description(app_details.get('description', 'Description not found')),
                    "genre": app_details.get('genre', 'Genre not found'),
                    "app_id": package_name,
                    "icon_url": icon_url  # Add icon URL for the competitor
                }
                competitors_data.append(competitor_info)
                print(f"Fetched data for competitor app '{title}'.")
            except Exception as e:
                print(f"Failed to fetch data for {title}: {e}")

    all_apps_data = {"reference_app": reference_app_data, "competitors": competitors_data}
    FileHandler.save_json(all_apps_data, save_dir, app_id)
    print(f"Apps data saved for '{app_id}' in '{save_dir}'.")

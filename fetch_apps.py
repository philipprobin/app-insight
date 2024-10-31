# fetch_apps.py
import requests
from bs4 import BeautifulSoup
from google_play_scraper import app as get_app_details
import re
from pathlib import Path
from utils.file_handler import FileHandler

def clean_description(description):
    description = re.sub(r'<.*?>', '', description)  # Remove HTML tags
    description = re.sub(r'http\S+|www\S+', '', description)  # Remove links
    description = ' '.join(description.split())  # Remove extra whitespace
    return description

def fetch_apps(search_term, app_id, region="us", num_results=10, save_dir=Path("./competitors")):
    """Fetches apps data and saves to JSON."""
    hl, gl = ("de", "DE") if region.lower() == "de" else ("en", "US")
    search_term_formatted = search_term.replace(" ", "%20")
    url = f"https://play.google.com/store/search?q={search_term_formatted}&c=apps&hl={hl}&gl={gl}"

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to retrieve the page.")
        return {}

    soup = BeautifulSoup(response.text, 'html.parser')
    reference_app_data = {}

    # Fetch reference app details
    try:
        app_details = get_app_details(app_id)
        reference_app_data = {
            "inAppProductPrice": app_details.get('inAppProductPrice', "N/A"),
            "reviews": app_details.get('reviews', "No reviews"),
            "ratings": app_details.get('score', "No rating"),
            "installs": app_details.get('installs', "Unknown installs"),
            "title": app_details['title'],
            "description": clean_description(app_details.get('description', 'Description not found')),
            "genre": app_details.get('genre', 'Genre not found'),
            "app_id": app_id
        }
        print(f"Fetched details for app ID {app_id}.")
    except Exception as e:
        print(f"Failed to fetch details for app ID {app_id}: {e}")

    # Collect competitor apps
    competitors_data = []
    for idx, app in enumerate(soup.find_all('a', class_='Si6A0c Gy4nib'), start=1):
        if idx > num_results:
            break
        title = app.find('span', class_='DdYX5').text if app.find('span', class_='DdYX5') else None
        link = "https://play.google.com" + app['href'] if app.has_attr('href') else None
        package_name = link.split("id=")[-1] if link else None

        if package_name:
            try:
                app_details = get_app_details(package_name)
                competitor_info = {
                    "inAppProductPrice": app_details.get('inAppProductPrice', "N/A"),
                    "reviews": app_details.get('reviews', "No reviews"),
                    "ratings": app_details.get('score', "No rating"),
                    "installs": app_details.get('installs', "Unknown installs"),
                    "title": title,
                    "description": clean_description(app_details.get('description', 'Description not found')),
                    "genre": app_details.get('genre', 'Genre not found'),
                    "app_id": package_name
                }
                competitors_data.append(competitor_info)
            except Exception as e:
                print(f"Failed to fetch data for {title}: {e}")

    all_apps_data = {"reference_app": reference_app_data, "competitors": competitors_data}
    FileHandler.save_json(all_apps_data, save_dir, app_id)
    print(f"Apps data saved for '{app_id}' in '{save_dir}'.")

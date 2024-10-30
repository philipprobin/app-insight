import requests
from bs4 import BeautifulSoup
from google_play_scraper import app as get_app_details, search
import pandas as pd
from tabulate import tabulate
import json
import re


def clean_description(description):
    description = re.sub(r'<.*?>', '', description)  # Remove HTML tags
    description = re.sub(r'http\S+|www\S+', '', description)  # Remove links
    description = ' '.join(description.split())  # Remove extra whitespace
    return description


def fetch_apps(search_term, app_id=None, region="us", num_results=10):
    hl, gl = ("de", "DE") if region.lower() == "de" else ("en", "US")

    search_term_formatted = search_term.replace(" ", "%20")
    url = f"https://play.google.com/store/search?q={search_term_formatted}&c=apps&hl={hl}&gl={gl}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to retrieve the page. Status code:", response.status_code)
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, 'html.parser')
    print("Page parsed successfully.")

    # Fetch details for the specific app ID if provided
    main_app_data = []
    if app_id:
        try:
            app_details = get_app_details(app_id)
            main_app_data.append({
                "app_id": app_id,
                "title": app_details['title'],
                "rating": app_details.get('score', "No rating"),
                "genre": app_details.get('genre', 'Genre not found'),
                "description": clean_description(app_details.get('description', 'Description not found'))
            })
            print(f"Fetched details for app ID {app_id}.")
        except Exception as e:
            print(f"Failed to fetch details for app ID {app_id}: {e}")

    # Collect search results, limiting to the specified number
    search_results = []
    for idx, app in enumerate(soup.find_all('a', class_='Si6A0c Gy4nib'), start=1):
        if idx > num_results:
            break
        title = app.find('span', class_='DdYX5').text if app.find('span', class_='DdYX5') else None
        link = "https://play.google.com" + app['href'] if app.has_attr('href') else None
        package_name = link.split("id=")[-1] if link else None

        if package_name:
            try:
                app_details = get_app_details(package_name)
                genre = app_details.get('genre', 'Genre not found')
                description = clean_description(app_details.get('description', 'Description not found'))
            except Exception as e:
                genre = "Genre not found"
                description = "Description not found"
                print(f"Failed to fetch genre or description for {title}: {e}")
        else:
            genre = "No link found"
            description = "No description found"

        if title:
            search_results.append({
                "app_id": package_name,
                "title": title,
                "rating": app_details.get('score', "No rating") if package_name else "No rating",
                "genre": genre,
                "description": description
            })

    # Combine main app and search results in a DataFrame
    all_apps = main_app_data + search_results
    print(f"Total apps fetched: {len(all_apps)}")

    return pd.DataFrame(all_apps)


def save_to_json(apps_listed, use_app_name_as_key=False):
    """
    Saves the apps data to JSON. Uses app name as key if `use_app_name_as_key` is True,
    otherwise uses app ID as key.
    """
    if use_app_name_as_key:
        apps_dict = {app['title']: app['description'] for app in apps_listed if 'title' in app}
    else:
        apps_dict = {app['app_id']: app['description'] for app in apps_listed if 'app_id' in app}

    with open("apps_descriptions.json", "w", encoding="utf-8") as json_file:
        json.dump(apps_dict, json_file, ensure_ascii=False, indent=4)
    print("JSON file 'apps_descriptions.json' created successfully.")


def main():
    app_id = "com.ubercab"  # Set the desired app_id
    use_app_name_as_key = False  # Set to True to use app name as key, False to use app ID

    # Fetch the app name based on the app_id
    try:
        app_details = get_app_details(app_id)
        search_term = app_details['title']  # Use the title as the search term
        print(f"Using '{search_term}' as the search term based on app_id '{app_id}'.")
    except Exception as e:
        print(f"Failed to fetch app details for app_id '{app_id}': {e}")
        return

    # Execute the search and data fetch
    apps_df = fetch_apps(search_term, app_id=app_id, region="us", num_results=10)

    # Display the DataFrame
    print("App List:")
    print(tabulate(apps_df, headers='keys', tablefmt='grid'))

    # Save the cleaned descriptions in JSON, with app name or app ID as key based on the flag
    save_to_json(apps_df.to_dict(orient='records'), use_app_name_as_key)


# Run the main function
main()

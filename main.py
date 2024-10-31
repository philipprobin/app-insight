# main.py
from fetch_apps import fetch_apps
from calculate_similarity import calculate_similarity

def main():
    app_id = "org.telegram.messenger"
    search_term = "Telegram"
    region = "us"
    num_results = 10

    # Step 1: Fetch app data and save it to /competitors
    fetch_apps(search_term, app_id, region=region, num_results=num_results)

    # Step 2: Calculate similarity scores and save to /ratings
    calculate_similarity(app_id)

if __name__ == '__main__':
    main()

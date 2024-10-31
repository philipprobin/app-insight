# main.py
from services.fetch_apps import fetch_apps
from services.calculate_similarity import calculate_similarity
from services.review_analyzer import ReviewAnalyzer


def main():
    app_id = "de.sparmahl"
    search_term = "SparMahl"
    region = "de"
    num_results = 10

    # Step 1: Fetch app data and save it to /competitors
    fetch_apps(search_term, app_id, region=region, num_results=num_results)

    # Step 2: Calculate similarity scores and save to /ratings
    calculate_similarity(app_id)

    # Step 3: Analyze reviews and save insights to /insights
    analyzer = ReviewAnalyzer(app_id)
    analyzer.analyze()

if __name__ == '__main__':
    main()

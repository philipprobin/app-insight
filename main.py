# main.py
from services.fetch_apps import fetch_apps
from services.calculate_similarity import calculate_similarity
from services.review_analyzer import ReviewAnalyzer
from services.merge_data import merge_app_data


def main():
    app_id = "com.instagram.android"
    region = "de"
    num_results = 10

    # Step 1: Fetch app data and save it to /competitors
    fetch_apps(app_id, region=region, num_results=num_results)

    # Step 2: Calculate similarity scores and save to /ratings
    calculate_similarity(app_id)

    # Step 3: Analyze reviews and save insights to /insights
    analyzer = ReviewAnalyzer(app_id)
    analyzer.analyze()

    # Step 4: Merge data from /competitors and /insights, save to /analysis_result
    result: dict = merge_app_data(app_id)


if __name__ == '__main__':
    main()

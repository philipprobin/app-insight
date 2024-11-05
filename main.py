from datetime import datetime

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

import time
from services.fetch_apps import fetch_apps
from services.calculate_similarity import calculate_similarity
from services.review_analyzer import ReviewAnalyzer
from services.merge_data import merge_app_data
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase initialization
cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
firebase_admin.initialize_app(cred)
db = firestore.client()  # Firestore client


def main():
    # Specify the parameters
    app_id = "notion.id"
    region = "us"
    num_results = 10
    user_id = "xpP2VJFjBzZIj5LK8GP3OeM54XU2"

    print(f"Running analysis for userId: {user_id}, appId: {app_id}")

    try:
        # Step 1: Fetch app data and save it to /competitors
        fetch_apps(app_id, region=region, num_results=num_results)
        print("Step 1: Fetched app data")

        # Step 2: Calculate similarity scores and save to /ratings
        calculate_similarity(app_id)
        print("Step 2: Calculated similarity scores")

        # Step 3: Analyze reviews and save insights to /insights
        analyzer = ReviewAnalyzer(app_id)
        analyzer.analyze(5)
        print("Step 3: Analyzed reviews")

        # Step 4: Merge data from /competitors and /insights, save to /analysis_result
        result = merge_app_data(app_id)
        print("Step 4: Merged data")

        # Output the result to confirm completion
        print("Final result:", result)

    except Exception as e:
        print("Error:", e)


if __name__ == '__main__':
    main()

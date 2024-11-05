import os
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
from services.fetch_apps import fetch_apps
from services.calculate_similarity import calculate_similarity
from services.review_analyzer import ReviewAnalyzer
from services.merge_data import merge_app_data
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
CORS(app)

# Firebase initialization
cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
firebase_admin.initialize_app(cred)
db = firestore.client()  # Firestore client

@app.route("/", methods=["GET"])
def run_main():
    app_id = request.args.get("appId", "com.instagram.android")
    region = request.args.get("region", "de")
    num_results = int(request.args.get("num_results", 10))
    user_id = request.args.get("userId")  # Get the user ID from the request

    if not user_id:
        return jsonify({"status": "error", "error": "User ID is required"}), 400

    print(f"Received request from userId: {user_id}")  # Print user ID for debugging

    try:
        # Run the main steps sequentially
        fetch_apps(app_id, region=region, num_results=num_results)
        calculate_similarity(app_id)
        analyzer = ReviewAnalyzer(app_id)
        analyzer.analyze(5)
        result = merge_app_data(app_id)

        # Store the result in Firestore under analyses/userId/appId/timestamp
        # When writing the document
        # Format timestamp as yyyymmddhhmmss
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        result["timestamp"] = timestamp  # Add timestamp as a field in the result data

        # Store the result in Firestore under users/userId/analyses/appId
        doc_name = f"{app_id};{timestamp}"
        doc_ref = db.collection("users").document(user_id).collection("analyses").document(doc_name)
        doc_ref.set(result)

        # Return the final result as JSON
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

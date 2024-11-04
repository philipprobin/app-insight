from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from services.fetch_apps import fetch_apps
from services.calculate_similarity import calculate_similarity
from services.review_analyzer import ReviewAnalyzer
from services.merge_data import merge_app_data

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route("/", methods=["GET"])
def run_main():
    # Get parameters from URL, with defaults if not provided
    app_id = request.args.get("appId", "com.instagram.android")
    region = request.args.get("region", "de")
    num_results = int(request.args.get("num_results", 10))

    try:
        # Run the main steps sequentially
        fetch_apps(app_id, region=region, num_results=num_results)
        calculate_similarity(app_id)
        analyzer = ReviewAnalyzer(app_id)
        analyzer.analyze()
        result = merge_app_data(app_id)  # Get the final merged data

        # Return the final result as JSON
        return jsonify(result), 200

    except Exception as e:
        # Catch any errors and include them in the response
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

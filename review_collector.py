import json
import os
from google_play_scraper import reviews, Sort


def load_similarity_scores(file_path):
    """Load similarity scores from the provided JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_top_apps(similarity_scores, top_n=6):
    """Get the top N apps with the highest similarity scores."""
    sorted_apps = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)
    top_apps = sorted_apps[:top_n]
    return [app[0] for app in top_apps]


def fetch_reviews(app_id, count=200):
    """Fetch the first 200 reviews for a given app ID."""
    result, _ = reviews(
        app_id,
        lang='en',  # Specify the language of reviews
        country='us',  # Specify the region
        sort=Sort.NEWEST,  # Sort reviews by newest
        count=count  # Number of reviews to fetch
    )
    return [review['content'] for review in result]


def save_reviews_to_json(reviews_dict, filename):
    """Save the reviews dictionary to a JSON file."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(reviews_dict, f, ensure_ascii=False, indent=4)
    print(f"Reviews saved to '{filename}'.")


def main():
    # Path to the similarity scores JSON
    similarity_scores_file = "ratings/gpt-4o-mini _app_names_prompt3.json"

    # Load similarity scores
    similarity_scores = load_similarity_scores(similarity_scores_file)

    # Get the top 6 apps by score
    top_app_ids = get_top_apps(similarity_scores, top_n=6)
    print("Top 6 apps:", top_app_ids)

    # Reference app name (assumes the first app in the list has a score of 1.0)
    reference_app_id = top_app_ids[0]

    # Fetch reviews for each top app
    reviews_dict = {}
    for app_id in top_app_ids:
        print(f"Fetching reviews for app ID: {app_id}")
        reviews_dict[app_id] = fetch_reviews(app_id, count=200)

    # Save reviews in a JSON file using the reference app name
    reference_app_name = reference_app_id.replace(".", "_")  # Replace dots for a valid filename
    output_file = f"reviews/{reference_app_name}.json"
    save_reviews_to_json(reviews_dict, output_file)


if __name__ == '__main__':
    main()

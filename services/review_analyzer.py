# review_analyzer.py

import os
import json
import re
import openai
from utils.file_handler import FileHandler
from utils.system_prompts import generate_insights_prompt
from pathlib import Path
from utils.cost_calculator import CostCalculator


class ReviewAnalyzer:
    def __init__(self, app_id):
        self.app_id = app_id

    openai.api_key = os.getenv("OPENAI_API_KEY")

    def load_reviews(self):
        """Load reviews for the top 5 highest-rated competitors from latest /ratings and /competitors files."""
        competitors_dir = Path("competitors")
        ratings_dir = Path("ratings")

        # Load the latest ratings file for the app
        ratings_data = FileHandler.get_latest_json(ratings_dir, self.app_id)
        if not ratings_data:
            print("No ratings found.")
            return None

        # Sort competitors by rating in descending order and select top 5
        sorted_competitors = sorted(ratings_data.items(), key=lambda x: x[1], reverse=True)[:5]
        top_competitors = [comp[0] for comp in sorted_competitors]  # Extract only app names

        # Load the latest competitors file for the app
        reviews_data = FileHandler.get_latest_json(competitors_dir, self.app_id)
        if not reviews_data:
            print("No competitor data found.")
            return None

        # Extract reviews for top-rated competitors
        top_reviews = {}

        # Add reference_app reviews
        top_reviews[reviews_data["reference_app"]["app_id"]] = reviews_data["reference_app"]["reviews"]

        # Add top competitors' reviews
        for comp in reviews_data["competitors"]:
            if comp["title"] in top_competitors:
                top_reviews[comp["app_id"]] = comp["reviews"]

        if not top_reviews:
            print("No reviews found for top competitors.")
            return None

        return top_reviews

    def generate_insights(self, reviews_data):
        """Generate insights by processing reviews through the OpenAI model."""
        messages = [
            {
                "role": "system",
                "content": [generate_insights_prompt]
            },
            {
                "role": "user",
                "content": json.dumps(reviews_data)
            }
        ]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=1,
                max_tokens=4096,  # increased token size
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
        except Exception as e:
            print(f"API call failed: {e}")
            return None

        # Extract response content
        assistant_reply = response['choices'][0]['message']['content']
        input_tokens = response['usage']['prompt_tokens']
        output_tokens = response['usage']['completion_tokens']
        total_cost = CostCalculator.calculate_api_cost(input_tokens, output_tokens)
        print(f"INSIGHT COST: ${total_cost:.4f}")

        # Parse JSON from assistant's reply
        try:
            json_str = re.search(r'\{.*\}', assistant_reply, re.DOTALL).group(0)
            insights_data = json.loads(json_str)
            return insights_data
        except Exception as e:
            print(f"Failed to parse assistant's reply as JSON. {e}")
            print("Assistant's reply:", assistant_reply)
            return None

    def analyze(self):
        """Load reviews, generate insights, and save the results."""
        reviews_data = self.load_reviews()
        if reviews_data:
            insights_data = self.generate_insights(reviews_data)
            if insights_data:
                insights_dir = Path("insights")
                # Use FileHandler to save without replacing dots
                FileHandler.save_json(insights_data, insights_dir, self.app_id)
                print(f"Insights saved to '{insights_dir}/{self.app_id}.json'.")

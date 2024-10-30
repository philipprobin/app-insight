import json
import re
import os
from apikey import openai_key  # Make sure your API key is correctly imported
import openai

# Pricing constants
INPUT_COST = 0.150 / 1_000_000  # Cost per million input tokens
OUTPUT_COST = 0.6 / 1_000_000  # Cost per million output tokens
CACHED_INPUT_COST = 0.075 / 1_000_000  # Cost per million cached input tokens

class ModelInsightAnalyser:
    def __init__(self, reviews_json_path):
        self.reviews_json_path = reviews_json_path
        openai.api_key = openai_key

    def calculate_cost(self, input_tokens, output_tokens, cached=False):
        """
        Calculate the cost based on the number of input and output tokens.
        """
        input_cost = (CACHED_INPUT_COST if cached else INPUT_COST) * input_tokens
        output_cost = OUTPUT_COST * output_tokens
        return input_cost + output_cost

    def load_reviews(self):
        """
        Load reviews from the JSON file.
        """
        with open(self.reviews_json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_insights(self, reviews_data):
        """
        Generate insights by processing reviews through the OpenAI model.
        """
        system_prompt = {
            "type": "text",
            "text": "The input is a JSON object containing app IDs as keys and lists of user reviews as values. "
                    "Here's an example:\n\n"
                    "{\n"
                    "    \"com.ubercab\": [\n"
                    "        \"Great app but crashes frequently.\",\n"
                    "        \"Driver rates are too high.\",\n"
                    "        \"Easy to use but payment fails sometimes.\"\n"
                    "    ]\n"
                    "}\n\n"
                    "Analyze these reviews to extract insights about all the apps. Identify common user pain points, positive feedback, "
                    "and suggestions for improvement. For each insight, provide:\n"
                    "1. A title summarizing the issue or positive aspect.\n"
                    "2. The number of users mentioning this issue.\n"
                    "3. Four representative quotes from users about this issue.\n"
                    "4. Sentiments associated with the issue using one of the following enums:\n\n"
                    "    SATISFIED, DISSATISFIED, HAPPY, ANGRY, EXCITED, DISAPPOINTED, SURPRISED, FRUSTRATED, GRATEFUL,\n"
                    "    CONFUSED, RELIEVED, AMAZED, UNSURE, IMPRESSED, DISGUSTED, APPRECIATIVE, NEUTRAL, ENTHUSIASTIC, SAD,\n"
                    "    HOPEFUL, CONCERNED, TRUSTING, REGRETFUL\n\n"
                    "Format the output as follows:\n"
                    "{\n"
                    "    \"apps\": [\n"
                    "        {\n"
                    "            \"appId\": \"com.ubercab\",\n"
                    "            \"insights\": [\n"
                    "                {\n"
                    "                    \"title\": \"Annoying Crashes\",\n"
                    "                    \"amount\": 50,\n"
                    "                    \"quotes\": [\n"
                    "                        \"The app crashes often.\",\n"
                    "                        \"I can't complete a ride without the app crashing.\",\n"
                    "                        \"Crashes happen every time I open the app.\",\n"
                    "                        \"Unstable, crashes a lot.\"\n"
                    "                    ],\n"
                    "                    \"sentiments\": [\"FRUSTRATED\", \"DISAPPOINTED\"]\n"
                    "                },\n"
                    "                {...}\n"
                    "            ]\n"
                    "        }\n"
                    "       {...}\n"
                    "    ]\n"
                    "}\n\n"
                    "Please output only the JSON object and no additional text."
        }

        app_id = list(reviews_data.keys())[0]  # Assuming we have a single app ID in the input
        messages = [
            {
                "role": "system",
                "content": [system_prompt]
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
                max_tokens=2048,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                response_format={
                    "type": "json_object"
                }
            )
        except Exception as e:
            print(f"API call failed: {e}")
            return None

        # Extract the assistant's reply containing the JSON object
        assistant_reply = response['choices'][0]['message']['content']
        input_tokens = response['usage']['prompt_tokens']
        output_tokens = response['usage']['completion_tokens']

        # Calculate and print the cost
        total_cost = self.calculate_cost(input_tokens, output_tokens)
        print(f"Total cost for this request: ${total_cost:.4f}")

        # Parse the JSON object from the assistant's reply
        try:
            json_str = re.search(r'\{.*\}', assistant_reply, re.DOTALL).group(0)
            insights_data = json.loads(json_str)
            return insights_data
        except Exception as e:
            print("Failed to parse assistant's reply as JSON.")
            print("Assistant's reply:")
            print(assistant_reply)
            return None

    def save_insights(self, insights_data, app_id):
        """
        Save insights data to a JSON file.
        """
        os.makedirs("insights", exist_ok=True)
        filename = f"insights/{app_id.replace('.', '_')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(insights_data, f, ensure_ascii=False, indent=4)
        print(f"Insights saved to '{filename}'.")

    def analyze(self):
        """
        Load reviews, generate insights, and save the results.
        """
        reviews_data = self.load_reviews()
        app_id = list(reviews_data.keys())[0]  # Get the app ID from the JSON data
        insights_data = self.generate_insights(reviews_data)
        if insights_data:
            self.save_insights(insights_data, app_id)

# Example usage
if __name__ == '__main__':
    analyser = ModelInsightAnalyser("reviews/com_ubercab.json")
    analyser.analyze()

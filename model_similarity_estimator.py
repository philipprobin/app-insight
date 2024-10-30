import json
import re
from apikey import openai_key  # Make sure your API key is correctly imported
import openai

# Pricing constants
INPUT_COST = 0.150 / 1_000_000  # $2.50 per million input tokens
OUTPUT_COST = 0.6 / 1_000_000  # $10.00 per million output tokens
CACHED_INPUT_COST = 0.075 / 1_000_000  # $1.25 per million cached input tokens

def calculate_cost(input_tokens, output_tokens, cached=False):
    """
    Calculate the cost based on the number of input and output tokens.
    If `cached` is True, a lower cost is applied for cached input tokens.
    """
    input_cost = (CACHED_INPUT_COST if cached else INPUT_COST) * input_tokens
    output_cost = OUTPUT_COST * output_tokens
    return input_cost + output_cost

def main():
    # Set up OpenAI API key
    openai.api_key = openai_key

    # Define the input and output JSON file paths
    input_json = 'apps_descriptions.json'  # Path to the input JSON file
    output_json = 'ratings/gpt-4o-mini _app_names_prompt3.json'       # Path to the output JSON file

    # Read the input JSON file
    with open(input_json, 'r', encoding='utf-8') as f:
        app_descriptions = json.load(f)

    # Prepare the system prompt with enhanced clarity
    system_prompt = {
        "type": "text",
        "text": "The input is a JSON object containing app IDs as keys and descriptions as values. Here’s an example:\n\n"
                "{\n"
                "    \"com.bonial.kaufda\": \"Deal discovery at its best...\",\n"
                "    \"com.marktguru.mg2.de\": \"Marktguru is your location...\",\n"
                "    \"de.prospektangebote.app\": \"Discover the brochures...\"\n"
                "}\n\n"
                "Your task is to compute similarity scores between first app (the one that appears first in the JSON) "
                "and the other apps. The similarity score will be used to identify competitors on the same market. You "
                "should use the knowledge you already have or can gather from the"
                "descriptions to compute these scores. Give higher similarity scores the more the app is a competitor "
                "on the same market. Give lower scores the more the core functionality differs.\n\n"
                "The output should be a JSON object with the same app IDs as keys and similarity scores as values. "
                "The similarity score should be a float between 0.00 and 1.00 (2 decimals after point), where 1.0 indicates identical apps,"
                "and the reference app (the first one in the input JSON) should have a score of 1.0.\n\n"
                "Please output only the JSON object with similarity scores and no additional text."
    }

    # Prepare the API request using OpenAI playground structure
    client = openai

    try:
        response = client.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": [system_prompt]
                },
                {
                    "role": "user",
                    "content": json.dumps(app_descriptions)
                }
            ],
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
        return

    # Extract the assistant's reply containing the JSON object
    assistant_reply = response['choices'][0]['message']['content']
    input_tokens = response['usage']['prompt_tokens']
    output_tokens = response['usage']['completion_tokens']

    # Parse the JSON object from the assistant's reply
    try:
        # Use regex to find the JSON object in the reply
        json_str = re.search(r'\{.*\}', assistant_reply, re.DOTALL).group(0)
        similarity_scores = json.loads(json_str)
    except Exception as e:
        print("Failed to parse assistant's reply as JSON.")
        print("Assistant's reply:")
        print(assistant_reply)
        return

    # Calculate and print the cost
    total_cost = calculate_cost(input_tokens, output_tokens)
    print(f"Total cost for this request: ${total_cost:.4f}")

    # Save the output JSON with similarity scores
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(similarity_scores, f, ensure_ascii=False, indent=4)

    print(f"Similarity scores saved to '{output_json}'.")

if __name__ == '__main__':
    main()

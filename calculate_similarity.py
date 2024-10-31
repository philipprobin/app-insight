# calculate_similarity.py
import json
import openai
import re
from api_key import openai_key
from utils.cost_calculator import CostCalculator
from utils.file_handler import FileHandler
from system_prompts import system_prompt
from pathlib import Path


def set_openai_api_key():
    openai.api_key = openai_key


def calculate_similarity(app_id, input_dir=Path("./competitors"), output_dir=Path("./ratings")):
    """Calculates similarity scores for the latest app data."""
    set_openai_api_key()

    app_descriptions = FileHandler.get_latest_json(input_dir, app_id)
    if app_descriptions is None:
        print("No app descriptions found.")
        return

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": [system_prompt]},
                {"role": "user", "content": json.dumps(app_descriptions)}
            ],
            max_tokens=2048, temperature=1
        )
    except Exception as e:
        print(f"API call failed: {e}")
        return

    assistant_reply = response['choices'][0]['message']['content']
    json_str = re.search(r'\{.*\}', assistant_reply, re.DOTALL).group(0)
    similarity_scores = json.loads(json_str)

    # Calculate and save cost information
    input_tokens, output_tokens = response['usage']['prompt_tokens'], response['usage']['completion_tokens']
    total_cost = CostCalculator.calculate_api_cost(input_tokens, output_tokens)
    print(f"Total cost: ${total_cost:.4f}")

    output_path = FileHandler.save_json(similarity_scores, output_dir, app_id)
    print(f"Similarity scores saved to '{output_path}'")
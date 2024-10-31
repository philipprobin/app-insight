system_prompt = {
    "type": "text",
    "text": "The input is a JSON object containing app IDs as keys and descriptions as values. Here’s an example:\n\n"
            "{\n"
            "    \"com.bonial.kaufda\": \"Deal discovery at its best...\",\n"
            "    \"com.marktguru.mg2.de\": \"Marktguru is your location...\",\n"
            "    \"de.prospektangebote.app\": \"Discover the brochures...\"\n"
            "}\n\n"
            "Your task is to compute similarity scores between the first app (the one that appears first in the JSON) "
            "and the other apps. The similarity score will be used to identify competitors on the same market. Use your "
            "knowledge and the descriptions provided to compute these scores. Give higher similarity scores the more the app "
            "is a competitor on the same market. Lower scores if the core functionality differs.\n\n"
            "The output should be a JSON object with the same app IDs as keys and similarity scores as values. "
            "The similarity score should be a float between 0.00 and 1.00 (2 decimals after the point), where 1.0 indicates identical apps, "
            "and the reference app (the first one in the input JSON) should have a score of 1.0.\n\n"
            "Please output only the JSON object with similarity scores and no additional text."
}

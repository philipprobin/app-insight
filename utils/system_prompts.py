system_prompt = {
    "type": "text",
    "text": "The input is a JSON object with two main keys: 'reference_app' and 'competitors'.\n\n"
            "- 'reference_app' contains the title and description of the main app you will use as the basis for comparison.\n"
            "- 'competitors' is a list of other apps, each with its own title and description.\n\n"
            "Your task is to compute similarity scores between the 'reference_app' and each app in the 'competitors' list. "
            "The similarity score will be used to identify competitors on the same market. Use your knowledge and the descriptions provided to compute these scores. "
            "Give higher similarity scores to apps that are more similar in purpose and functionality to the 'reference_app', and lower scores if the core functionality differs.\n\n"
            "The output should be a JSON object with the titles of each competitor app as keys and similarity scores as values. "
            "The similarity score should be a float between 0.00 and 1.00 (2 decimals after the point), where 1.0 indicates identical functionality and purpose to the 'reference_app'.\n\n"
            "Please output only the JSON object with similarity scores and no additional text."
}

# system_prompts.py

generate_insights_prompt = {
    "type": "text",
    "text": "The input is a JSON object where each key is an app ID, and each value is a list of user reviews. "
            "Here's an example:\n\n"
            "{\n"
            "    \"com.ubercab\": [\n"
            "        \"Great app but crashes frequently.\",\n"
            "        \"Driver rates are too high.\",\n"
            "        \"Easy to use but payment fails sometimes.\"\n"
            "    ]\n"
            "}\n\n"
            "Your task is to analyze these reviews thoroughly and extract as many meaningful insights as possible "
            "for each app. Ensure that for every app with reviews, there is at least one insight in the output. "
            "The more insights you can identify, the better.\n\n"
            "For each insight, provide:\n"
            "1. A title that clearly summarizes the main issue or positive aspect.\n"
            "2. The total number of users who mentioned this issue or aspect.\n"
            "3. A list of all user quotes related to this issue, with the number of quotes matching the count specified in point 2.\n"
            "4. Associated sentiments for each issue, using one or more of the following categories:\n\n"
            "    SATISFIED, DISSATISFIED, HAPPY, ANGRY, EXCITED, DISAPPOINTED, SURPRISED, FRUSTRATED, GRATEFUL,\n"
            "    CONFUSED, RELIEVED, AMAZED, UNSURE, IMPRESSED, DISGUSTED, APPRECIATIVE, NEUTRAL, ENTHUSIASTIC, SAD,\n"
            "    HOPEFUL, CONCERNED, TRUSTING, REGRETFUL\n\n"
            "Structure the output as follows:\n"
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
            "        },\n"
            "       {...}\n"
            "    ]\n"
            "}\n\n"
            "Please output only the JSON object without additional text. Make sure that each app with reviews has at least one insight listed. The more insights you can identify from the reviews, the better."
}

# services/merge_data.py
from pathlib import Path
from utils.file_handler import FileHandler


def merge_app_data(app_id):
    """Merge competitor data and insights for a given app ID into a single file."""
    competitors_dir = Path("competitors")
    insights_dir = Path("insights")
    analysis_result_dir = Path("analysis_result")

    # Load competitors data
    competitors_data = FileHandler.get_latest_json(competitors_dir, app_id)
    if competitors_data is None:
        print(f"No competitor data found for app ID '{app_id}'.")
        return

    # Remove reviews from the reference app and competitors
    competitors_data["reference_app"].pop("reviews", None)
    for competitor in competitors_data.get("competitors", []):
        competitor.pop("reviews", None)

    # Load insights data
    insights_data = FileHandler.get_latest_json(insights_dir, app_id)
    if insights_data is None:
        print(f"No insights data found for app ID '{app_id}'.")
        return

    # Find insights for the reference app and competitors
    reference_app_insights = next((app for app in insights_data.get("apps", []) if app["appId"] == app_id), None)
    competitor_insights = {
        app["appId"]: app["insights"]
        for app in insights_data.get("apps", [])
        if app.get("insights")  # This checks that insights is not empty
    }

    # Merge insights into reference app
    merged_data = {
        "reference_app": {
            **competitors_data["reference_app"],
            "insights": reference_app_insights.get("insights", []) if reference_app_insights else []
        },
        "competitors": []
    }

    # Merge insights into each competitor if available, and only include competitors with non-empty insights
    for competitor in competitors_data["competitors"]:
        competitor_id = competitor["app_id"]
        insights = competitor_insights.get(competitor_id, [])

        if insights:  # Only include competitors with non-empty insights
            competitor["insights"] = insights
            merged_data["competitors"].append(competitor)

    # Save the merged data to the analysis_result directory
    FileHandler.save_json(merged_data, analysis_result_dir, app_id)
    print(f"Analysis result saved to '{analysis_result_dir}/{app_id}.json'.")
    return merged_data

import json
from datetime import datetime
from pathlib import Path


class FileHandler:
    @staticmethod
    def save_json(data: dict, directory: Path, prefix: str) -> Path:
        """Save data as JSON with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.json"

        directory.mkdir(exist_ok=True)
        filepath = directory / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return filepath

    @staticmethod
    def get_latest_json(directory: Path, prefix: str) -> dict:
        """Get most recent JSON file with given prefix"""
        files = list(directory.glob(f"{prefix}_*.json"))
        if not files:
            return None

        latest_file = max(files, key=lambda x: x.stat().st_mtime)
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def extract_titles_and_descriptions(data: dict) -> dict:
        """
        Extracts only the titles and descriptions from the provided data
        in a format suitable for the similarity model.
        """
        extracted_data = {
            "reference_app": {
                "title": data["reference_app"].get("title", ""),
                "description": data["reference_app"].get("description", "")
            },
            "competitors": [
                {
                    "title": competitor.get("title", ""),
                    "description": competitor.get("description", "")
                }
                for competitor in data.get("competitors", [])
            ]
        }
        return extracted_data

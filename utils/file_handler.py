from pathlib import Path
import json


class FileHandler:
    @staticmethod
    def save_json(data: dict, directory: Path, prefix: str) -> Path:
        """Save data as JSON without timestamp."""
        filename = f"{prefix}.json"  # Remove timestamp from filename

        directory.mkdir(exist_ok=True)
        filepath = directory / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return filepath

    @staticmethod
    def get_latest_json(directory: Path, prefix: str) -> dict:
        """Retrieve JSON file by exact prefix without timestamp."""
        filepath = directory / f"{prefix}.json"  # Match the exact filename
        if not filepath.exists():
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
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

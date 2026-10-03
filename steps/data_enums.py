import requests

# Global variable to store fetched literals
import json

_literals_cache = None
def fetch_literals():
    global _literals_cache
    if _literals_cache is not None:
        return _literals_cache  # Return cached version

    try:
        response = requests.get("https://h2research.org/backend/public/api/get-bot-filters")  # Adjust port if needed
        response.raise_for_status()
        json_data = response.json()

        if json_data.get("status") and "data" in json_data:
            _literals_cache = json_data["data"]  # Cache the data
            print("literals_cache is: ",_literals_cache['systems'][0])
            return _literals_cache
            
        else:
            print("Invalid response format or status is false")
            return {}
    except requests.exceptions.RequestException as e:
        print(f"Error calling /getLiterals: {e}")
        return {}
        
        
import json

_literals_cache = None

def fetch_literals():
    global _literals_cache
    if _literals_cache is not None:
        return _literals_cache  # Return cached version

    try:
        with open("FieldsJson.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        if data.get("status") and "data" in data:
            _literals_cache = data["data"]
            return _literals_cache
        else:
            print("Invalid JSON format or 'status' is false")
            return {}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading literals.json: {e}")
        return {}

# def get_system_lists():
#     data = fetch_literals()
#     # print("systems_Data",data)
#     return [item["name"] for item in data.get("system", [])]


def get_species_lists():
    data = fetch_literals()
    return [item["name"] for item in data.get("species", [])]


# def get_study_types_lists():
#     data = fetch_literals()
#     return [item["name"] for item in data.get("study_type", [])]
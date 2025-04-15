import urllib.parse

user_selections = {
    "start_date": "2025-01-01",
    "end_date": "2025-01-05",
    "business_unit": "OBU",
    "therapeutic_area": "Oncology",
    "disease_indication": "Breast Cancer",
}

base_url = "http://localhost:5001/summary"
query_string = urllib.parse.urlencode(user_selections)
full_url = f"{base_url}?{query_string}"

print(full_url)

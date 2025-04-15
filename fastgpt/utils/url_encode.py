import urllib.parse
import json

data = {
    "business_unit": "Pharma",
    "therapeutic_area": "Oncology",
    "disease_indication": "Cancer",
}

encoded_data = urllib.parse.quote(json.dumps(data))
url = f"http://localhost:5001/?interro_selection={encoded_data}"

print(url)

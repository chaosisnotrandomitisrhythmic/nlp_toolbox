import requests
import json

# API endpoint
url = "http://0.0.0.0:5001/conversation"

# Example payload using the specified interro_selection
payload = {
    "user_id": "user123",
    "interro_selection": {
        "business_unit": "Pharma",
        "therapeutic_area": "Oncology",
        "disease_indication": "Cancer"
    }
}

# Make the POST request
response = requests.post(url, json=payload)

# Print the response
print("Status Code:", response.status_code)
print("Response:", response.json())
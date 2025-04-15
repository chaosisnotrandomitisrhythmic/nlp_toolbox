import httpx
import asyncio

API_TIMEOUT = 30.0

http_client = httpx.AsyncClient(timeout=API_TIMEOUT)


async def test_dummy_summary():
    # The endpoint URL
    url = "http://localhost:8000/dummy-summary"

    # The request parameters
    params = {
        "start_date": "2024-01-01",
        "end_date": "2024-03-20",
        "business_unit": "Oncology",
        "therapeutic_area": "Cancer",
        "disease_indication": "Lung Cancer",
    }

    # Make the POST request
    response = await http_client.post(url, json=params)

    # Check if the request was successful
    if response.status_code == 200:
        result = response.json()
        print("Summary ID:", result["result"]["id"])
        print("Summary HTML:", result["result"]["summary"])
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    asyncio.run(test_dummy_summary())

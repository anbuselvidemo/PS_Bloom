"""Client for the City of Melbourne 'Microclimate Sensor Readings' dataset.

Docs: https://data.melbourne.vic.gov.au/explore/dataset/microclimate-sensor-readings/
The dataset is served through Opendatasoft's Explore API v2, which is a
plain paginated JSON endpoint (no auth needed for public read access).
"""
import time
import requests

BASE_URL = (
    "https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/"
    "microclimate-sensor-readings/records"
)
PAGE_SIZE = 100  # API max per page is 100


def fetch_records(limit=1000, timeout=15, max_retries=3):
    """Fetch up to `limit` raw records from the API, paginating as needed.

    Basic retry on transient network/HTTP errors since this hits a public
    API over the internet.
    """
    records = []
    offset = 0

    while len(records) < limit:
        page_size = min(PAGE_SIZE, limit - len(records))
        params = {"limit": page_size, "offset": offset}

        for attempt in range(1, max_retries + 1):
            try:
                resp = requests.get(BASE_URL, params=params, timeout=timeout)
                resp.raise_for_status()
                break
            except requests.RequestException as exc:
                if attempt == max_retries:
                    raise RuntimeError(
                        f"Failed to fetch data from API after {max_retries} attempts"
                    ) from exc
                time.sleep(2 * attempt)  # simple backoff

        page = resp.json().get("results", [])
        if not page:
            break  # no more data available

        records.extend(page)
        offset += len(page)

    return records

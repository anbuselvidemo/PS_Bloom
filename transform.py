"""Turn raw API records into the flat dict shape `db.insert_readings` expects.

ASSUMPTION: the live API was not reachable from this environment while
writing this exercise, so field names are based on the published data
dictionary. Before running against production, confirm the exact field
names with a quick `curl` against the endpoint in api_client.py and adjust
FIELD_MAP below if they differ (e.g. if temperature/humidity come back as
separate rows via a `type`/`value` pair instead of dedicated columns).
"""

FIELD_MAP = {
    "site_id": "site_id",
    "reading_time": "time",
    "temperature": "air_temperature",
    "humidity": "relative_humidity",
    "latitude": "latitude",
    "longitude": "longitude",
}


def transform_record(raw):
    """Map one raw API record to our DB row shape.

    Returns None if the record is missing the fields we need to key on
    (site_id + time), since we can't dedupe or store it meaningfully.
    """
    site_id = raw.get(FIELD_MAP["site_id"])
    reading_time = raw.get(FIELD_MAP["reading_time"])

    if not site_id or not reading_time:
        return None

    return {
        "site_id": str(site_id),
        "reading_time": reading_time,
        "temperature": raw.get(FIELD_MAP["temperature"]),
        "humidity": raw.get(FIELD_MAP["humidity"]),
        "latitude": raw.get(FIELD_MAP["latitude"]),
        "longitude": raw.get(FIELD_MAP["longitude"]),
    }


def transform_records(raw_records):
    """Transform a list of raw records, silently dropping unusable ones."""
    rows = [transform_record(r) for r in raw_records]
    return [r for r in rows if r is not None]

"""Turn raw API records into the flat dict shape `db.insert_readings` expects.

Confirmed against a live sample of the `microclimate-sensors-data` API
(one row per reading, not a type/value pair as an earlier, deprecated
dataset used). Real field names:

    device_id            -> site_id
    received_at          -> reading_time
    airtemperature       -> temperature
    relativehumidity     -> humidity
    latlong.lat / .lon   -> latitude / longitude

Other fields in the payload (wind speed/direction, atmospheric pressure,
pm25, pm10, noise) aren't needed for the analyst team's stated use case
(temperature/humidity by location and time) and are ignored here.
"""

FIELD_MAP = {
    "site_id": "device_id",
    "reading_time": "received_at",
    "temperature": "airtemperature",
    "humidity": "relativehumidity",
}


def transform_record(raw):
    """Map one raw API record to our DB row shape.

    Returns None if the record is missing the fields we key duplicates on
    (site_id + reading_time), since it can't be safely stored.
    """
    site_id = raw.get(FIELD_MAP["site_id"])
    reading_time = raw.get(FIELD_MAP["reading_time"])

    if not site_id or not reading_time:
        return None

    latlong = raw.get("latlong") or {}

    return {
        "site_id": str(site_id),
        "reading_time": reading_time,
        "temperature": raw.get(FIELD_MAP["temperature"]),
        "humidity": raw.get(FIELD_MAP["humidity"]),
        "latitude": latlong.get("lat"),
        "longitude": latlong.get("lon"),
    }


def transform_records(raw_records):
    """Transform a list of raw records, silently dropping unusable ones."""
    rows = [transform_record(r) for r in raw_records]
    return [r for r in rows if r is not None]

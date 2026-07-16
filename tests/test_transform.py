from transform import transform_record, transform_records


def test_transform_record_maps_real_fields():
    raw = {
        "device_id": "ICTMicroclimate-03",
        "received_at": "2023-05-18T06:09:52+00:00",
        "sensorlocation": "CH1 rooftop",
        "latlong": {"lon": 144.96728, "lat": -37.8140348},
        "airtemperature": 12.4,
        "relativehumidity": 68.2,
        "atmosphericpressure": 1016.7,
        "pm25": 1.0,
        "pm10": 3.0,
        "noise": 87.7,
    }
    row = transform_record(raw)
    assert row == {
        "site_id": "ICTMicroclimate-03",
        "reading_time": "2023-05-18T06:09:52+00:00",
        "temperature": 12.4,
        "humidity": 68.2,
        "latitude": -37.8140348,
        "longitude": 144.96728,
    }


def test_transform_record_missing_key_fields_returns_none():
    assert transform_record({"airtemperature": 12.4}) is None
    assert transform_record({"device_id": "ICTMicroclimate-03"}) is None


def test_transform_record_handles_missing_latlong():
    raw = {
        "device_id": "ICTMicroclimate-03",
        "received_at": "2023-05-18T06:09:52+00:00",
        "airtemperature": 12.4,
        "relativehumidity": 68.2,
    }
    row = transform_record(raw)
    assert row["latitude"] is None
    assert row["longitude"] is None


def test_transform_records_drops_unusable_rows():
    raw_records = [
        {"device_id": "ICTMicroclimate-03", "received_at": "2023-05-18T06:09:52+00:00", "airtemperature": 12.4},
        {"airtemperature": 99},
    ]
    rows = transform_records(raw_records)
    assert len(rows) == 1
    assert rows[0]["site_id"] == "ICTMicroclimate-03"

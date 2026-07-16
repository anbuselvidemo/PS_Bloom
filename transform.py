from transform import transform_records


def test_pivots_temperature_and_humidity_rows_together():
    raw_records = [
        {"site_id": 1011, "local_time": "2026-01-01T00:15:00+00:00", "type": "TPH.TEMP", "value": 21.5},
        {"site_id": 1011, "local_time": "2026-01-01T00:15:00+00:00", "type": "TPH.RH", "value": 55.0},
    ]
    rows = transform_records(raw_records)
    assert len(rows) == 1
    assert rows[0]["site_id"] == "1011"
    assert rows[0]["reading_time"] == "2026-01-01T00:15:00+00:00"
    assert rows[0]["temperature"] == 21.5
    assert rows[0]["humidity"] == 55.0


def test_different_site_or_time_produce_separate_rows():
    raw_records = [
        {"site_id": 1011, "local_time": "2026-01-01T00:15:00+00:00", "type": "TPH.TEMP", "value": 21.5},
        {"site_id": 1011, "local_time": "2026-01-01T00:30:00+00:00", "type": "TPH.TEMP", "value": 21.8},
        {"site_id": 1012, "local_time": "2026-01-01T00:15:00+00:00", "type": "TPH.TEMP", "value": 19.0},
    ]
    rows = transform_records(raw_records)
    assert len(rows) == 3


def test_unrecognised_type_is_ignored():
    raw_records = [
        {"site_id": 1011, "local_time": "2026-01-01T00:15:00+00:00", "type": "PM2.5", "value": 8.0},
    ]
    rows = transform_records(raw_records)
    assert rows == []


def test_missing_site_id_or_time_is_dropped():
    raw_records = [
        {"type": "TPH.TEMP", "value": 21.5},
        {"site_id": 1011, "type": "TPH.TEMP", "value": 21.5},
    ]
    rows = transform_records(raw_records)
    assert rows == []


def test_partial_reading_still_included_with_null_other_field():
    # A site/time might only have a temperature reading with no matching
    # humidity row (or vice versa) if the sensor didn't report one.
    raw_records = [
        {"site_id": 1011, "local_time": "2026-01-01T00:15:00+00:00", "type": "TPH.TEMP", "value": 21.5},
    ]
    rows = transform_records(raw_records)
    assert len(rows) == 1
    assert rows[0]["temperature"] == 21.5
    assert rows[0]["humidity"] is None
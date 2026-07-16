from unittest.mock import patch, MagicMock

from api_client import fetch_records


def _mock_response(results):
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = {"results": results}
    return resp


@patch("api_client.requests.get")
def test_fetch_records_stops_when_page_is_empty(mock_get):
    mock_get.side_effect = [
        _mock_response([{"site_id": "1"}] * 100),
        _mock_response([]),  # no more data
    ]
    records = fetch_records(limit=1000)
    assert len(records) == 100
    assert mock_get.call_count == 2


@patch("api_client.requests.get")
def test_fetch_records_respects_limit(mock_get):
    def respond(url, params, timeout):
        return _mock_response([{"site_id": "1"}] * params["limit"])

    mock_get.side_effect = respond
    records = fetch_records(limit=250)
    assert len(records) == 250
    assert mock_get.call_count == 3  # 100 + 100 + 50

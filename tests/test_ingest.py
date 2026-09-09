from datetime import date
from unittest.mock import Mock

import pytest
import requests

from electricity_pipeline.config import Settings
from electricity_pipeline.ingest import fetch_prices


def test_fetch_prices_returns_json_data(monkeypatch):
    fake_response = Mock()
    fake_response.json.return_value = {
        "data": {"attributes": {"title": "Test"}},
        "included": [],
    }

    mock_get = Mock(return_value=fake_response)
    monkeypatch.setattr("requests.get", mock_get)

    settings = Settings(
        ree_api_base_url="https://test.example",
        database_url="postgresql://fake",
    )

    result = fetch_prices(date(2026, 1, 1), date(2026, 1, 31), settings)

    assert result == fake_response.json.return_value


def test_fetch_prices_raises_http_error(monkeypatch):
    fake_response = Mock()
    fake_response.raise_for_status.side_effect = requests.HTTPError("Bad Request")

    mock_get = Mock(return_value=fake_response)
    monkeypatch.setattr("requests.get", mock_get)

    settings = Settings(
        ree_api_base_url="https://test.example",
        database_url="postgresql://fake",
    )

    with pytest.raises(requests.HTTPError):
        fetch_prices(date(2026, 1, 1), date(2026, 1, 31), settings)

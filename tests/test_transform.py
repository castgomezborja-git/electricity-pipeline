from decimal import Decimal

import pytest

from electricity_pipeline.transform import (
    parse_pvpc_prices,
    parse_spot_prices,
)

## Tests for the parse_pvpc_prices function


def test_parse_pvpc_prices_raises_when_indicator_missing():
    raw_data = {"included": []}

    with pytest.raises(ValueError):
        parse_pvpc_prices(raw_data)


def test_parse_pvpc_prices_returns_validated_prices():
    # Arrange
    raw_data = {
        "included": [
            {
                "id": "1001",
                "attributes": {
                    "values": [
                        {"value": 225.38, "datetime": "2026-09-06T00:00:00.000+02:00"},
                        {"value": -8.57, "datetime": "2026-09-06T11:00:00.000+02:00"},
                    ]
                },
            }
        ]
    }

    # Act
    result = parse_pvpc_prices(raw_data)

    # Assert
    assert len(result) == 2
    assert result[0].price_eur_mwh == Decimal("225.38")
    assert result[1].price_eur_mwh == Decimal("-8.57")


def test_parse_pvpc_prices_accepts_negative_prices():
    raw_data = {
        "included": [
            {
                "id": "1001",
                "attributes": {
                    "values": [
                        {"value": -6.63, "datetime": "2026-09-06T12:00:00.000+02:00"},
                    ]
                },
            }
        ]
    }

    result = parse_pvpc_prices(raw_data)

    assert result[0].price_eur_mwh == Decimal("-6.63")


### Tests for the parse_spot_prices function


def test_parse_spot_prices_raises_when_indicator_missing():
    raw_data = {"included": []}

    with pytest.raises(ValueError):
        parse_spot_prices(raw_data)


def test_parse_spot_prices_returns_validated_prices():
    # Arrange
    raw_data = {
        "included": [
            {
                "id": "600",
                "attributes": {
                    "values": [
                        {"value": 225.38, "datetime": "2026-09-06T00:00:00.000+02:00"},
                        {"value": -8.57, "datetime": "2026-09-06T11:00:00.000+02:00"},
                    ]
                },
            }
        ]
    }

    # Act
    result = parse_spot_prices(raw_data)

    # Assert
    assert len(result) == 2
    assert result[0].price_eur_mwh == Decimal("225.38")
    assert result[1].price_eur_mwh == Decimal("-8.57")


def test_parse_spot_prices_accepts_negative_prices():
    raw_data = {
        "included": [
            {
                "id": "600",
                "attributes": {
                    "values": [
                        {"value": -6.63, "datetime": "2026-09-06T12:00:00.000+02:00"},
                    ]
                },
            }
        ]
    }

    result = parse_spot_prices(raw_data)

    assert result[0].price_eur_mwh == Decimal("-6.63")

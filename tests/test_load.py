from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select

from electricity_pipeline.load import load_pvpc_prices, load_spot_prices
from electricity_pipeline.models import PVPCPriceModel, SpotMarketPriceModel
from electricity_pipeline.schemas import PVPCPrice, SpotMarketPrice


def test_load_pvpc_prices_inserts_new_price(db_session):
    price_datetime = datetime(2026, 1, 1, tzinfo=UTC)

    load_pvpc_prices(
        [PVPCPrice(price_datetime=price_datetime, price_eur_mwh=Decimal("100.0"))],
        db_session,
    )

    rows = db_session.execute(select(PVPCPriceModel)).scalars().all()

    assert len(rows) == 1
    assert rows[0].price_datetime == price_datetime
    assert rows[0].price_eur_mwh == Decimal("100.0")


def test_load_pvpc_prices_updates_existing_price(db_session):
    price_datetime = datetime(2026, 1, 1, tzinfo=UTC)

    load_pvpc_prices(
        [PVPCPrice(price_datetime=price_datetime, price_eur_mwh=Decimal("100.0"))],
        db_session,
    )
    load_pvpc_prices(
        [PVPCPrice(price_datetime=price_datetime, price_eur_mwh=Decimal("50.0"))],
        db_session,
    )

    rows = db_session.execute(select(PVPCPriceModel)).scalars().all()

    assert len(rows) == 1
    assert rows[0].price_eur_mwh == Decimal("50.0")


def test_load_spot_prices_inserts_new_price(db_session):
    price_datetime = datetime(2026, 1, 1, tzinfo=UTC)

    load_spot_prices(
        [
            SpotMarketPrice(
                price_datetime=price_datetime, price_eur_mwh=Decimal("100.0")
            )
        ],
        db_session,
    )

    rows = db_session.execute(select(SpotMarketPriceModel)).scalars().all()

    assert len(rows) == 1
    assert rows[0].price_datetime == price_datetime
    assert rows[0].price_eur_mwh == Decimal("100.0")


def test_load_spot_prices_updates_existing_price(db_session):
    price_datetime = datetime(2026, 1, 1, tzinfo=UTC)

    load_spot_prices(
        [
            SpotMarketPrice(
                price_datetime=price_datetime, price_eur_mwh=Decimal("100.0")
            )
        ],
        db_session,
    )
    load_spot_prices(
        [SpotMarketPrice(price_datetime=price_datetime, price_eur_mwh=Decimal("50.0"))],
        db_session,
    )

    rows = db_session.execute(select(SpotMarketPriceModel)).scalars().all()

    assert len(rows) == 1
    assert rows[0].price_eur_mwh == Decimal("50.0")

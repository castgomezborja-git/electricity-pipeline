from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from electricity_pipeline.models import PVPCPriceModel, SpotMarketPriceModel
from electricity_pipeline.schemas import PVPCPrice, SpotMarketPrice


def load_pvpc_prices(prices: list[PVPCPrice], session: Session) -> None:
    """Inserta precios PVPC, actualizando el valor si el datetime ya existe."""
    for price in prices:
        stmt = insert(PVPCPriceModel).values(
            price_datetime=price.price_datetime,
            price_eur_mwh=price.price_eur_mwh,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["price_datetime"],
            set_={"price_eur_mwh": stmt.excluded.price_eur_mwh},
        )
        session.execute(stmt)
    session.commit()


def load_spot_prices(prices: list[SpotMarketPrice], session: Session) -> None:
    """Inserta precios de mercado spot, actualizando el valor si el datetime ya existe."""
    for price in prices:
        stmt = insert(SpotMarketPriceModel).values(
            price_datetime=price.price_datetime,
            price_eur_mwh=price.price_eur_mwh,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["price_datetime"],
            set_={"price_eur_mwh": stmt.excluded.price_eur_mwh},
        )
        session.execute(stmt)
    session.commit()

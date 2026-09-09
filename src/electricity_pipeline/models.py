from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ElectricityPriceModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    price_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), unique=True
    )
    price_eur_mwh: Mapped[Decimal] = mapped_column(Numeric(10, 2))


class PVPCPriceModel(ElectricityPriceModel):
    __tablename__ = "pvpc_prices"


class SpotMarketPriceModel(ElectricityPriceModel):
    __tablename__ = "spot_market_prices"

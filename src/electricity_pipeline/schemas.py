from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ElectricityPriceBase(BaseModel):
    price_datetime: datetime
    price_eur_mwh: Decimal


class PVPCPrice(ElectricityPriceBase):
    pass


class SpotMarketPrice(ElectricityPriceBase):
    pass

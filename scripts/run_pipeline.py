import logging
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from electricity_pipeline.config import Settings
from electricity_pipeline.ingest import fetch_prices
from electricity_pipeline.load import load_pvpc_prices, load_spot_prices
from electricity_pipeline.models import PVPCPriceModel
from electricity_pipeline.transform import parse_pvpc_prices, parse_spot_prices

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


MADRID_TZ = ZoneInfo("Europe/Madrid")


def determinar_fecha_inicio(session: Session) -> date:
    ultima_fecha = session.execute(
        select(func.max(PVPCPriceModel.price_datetime))
    ).scalar()

    if ultima_fecha is None:
        return date(2026, 9, 1)  # fallback si la tabla está vacía

    return ultima_fecha.astimezone(MADRID_TZ).date() + timedelta(days=1)


settings = Settings()
engine = create_engine(settings.database_url)

with Session(engine) as session:
    fecha_inicio = determinar_fecha_inicio(session)

hoy = datetime.now(tz=MADRID_TZ).date()

if fecha_inicio > hoy:
    logger.info("Ya hay datos cargados hasta hoy, nada que hacer")
else:
    dia_actual = fecha_inicio
    while dia_actual <= hoy:
        logger.info(f"Cargando {dia_actual}...")
        try:
            data = fetch_prices(dia_actual, dia_actual, settings)
            pvpc = parse_pvpc_prices(data)
            spot = parse_spot_prices(data)

            with Session(engine) as session:
                load_pvpc_prices(pvpc, session)
                load_spot_prices(spot, session)

            logger.info(f"OK: {len(pvpc)} PVPC, {len(spot)} spot")
        except Exception:
            logger.exception(f"ERROR en {dia_actual}")

        dia_actual += timedelta(days=1)

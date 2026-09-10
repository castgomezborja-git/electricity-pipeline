from datetime import date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from electricity_pipeline.config import Settings
from electricity_pipeline.ingest import fetch_prices
from electricity_pipeline.load import load_pvpc_prices, load_spot_prices
from electricity_pipeline.transform import parse_pvpc_prices, parse_spot_prices

FECHA_INICIO = date(2026, 9, 3)
FECHA_FIN = date(2026, 9, 10)

settings = Settings()
engine = create_engine(settings.database_url)

dia_actual = FECHA_INICIO
while dia_actual <= FECHA_FIN:
    print(f"Cargando {dia_actual}...")

    try:
        data = fetch_prices(dia_actual, dia_actual, settings)
        pvpc = parse_pvpc_prices(data)
        spot = parse_spot_prices(data)

        with Session(engine) as session:
            load_pvpc_prices(pvpc, session)
            load_spot_prices(spot, session)

        print(f"  OK: {len(pvpc)} PVPC, {len(spot)} spot")
    except Exception as error:  # noqa: BLE001 — backfill debe continuar ante cualquier fallo puntual de un día
        print(f"  ERROR en {dia_actual}: {error}")

    dia_actual += timedelta(days=1)

print("Backfill completado")

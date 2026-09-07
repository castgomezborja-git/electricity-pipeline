from datetime import date

import requests

from electricity_pipeline.config import Settings


def fetch_prices(start_date: date, end_date: date, settings: Settings) -> dict:
    """
    Llama al endpoint de precios en tiempo real de REE y devuelve el JSON crudo.

    No valida ni transforma los datos: esa responsabilidad es de transform.py.
    """
    url = f"{settings.ree_api_base_url}/mercados/precios-mercados-tiempo-real"
    params = {
        "start_date": start_date.isoformat() + "T00:00",
        "end_date": end_date.isoformat() + "T23:59",
        "time_trunc": "hour",
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

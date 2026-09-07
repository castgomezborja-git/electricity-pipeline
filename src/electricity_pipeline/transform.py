from electricity_pipeline.schemas import PVPCPrice, SpotMarketPrice


def _find_indicator_values(raw_data: dict, indicator_id: str) -> list[dict]:
    """
    Busca en raw_data['included'] el indicador con el id dado y devuelve
    su lista de valores crudos (sin transformar).

    Lanza ValueError si el indicador no aparece — preferimos fallar
    explícitamente a que el pipeline siga adelante con datos incompletos.
    """
    for item in raw_data.get("included", []):
        if item.get("id") == indicator_id:
            return item.get("attributes", {}).get("values", [])
    raise ValueError(
        f"Indicador con id={indicator_id!r} no encontrado en la respuesta de la API"
    )


def parse_pvpc_prices(raw_data: dict) -> list[PVPCPrice]:
    """Convierte los valores PVPC del JSON crudo en instancias validadas."""
    values = _find_indicator_values(raw_data, indicator_id="1001")
    return [
        PVPCPrice(datetime=item["datetime"], price_eur_mwh=item["value"])
        for item in values
    ]


def parse_spot_prices(raw_data: dict) -> list[SpotMarketPrice]:
    """Convierte los valores de mercado spot del JSON crudo en instancias validadas."""
    values = _find_indicator_values(raw_data, indicator_id="600")
    return [
        SpotMarketPrice(datetime=item["datetime"], price_eur_mwh=item["value"])
        for item in values
    ]

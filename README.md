# electricity-pipeline

Pipeline ETL para el precio de la electricidad en España, con dashboard interactivo y automatización diaria.

Extrae datos horarios (PVPC) y cuarto-horarios (mercado spot/OMIE) de la API pública de Red Eléctrica de España, los valida y almacena en PostgreSQL, y los expone en un dashboard de Streamlit.

## Stack

- **Python 3.12** + [`uv`](https://docs.astral.sh/uv/) como gestor de dependencias
- **`requests`** para la ingesta desde la API de REE
- **`pydantic`** + **`pydantic-settings`** para validación de datos y configuración
- **`SQLAlchemy 2.0`** + **`psycopg`** (driver v3) sobre **PostgreSQL 16**, vía Docker Compose
- **`Streamlit`** + **`plotly`** + **`pandas`** para el dashboard
- **`pytest`** + **`testcontainers`** para tests (unitarios, mocking HTTP, y base de datos real)
- **`ruff`** para linting y formato

## Arquitectura

API REE → ingest.py → transform.py (pydantic) → load.py (upsert) → PostgreSQL
│
┌─────────────────┴──────────────────┐
▼ ▼
dashboard/app.py scripts/run_pipeline.py
(Streamlit, lectura) (automatización diaria)


Los dos indicadores (PVPC horario y mercado spot cuarto-horario) se guardan en tablas separadas, cada una con su granularidad nativa — no se normalizan a una granularidad común en la carga, para no perder información.

## Requisitos

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- Docker Desktop (para PostgreSQL, y para los tests que usan `testcontainers`)

## Puesta en marcha

1. Clona el repositorio e instala dependencias:
```powershell
   uv sync
```

2. Copia `.env.example` a `.env` y ajusta los valores (usuario/contraseña de PostgreSQL, evitando el símbolo `$` — ver notas más abajo):
```powershell
   cp .env.example .env
```

3. Levanta PostgreSQL:
```powershell
   docker compose up -d
```

4. Crea las tablas:
```powershell
   uv run python -c "from sqlalchemy import create_engine; from electricity_pipeline.config import Settings; from electricity_pipeline.models import Base; engine = create_engine(Settings().database_url); Base.metadata.create_all(engine)"
```

5. Carga datos históricos (opcional, ajusta el rango en el propio script):
```powershell
   uv run python scripts/backfill.py
```

6. Lanza el dashboard:
```powershell
   uv run streamlit run dashboard/app.py
```

## Tests

```powershell
uv run pytest -v
```

Requiere Docker en ejecución (los tests de `load.py` levantan un PostgreSQL real vía `testcontainers`).

## Automatización

`scripts/run_pipeline.py` determina automáticamente qué rango de fechas falta por cargar (consultando `MAX(price_datetime)` en la base de datos) y lo ingiere. En Windows, se dispara diariamente vía Task Scheduler ejecutando `scripts/run_pipeline.ps1` a las 21:00h (después de que REE publique el PVPC definitivo del día siguiente, ~20:15h). Los logs se guardan en `logs/`, uno por día.

## Notas

- Los precios pueden ser negativos (excedente de generación solar) — es un dato válido, no un error.
- Evita el símbolo `$` en `POSTGRES_PASSWORD`: colisiona con la sintaxis de interpolación de variables de Docker Compose.
- Todas las comparaciones de fecha usan explícitamente la zona horaria `Europe/Madrid`, tanto en SQL (`AT TIME ZONE`) como en Python (`zoneinfo`), para evitar desajustes con la zona horaria implícita del sistema/sesión.


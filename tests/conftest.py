import pytest
from testcontainers.community.postgres import PostgresContainer

from electricity_pipeline.models import Base
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session


@pytest.fixture(scope="session")
def postgres_engine():
    with PostgresContainer("postgres:16", driver="psycopg") as postgres:
        engine = create_engine(postgres.get_connection_url())
        Base.metadata.create_all(engine)
        yield engine


@pytest.fixture()
def db_session(postgres_engine):
    with Session(postgres_engine) as session:
        session.execute(
            text("TRUNCATE TABLE pvpc_prices, spot_market_prices RESTART IDENTITY;")
        )
        session.commit()
        yield session

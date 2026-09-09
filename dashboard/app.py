import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text

from electricity_pipeline.config import Settings

settings = Settings()
engine = create_engine(settings.database_url)

st.set_page_config(page_title="Precio de la luz en España", layout="wide")
st.title("Precio de la luz en España")

tab_hoy, tab_historico = st.tabs(["Hoy", "Histórico"])


with tab_hoy:
    N_HORAS_BARATAS = 5
    query = text("""
        SELECT
            price_datetime AT TIME ZONE 'Europe/Madrid' AS price_datetime_local,
            price_eur_mwh
        FROM pvpc_prices
        WHERE (price_datetime AT TIME ZONE 'Europe/Madrid')::date
            = (now() AT TIME ZONE 'Europe/Madrid')::date
        ORDER BY price_datetime
    """)
    df_hoy = pd.read_sql(query, engine)

    horas_baratas = df_hoy.nsmallest(N_HORAS_BARATAS, "price_eur_mwh").sort_values(
        "price_datetime_local"
    )

    st.subheader(f"Las {N_HORAS_BARATAS} horas más baratas de hoy")
    columnas = st.columns(N_HORAS_BARATAS)

    for columna, (_, fila) in zip(columnas, horas_baratas.iterrows()):
        with columna:
            hora = fila["price_datetime_local"].strftime("%H:%M")
            st.metric(label=hora, value=f"{fila['price_eur_mwh']:.2f} €/MWh")

    df_hoy["es_barata"] = df_hoy["price_datetime_local"].isin(
        horas_baratas["price_datetime_local"]
    )

    fig = px.bar(
        df_hoy,
        x="price_datetime_local",
        y="price_eur_mwh",
        color="es_barata",
        color_discrete_map={True: "#2ecc71", False: "#4a4a4a"},
        labels={"price_datetime_local": "Hora", "price_eur_mwh": "€/MWh"},
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


with tab_historico:
    st.write("Pendiente")

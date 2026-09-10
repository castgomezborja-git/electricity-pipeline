from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text

from electricity_pipeline.config import Settings

MADRID_TZ = ZoneInfo("Europe/Madrid")

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

    df_hoy["price_eur_kwh"] = df_hoy["price_eur_mwh"] / 1000  # Convertir €/MWh a €/kWh

    horas_baratas = df_hoy.nsmallest(N_HORAS_BARATAS, "price_eur_mwh").sort_values(
        "price_datetime_local"
    )

    st.subheader(f"Las {N_HORAS_BARATAS} horas más baratas de hoy")
    columnas = st.columns(N_HORAS_BARATAS)

    for columna, (_, fila) in zip(columnas, horas_baratas.iterrows()):
        with columna:
            hora = fila["price_datetime_local"].strftime("%H:%M")
            st.metric(label=hora, value=f"{fila['price_eur_kwh']:.3f} €/kWh")

    df_hoy["es_barata"] = df_hoy["price_datetime_local"].isin(
        horas_baratas["price_datetime_local"]
    )  # Cuadros con las horas mas baratas del dia

    fig = px.bar(
        df_hoy,
        x="price_datetime_local",
        y="price_eur_kwh",
        color="es_barata",
        color_discrete_map={True: "#2ecc71", False: "#4a4a4a"},
        labels={"price_datetime_local": "Hora", "price_eur_kwh": "€/kWh"},
    )

    fig.update_layout(
        showlegend=False, xaxis_fixedrange=True, yaxis_fixedrange=True
    )  # Bloquear zoom y arrastre en cada eje
    fig.update_traces(
        hovertemplate="Hora: %{x|%H:%M}<br>Precio: %{y:.4f} €/kWh<extra></extra>"
    )  # Modificar el tooltip de las barras para que muestre la hora y el precio en €/kWh

    st.plotly_chart(
        fig, width="stretch", config={"displayModeBar": False}
    )  # Oculta la barrra de herrramientas de plotly


with tab_historico:
    hoy = datetime.now(tz=MADRID_TZ).date()
    rango = st.date_input(
        "Rango de fechas",
        value=(hoy - timedelta(days=7), hoy),
        max_value=hoy,
    )

    if len(rango) != 2:
        st.stop()

    fecha_inicio, fecha_fin = rango

    # Consulta a la base de datos para obtener los precios PVPC históricos
    query_pvpc = text("""
        SELECT
            price_datetime AT TIME ZONE 'Europe/Madrid' AS price_datetime_local,
            price_eur_mwh
        FROM pvpc_prices
        WHERE (price_datetime AT TIME ZONE 'Europe/Madrid')::date BETWEEN :inicio AND :fin
        ORDER BY price_datetime
    """)
    df_pvpc_historico = pd.read_sql(
        query_pvpc, engine, params={"inicio": fecha_inicio, "fin": fecha_fin}
    )
    df_pvpc_historico["price_eur_kwh"] = df_pvpc_historico["price_eur_mwh"] / 1000

    # Consulta a la base de datos para obtener los precios SPOT históricos
    query_spot = text("""
        SELECT
            price_datetime AT TIME ZONE 'Europe/Madrid' AS price_datetime_local,
            price_eur_mwh
        FROM spot_market_prices
        WHERE (price_datetime AT TIME ZONE 'Europe/Madrid')::date BETWEEN :inicio AND :fin
        ORDER BY price_datetime
    """)
    df_spot_historico = pd.read_sql(
        query_spot, engine, params={"inicio": fecha_inicio, "fin": fecha_fin}
    )
    df_spot_historico["price_eur_kwh"] = df_spot_historico["price_eur_mwh"] / 1000

    df_pvpc_historico["serie"] = "PVPC"
    df_spot_historico["serie"] = "Mercado spot"

    df_historico = pd.concat(
        [
            df_pvpc_historico[["price_datetime_local", "price_eur_kwh", "serie"]],
            df_spot_historico[["price_datetime_local", "price_eur_kwh", "serie"]],
        ],
        ignore_index=True,
    )

    fig_historico = px.line(
        df_historico,
        x="price_datetime_local",
        y="price_eur_kwh",
        color="serie",
        color_discrete_map={"PVPC": "#2ecc71", "Mercado spot": "#e67e22"},
        labels={"price_datetime_local": "Fecha", "price_eur_kwh": "€/kWh", "serie": ""},
    )
    fig_historico.update_traces(
        hovertemplate="%{fullData.name}<br>%{x|%d/%m %H:%M}<br>%{y:.4f} €/kWh<extra></extra>"
    )

    fig_historico.update_layout(hovermode="x unified")

    st.plotly_chart(fig_historico, width="stretch")

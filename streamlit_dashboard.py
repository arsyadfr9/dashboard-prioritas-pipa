import streamlit as st
import geopandas as gpd
import pydeck as pdk
import pandas as pd
import os

st.set_page_config(layout="wide")
st.title("Dashboard Prediksi Kebocoran Pipa")

# Tab 1: Pemilih Model
st.header("1. Pemilihan Model Prediksi")

model = st.radio(
    "Pilih salah satu model prediksi kebocoran:",
    [
        "Poisson - Fisik",
        "Poisson - Tekanan & Debit",
        "GBT - Fisik",
        "GBT - Tekanan & Debit"
    ]
)

st.success(f"Model yang dipilih: {model}")

# Tab 2: Peta Interaktif
st.header("2. Peta Interaktif Jaringan Pipa")

# Mapping nama model ke path file geojson
model_files = {
    "Poisson - Fisik": "data/Poisson dari Fisik - Standar.geojson",
    "Poisson - Tekanan & Debit": "data/Poisson dari Tekanan dan Debit - Standar.geojson",
    "GBT - Fisik": "data/GBT dari Fisik - Standar.geojson",
    "GBT - Tekanan & Debit": "data/GBT dari Tekanan dan Debit - Standar.geojson"
}

@st.cache_data
def load_model_data(model_name):
    path = model_files.get(model_name)
    if path and os.path.exists(path):
        gdf = gpd.read_file(path)
        gdf = gdf.to_crs(epsg=4326)
        return gdf
    return None

model_gdf = load_model_data(model)

if model_gdf is not None and not model_gdf.empty:
    st.success(f"Memuat {len(model_gdf)} segmen pipa dari model '{model}'")

    # Tampilkan peta pydeck
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=model_gdf.geometry.centroid.y.mean(),
            longitude=model_gdf.geometry.centroid.x.mean(),
            zoom=13,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                "GeoJsonLayer",
                data=model_gdf.to_json(),
                pickable=True,
                stroked=True,
                filled=False,
                get_line_color="""
                    ['match', properties.kategori_risiko,
                    'Sangat Tinggi', [255, 0, 0],
                    'Tinggi', [255, 85, 0],
                    'Sedang', [255, 200, 0],
                    'Rendah', [0, 200, 0],
                    'Sangat Rendah', [0, 120, 0],
                    [100, 100, 100]]
                """,
                get_line_width=4,
            )
        ],
        tooltip={"text": "Pipa {pipa_index}\nRisiko: {kategori_risiko}\nSL: {SL}\nKebocoran: {jumlah_kebocoran}"}
    ))

    # Tab 3: Ringkasan Statistik
    st.header("3. Ringkasan Statistik Risiko dan Dampak")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Jumlah Pipa per Kategori Risiko")
        count_per_category = model_gdf["kategori_risiko"].value_counts().reset_index()
        count_per_category.columns = ["Kategori Risiko", "Jumlah Pipa"]
        st.dataframe(count_per_category)

    with col2:
        st.subheader("Rata-rata dan Total SL")
        sl_summary = model_gdf.groupby("kategori_risiko")["SL"].agg(["count", "mean", "sum"]).reset_index()
        st.dataframe(sl_summary)

    st.subheader("Distribusi Risiko")
    st.bar_chart(count_per_category.set_index("Kategori Risiko"))

else:
    st.warning("Data model tidak ditemukan atau kosong.")

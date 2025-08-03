import streamlit as st
import geopandas as gpd
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide")
st.title("Dashboard Prioritas Perbaikan Pipa (Garis)")

# Load file GeoJSON
@st.cache_data
def load_data():
    gdf = gpd.read_file("Prioritas Perbaikan.geojson")
    gdf = gdf.to_crs(epsg=4326)  # pastikan dalam lat-long
    return gdf

gdf = load_data()

# Filter prioritas
opsi = gdf["kategori_prioritas"].dropna().unique().tolist()
pilihan = st.sidebar.multiselect("Filter Prioritas", opsi, default=opsi)

filtered = gdf[gdf["kategori_prioritas"].isin(pilihan)]

# Peta pydeck
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=filtered.geometry.centroid.y.mean(),
        longitude=filtered.geometry.centroid.x.mean(),
        zoom=13,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            "GeoJsonLayer",
            data=filtered,
            pickable=True,
            stroked=True,
            filled=False,
            get_line_color="""
                ['match', properties.kategori_prioritas,
                'Tinggi', [255, 0, 0],
                'Sedang', [255, 165, 0],
                'Rendah', [0, 200, 0],
                [100, 100, 100]]
            """,
            get_line_width=4,
        )
    ],
    tooltip={"text": "Pipa {pipa_index}\nPrioritas: {kategori_prioritas}\nKerugian: Rp{kerugian_rp:.0f}\nSL: {SL}"}
))

# Tabel
st.subheader("Daftar Pipa Prioritas")
st.dataframe(filtered[["pipa_index", "kategori_prioritas", "skor_prioritas", "kerugian_rp", "SL", "jenis_pipa"]].sort_values(by="skor_prioritas", ascending=False))
